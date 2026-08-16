import json
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.annotation_converter import ConversionError, convert_to_yolo
from src.data.annotation_reader import AnnotationParseError, read_voc_annotation
from src.data.annotation_validator import load_classes, validate_annotation

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).resolve().parents[1]
    raw_data_dir = project_root / "data" / "raw" / "neu_dataset" / "NEU-DET"
    processed_dir = project_root / "data" / "processed" / "yolo"
    classes_path = project_root / "configs" / "data" / "classes.yaml"
    reports_dir = project_root / "reports" / "dataset_validation"

    if not raw_data_dir.exists():
        logger.error(f"Raw data directory not found: {raw_data_dir}")
        sys.exit(1)

    try:
        valid_classes = load_classes(classes_path)
        logger.info(f"Loaded {len(valid_classes)} classes from {classes_path}")
    except Exception as e:
        logger.error(f"Failed to load classes: {e}")
        sys.exit(1)

    splits = ["train", "validation"]

    stats = {
        "total_annotation_files": 0,
        "successfully_parsed": 0,
        "failed_to_parse": 0,
        "total_objects": 0,
        "valid_objects": 0,
        "invalid_objects": 0,
        "conversion_failures": 0,
        "class_distribution": {k: 0 for k in valid_classes.keys()},
        "images_without_annotations": 0
    }

    for split in splits:
        split_raw_annotations = raw_data_dir / split / "annotations"
        split_processed_labels = processed_dir / "labels" / split

        if not split_raw_annotations.exists():
            logger.warning(f"Annotations directory not found for split '{split}': {split_raw_annotations}")
            continue

        split_processed_labels.mkdir(parents=True, exist_ok=True)

        # We also need images directory created in processed,
        # normally we would copy or symlink images.
        # For this module, we'll create the directory structure at least.
        (processed_dir / "images" / split).mkdir(parents=True, exist_ok=True)

        xml_files = list(split_raw_annotations.glob("*.xml"))
        logger.info(f"Processing {len(xml_files)} files for split '{split}'...")

        for xml_file in xml_files:
            stats["total_annotation_files"] += 1

            try:
                annotation = read_voc_annotation(xml_file)
                stats["successfully_parsed"] += 1
            except AnnotationParseError as e:
                logger.warning(f"Parse error in {xml_file.name}: {e}")
                stats["failed_to_parse"] += 1
                continue

            if not annotation.objects:
                stats["images_without_annotations"] += 1
                continue

            stats["total_objects"] += len(annotation.objects)

            validation_errors = validate_annotation(annotation, valid_classes)
            if validation_errors:
                # We could filter out invalid objects or fail the whole file.
                # According to rules, don't silently ignore. We'll drop invalid objects and count them,
                # or skip the whole file. To be safe, we skip objects that are invalid.
                # Actually, our convert_to_yolo handles the whole ImageAnnotation.
                # Let's filter out invalid objects from the annotation before converting.
                valid_objs = []
                for idx, obj in enumerate(annotation.objects):
                    obj_errors = [err for err in validation_errors if err.startswith(f"Object {idx}:")]
                    if obj_errors:
                        stats["invalid_objects"] += 1
                        logger.warning(f"Invalid object in {xml_file.name}: {obj_errors}")
                    else:
                        valid_objs.append(obj)
                        stats["valid_objects"] += 1
                        stats["class_distribution"][obj.class_name] += 1

                annotation.objects = valid_objs
            else:
                stats["valid_objects"] += len(annotation.objects)
                for obj in annotation.objects:
                    stats["class_distribution"][obj.class_name] += 1

            if not annotation.objects:
                continue # No valid objects left to convert

            try:
                yolo_lines = convert_to_yolo(annotation, valid_classes)
            except ConversionError as e:
                logger.error(f"Conversion failed for {xml_file.name}: {e}")
                stats["conversion_failures"] += 1
                continue

            # Write to txt file
            txt_path = split_processed_labels / f"{xml_file.stem}.txt"
            with open(txt_path, "w") as f:
                f.write("\n".join(yolo_lines) + "\n")

    # Save report
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "annotation_report.json"
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=4)

    logger.info(f"Annotation preparation complete. Report saved to {report_path}")
    logger.info(f"Stats summary: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    main()
