#!/usr/bin/env python3
"""
Script to create visual samples for human inspection of the dataset.
Generates a grid of random images for each class to quickly verify data quality,
defect visibility, and ensure there are no corrupted images.
"""

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

# Add project root to sys.path so we can run this script from anywhere
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.core.constants import DATA_DIR, REPORTS_DIR
from src.core.logging import configure_logging
from src.data.image_loader import load_image
from src.data.image_validator import SUPPORTED_EXTENSIONS

logger = configure_logging(name="visualize_dataset")


def create_image_grid(image_paths, grid_size=(3, 3), cell_size=(200, 200)) -> np.ndarray:
    """
    Creates a grid image from a list of image paths.
    Resizes images to fit the uniform cells perfectly.
    """
    rows, cols = grid_size
    cell_w, cell_h = cell_size

    # Initialize a black canvas
    grid_img = np.zeros((rows * cell_h, cols * cell_w, 3), dtype=np.uint8)

    for idx, path in enumerate(image_paths):
        if idx >= rows * cols:
            break

        r = idx // cols
        c = idx % cols

        try:
            # We explicitly load as RGB just for visualization so colors are correct
            img = load_image(path, as_rgb=True)

            # Resize image to fit the cell exactly
            img_resized = cv2.resize(img, (cell_w, cell_h))

            # The loader might return 2D grayscale if the source is purely grayscale
            # We must convert to 3 channels to place it in our RGB canvas
            if len(img_resized.shape) == 2:
                img_resized = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)

            # Place image in the grid
            grid_img[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w] = img_resized
        except Exception as e:
            logger.warning(f"Failed to process {path} for visualization: {e}")

    return grid_img


def visualize_dataset(raw_dir: Path, output_dir: Path, samples_per_class: int = 9) -> None:
    logger.info(f"Generating visual samples from: {raw_dir}")

    if not raw_dir.exists() or not raw_dir.is_dir():
        logger.error(f"Raw dataset directory does not exist: {raw_dir}")
        sys.exit(1)

    image_paths_by_class = defaultdict(list)
    for ext in SUPPORTED_EXTENSIONS:
        for path in raw_dir.rglob(f"*{ext}"):
            image_paths_by_class[path.parent.name].append(path)
        for path in raw_dir.rglob(f"*{ext.upper()}"):
            image_paths_by_class[path.parent.name].append(path)

    # Deduplicate within classes in case of case-insensitive filesystems
    for class_name in image_paths_by_class:
        image_paths_by_class[class_name] = list(set(image_paths_by_class[class_name]))

    if not image_paths_by_class:
        logger.warning(f"No valid image files found in {raw_dir}.")
        sys.exit(0)

    output_dir.mkdir(parents=True, exist_ok=True)

    for class_name, paths in image_paths_by_class.items():
        logger.info(f"Generating sample grid for class: '{class_name}' ({len(paths)} total images)")

        # Pick random samples safely
        num_samples = min(samples_per_class, len(paths))
        sampled_paths = random.sample(paths, num_samples)

        # Calculate grid size dynamically (e.g., 9 -> 3x3, 4 -> 2x2)
        grid_dim = int(np.ceil(np.sqrt(num_samples)))
        grid_size = (grid_dim, grid_dim)

        grid_img = create_image_grid(sampled_paths, grid_size=grid_size)

        # OpenCV expects BGR for imwrite, so we convert back from RGB
        grid_img_bgr = cv2.cvtColor(grid_img, cv2.COLOR_RGB2BGR)

        output_file = output_dir / f"{class_name}_sample_grid.jpg"
        cv2.imwrite(str(output_file), grid_img_bgr)

    logger.info("=" * 40)
    logger.info(f"Visualization complete. Sample grids saved to: {output_dir}")
    logger.info("Please inspect these grids manually to ensure data quality.")
    logger.info("=" * 40)


def main():
    parser = argparse.ArgumentParser(description="Create visual samples of the dataset.")
    default_raw_dir = project_root / DATA_DIR / "raw"
    default_output_dir = project_root / REPORTS_DIR / "dataset_validation" / "samples"

    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=default_raw_dir,
        help=f"Path to the raw dataset directory (default: {default_raw_dir})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Path to output the visual grids (default: {default_output_dir})",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=9,
        help="Number of images per class to sample (default: 9, yields a 3x3 grid)",
    )

    args = parser.parse_args()

    # Set a random seed for reproducible sampling (creates same grids every run)
    random.seed(42)

    visualize_dataset(args.raw_dir, args.output_dir, args.samples)


if __name__ == "__main__":
    main()
