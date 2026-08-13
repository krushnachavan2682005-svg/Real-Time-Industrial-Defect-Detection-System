#!/usr/bin/env python3
"""
Script to detect exact duplicate images in the raw dataset based on content hashing.
"""

import argparse
import hashlib
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
from src.data.image_validator import SUPPORTED_EXTENSIONS

logger = configure_logging(name="find_duplicates")


def compute_file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Computes the MD5 hash of a file's binary contents."""
    md5_hash = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            # Read in chunks to avoid memory bloat with large files
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error reading file {filepath} for hashing: {e}")
        return ""


def find_duplicates(raw_dir: Path, output_file: Path) -> None:
    logger.info(f"Starting exact duplicate detection in: {raw_dir}")

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

    logger.info(f"Hashing {len(image_paths)} images...")

    hash_map = defaultdict(list)
    for path in image_paths:
        file_hash = compute_file_hash(path)
        if file_hash:
            # Store relative paths for the report so it's portable across machines
            hash_map[file_hash].append(str(path.relative_to(project_root)))

    # Filter only groups that have more than 1 identical file
    duplicates = [paths for paths in hash_map.values() if len(paths) > 1]

    total_duplicate_files = sum(len(group) for group in duplicates)
    total_redundant_files = sum(len(group) - 1 for group in duplicates)

    logger.info("=" * 40)
    logger.info(" DUPLICATE DETECTION SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Total Images Scanned : {len(image_paths)}")
    logger.info(f"Duplicate Groups     : {len(duplicates)}")
    logger.info(f"Files Involved       : {total_duplicate_files}")
    logger.info(f"Redundant Files      : {total_redundant_files}")
    logger.info("=" * 40)

    report = {
        "dataset_directory": str(raw_dir.relative_to(project_root)),
        "summary": {
            "total_images_scanned": len(image_paths),
            "duplicate_groups_found": len(duplicates),
            "total_redundant_files": total_redundant_files,
        },
        "duplicate_groups": duplicates,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    logger.info(f"Duplicate report saved to: {output_file}")
    if total_redundant_files > 0:
        logger.warning(
            "NOTE: Duplicates were reported, but raw data was NOT modified."
        )


def main():
    parser = argparse.ArgumentParser(description="Find exact duplicate images.")

    default_raw_dir = project_root / DATA_DIR / "raw"
    default_report_file = (
        project_root / REPORTS_DIR / "dataset_validation" / "duplicates.json"
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
        help=f"Path to output the duplicates JSON (default: {default_report_file})",
    )

    args = parser.parse_args()
    find_duplicates(args.raw_dir, args.output_file)


if __name__ == "__main__":
    main()
