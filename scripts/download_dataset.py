import argparse
import sys
import urllib.request
import zipfile
from pathlib import Path
from urllib.error import URLError

# Ensure src can be imported
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.config import settings
from src.core.logging import configure_logging

logger = configure_logging(level=settings.LOG_LEVEL, name="download_dataset")

DEFAULT_EXTRACT_DIR = Path("data/raw/neu_dataset")
def check_dataset_exists(extract_dir: Path) -> bool:
    """Check if the dataset seems to be already present in the expected NEU-DET structure."""
    neu_det_dir = extract_dir / "NEU-DET"
    if not neu_det_dir.exists() or not neu_det_dir.is_dir():
        return False

    expected_dirs = [
        neu_det_dir / "train" / "images",
        neu_det_dir / "train" / "annotations",
        neu_det_dir / "validation" / "images",
        neu_det_dir / "validation" / "annotations",
    ]

    for d in expected_dirs:
        if not d.exists() or not d.is_dir():
            return False

    # Check for images in the image directories
    valid_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    images_found = False

    for img_dir in [
        neu_det_dir / "train" / "images",
        neu_det_dir / "validation" / "images",
    ]:
        for ext in valid_extensions:
            if any(img_dir.rglob(f"*{ext}")):
                images_found = True
                break

    if not images_found:
        return False

    return True


def download_from_url(url: str, dest_path: Path) -> bool:
    """Download a file from a URL."""
    logger.info(f"Downloading dataset from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        logger.info(f"Successfully downloaded to {dest_path}")
        return True
    except URLError as e:
        logger.error(f"Failed to download from {url}: {e}")
        return False


def extract_archive(archive_path: Path, extract_dir: Path) -> bool:
    """Extract a ZIP archive."""
    logger.info(f"Extracting {archive_path} to {extract_dir}...")
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info("Successfully extracted dataset.")
        return True
    except zipfile.BadZipFile:
        logger.error(f"The file at {archive_path} is not a valid ZIP archive.")
        return False
    except Exception as e:
        logger.error(f"Failed to extract {archive_path}: {e}")
        return False


def setup_dataset(
    source_url: str | None, local_archive: Path | None, extract_dir: Path
) -> None:
    """Main function to setup the dataset."""
    logger.info("Starting dataset setup...")

    # 1. Check if dataset already exists
    if check_dataset_exists(extract_dir):
        logger.info(f"Dataset already exists at {extract_dir}. Skipping download.")
        return

    extract_dir.mkdir(parents=True, exist_ok=True)

    temp_archive_path = None

    # 2. Locate / Fetch
    if local_archive:
        if not local_archive.exists():
            logger.error(f"Local archive not found: {local_archive}")
            sys.exit(1)
        archive_path = local_archive
    elif source_url:
        temp_archive_path = Path("data/raw/temp_neu_dataset.zip")
        temp_archive_path.parent.mkdir(parents=True, exist_ok=True)
        success = download_from_url(source_url, temp_archive_path)
        if not success:
            sys.exit(1)
        archive_path = temp_archive_path
    else:
        logger.error("No dataset source provided. Use --source or --local-archive.")
        sys.exit(1)

    # 3. Extract
    success = extract_archive(archive_path, extract_dir)
    if not success:
        if temp_archive_path and temp_archive_path.exists():
            temp_archive_path.unlink()
        sys.exit(1)

    # 4. Clean up if we downloaded a temporary file
    if temp_archive_path and temp_archive_path.exists():
        logger.info(f"Cleaning up temporary archive {temp_archive_path}...")
        temp_archive_path.unlink()

    # 5. Basic Verification
    if check_dataset_exists(extract_dir):
        logger.info("Dataset setup completed successfully.")
    else:
        logger.warning(
            "Dataset extracted, but no valid images or expected folders were found. "
            "Please verify the contents manually."
        )


def main():
    parser = argparse.ArgumentParser(description="Download and setup the NEU dataset.")
    parser.add_argument(
        "--source",
        type=str,
        help="URL to download the dataset archive.",
    )
    parser.add_argument(
        "--local-archive",
        type=Path,
        help="Path to an already downloaded local dataset archive (.zip).",
    )
    parser.add_argument(
        "--extract-dir",
        type=Path,
        default=DEFAULT_EXTRACT_DIR,
        help=f"Directory to extract the dataset (default: {DEFAULT_EXTRACT_DIR})",
    )

    args = parser.parse_args()

    setup_dataset(args.source, args.local_archive, args.extract_dir)


if __name__ == "__main__":
    main()
