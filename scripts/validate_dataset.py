#!/usr/bin/env python3
"""
Script to validate the complete raw dataset.
It aggregates results from `src.data.image_validator` and generates a JSON report.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to sys.path so we can run this script from anywhere
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.core.constants import DATA_DIR, REPORTS_DIR
from src.core.logging import configure_logging
from src.data.image_validator import SUPPORTED_EXTENSIONS, validate_image

logger = configure_logging(name="validate_dataset")


def validate_dataset(raw_dir: Path, output_file: Path) -> None:
    logger.info(f"Starting dataset validation on: {raw_dir}")

    if not raw_dir.exists() or not raw_dir.is_dir():
        logger.error(f"Raw dataset directory does not exist: {raw_dir}")
        sys.exit(1)

    # Statistics to collect
    stats = {
        "total_images_found": 0,
        "valid_images": 0,
        "invalid_images": 0,
        "classes": [],
        "image_count_per_class": defaultdict(int),
        "image_formats": defaultdict(int),
        "dimensions": defaultdict(int),
        "invalid_files": [],
    }

    # Discover images
    # We will look for any file with a supported extension recursively.
    # The immediate parent directory name is considered the class name.
    image_paths = []
    for ext in SUPPORTED_EXTENSIONS:
        # Check both lower and upper case extensions
        image_paths.extend(raw_dir.rglob(f"*{ext}"))
        image_paths.extend(raw_dir.rglob(f"*{ext.upper()}"))

    # Deduplicate in case of case-insensitive file system returning duplicates
    image_paths = list(set(image_paths))

    stats["total_images_found"] = len(image_paths)
    logger.info(f"Found {len(image_paths)} potential image files. Validating...")

    for i, path in enumerate(image_paths):
        # Progress logging
        if (i + 1) % 500 == 0:
            logger.info(f"Validated {i + 1}/{len(image_paths)} images...")

        class_name = path.parent.name
        if class_name not in stats["classes"]:
            stats["classes"].append(class_name)

        stats["image_count_per_class"][class_name] += 1
        stats["image_formats"][path.suffix.lower()] += 1

        result = validate_image(path)

        if result.is_valid:
            stats["valid_images"] += 1
            dim_key = f"{result.width}x{result.height}x{result.channels}"
            stats["dimensions"][dim_key] += 1
        else:
            stats["invalid_images"] += 1
            stats["invalid_files"].append(
                {"file": str(path.relative_to(project_root)), "reason": result.error_reason}
            )

    # Prepare final report dict
    report = {
        "dataset_directory": str(raw_dir.relative_to(project_root)),
        "summary": {
            "total_images": stats["total_images_found"],
            "valid_images": stats["valid_images"],
            "invalid_images": stats["invalid_images"],
            "total_classes": len(stats["classes"]),
        },
        "class_distribution": dict(stats["image_count_per_class"]),
        "formats_distribution": dict(stats["image_formats"]),
        "dimensions_distribution": dict(stats["dimensions"]),
        "invalid_files": stats["invalid_files"],
    }

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    logger.info(f"Validation complete. Report saved to: {output_file}")

    if stats["invalid_images"] > 0:
        logger.warning(
            f"Found {stats['invalid_images']} invalid images. Check the report for details."
        )
    else:
        logger.info("All images are valid!")


def main():
    parser = argparse.ArgumentParser(description="Validate the raw image dataset.")

    default_raw_dir = project_root / DATA_DIR / "raw"
    default_report_file = (
        project_root / REPORTS_DIR / "dataset_validation" / "validation_report.json"
    )

    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=default_raw_dir,
        help=f"Path to the raw dataset directory (default: {default_raw_dir})",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=default_report_file,
        help=f"Path to output the validation JSON report (default: {default_report_file})",
    )

    args = parser.parse_args()

    validate_dataset(args.raw_dir, args.output_file)


if __name__ == "__main__":
    main()
