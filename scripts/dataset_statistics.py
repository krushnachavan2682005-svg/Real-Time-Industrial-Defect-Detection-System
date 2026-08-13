#!/usr/bin/env python3
"""
Script to generate an objective statistical overview of the raw dataset.
Calculates deep statistical metrics (min/max/avg dimensions, sizes) and provides a terminal summary.
"""

import argparse
import json
import statistics
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

logger = configure_logging(name="dataset_statistics")


def generate_statistics(raw_dir: Path, output_file: Path) -> None:
    logger.info(f"Generating statistics for dataset at: {raw_dir}")

    if not raw_dir.exists() or not raw_dir.is_dir():
        logger.error(f"Raw dataset directory does not exist: {raw_dir}")
        sys.exit(1)

    image_paths = []
    for ext in SUPPORTED_EXTENSIONS:
        image_paths.extend(raw_dir.rglob(f"*{ext}"))
        image_paths.extend(raw_dir.rglob(f"*{ext.upper()}"))
    image_paths = list(set(image_paths))

    if not image_paths:
        logger.warning(f"No valid image files found in {raw_dir}.")
        sys.exit(0)

    # Accumulators
    widths = []
    heights = []
    channels_list = []
    file_sizes = []
    class_counts = defaultdict(int)
    formats = defaultdict(int)

    logger.info(f"Analyzing {len(image_paths)} images to generate statistics...")

    for path in image_paths:
        class_name = path.parent.name
        class_counts[class_name] += 1
        formats[path.suffix.lower()] += 1

        # We reuse the robust validator to parse actual dimensions and stats safely
        result = validate_image(path)
        if result.is_valid:
            widths.append(result.width)
            heights.append(result.height)
            channels_list.append(result.channels)
            file_sizes.append(result.file_size_bytes)

    if not widths:
        logger.error("No valid images could be parsed to generate statistics.")
        sys.exit(1)

    # Statistical Calculations
    stats = {
        "dataset_path": str(raw_dir.relative_to(project_root)),
        "total_images": len(image_paths),
        "valid_images": len(widths),
        "classes": dict(class_counts),
        "formats": dict(formats),
        "dimensions": {
            "width": {
                "min": min(widths),
                "max": max(widths),
                "avg": round(statistics.mean(widths), 2),
            },
            "height": {
                "min": min(heights),
                "max": max(heights),
                "avg": round(statistics.mean(heights), 2),
            },
            "channels": list(set(channels_list)),
        },
        "file_size": {
            "total_mb": round(sum(file_sizes) / (1024 * 1024), 2),
            "min_kb": round(min(file_sizes) / 1024, 2),
            "max_kb": round(max(file_sizes) / 1024, 2),
            "avg_kb": round(statistics.mean(file_sizes) / 1024, 2),
        },
    }

    # Console Summary
    logger.info("=" * 40)
    logger.info(" DATASET STATISTICS SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Total Images   : {stats['total_images']}")
    logger.info(f"Valid Images   : {stats['valid_images']}")
    logger.info(f"Total Size     : {stats['file_size']['total_mb']} MB")
    logger.info(f"Classes        : {len(stats['classes'])}")
    for c, count in stats['classes'].items():
        logger.info(f"  - {c}: {count}")
    logger.info(
        f"Avg Dimensions : {stats['dimensions']['width']['avg']}W x {stats['dimensions']['height']['avg']}H"
    )
    logger.info(f"Channels found : {stats['dimensions']['channels']}")
    logger.info("=" * 40)

    # Save to disk
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    logger.info(f"Detailed statistics saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate deep dataset statistics.")

    default_raw_dir = project_root / DATA_DIR / "raw"
    default_report_file = (
        project_root / REPORTS_DIR / "dataset_validation" / "statistics.json"
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
        help=f"Path to output the statistics JSON (default: {default_report_file})",
    )

    args = parser.parse_args()
    generate_statistics(args.raw_dir, args.output_file)


if __name__ == "__main__":
    main()
