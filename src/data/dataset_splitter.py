import logging
from typing import List, Dict, Any
from sklearn.model_selection import train_test_split
from collections import defaultdict

logger = logging.getLogger(__name__)


class DatasetSplitter:
    """Reusable logic for splitting a dataset while preventing data leakage from duplicates."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def split(
        self,
        samples: List[Dict[str, Any]],
        train_ratio: float,
        val_ratio: float,
        test_ratio: float,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Splits dataset samples into train, val, and test sets.

        Args:
            samples: List of dictionaries. Each must contain 'hash' and 'class_name'.
            train_ratio: Proportion of dataset for training.
            val_ratio: Proportion of dataset for validation.
            test_ratio: Proportion of dataset for testing.

        Returns:
            Dictionary with 'train', 'val', and 'test' keys mapping to lists of samples.
        """
        if not samples:
            raise ValueError("No samples provided for splitting.")

        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 1e-5:
            raise ValueError(f"Split ratios must sum to 1.0. Got {total_ratio}")

        # Group by hash to ensure exact content duplicates stay in the same split
        hash_groups = defaultdict(list)
        for sample in samples:
            hash_val = sample.get("hash")
            if not hash_val:
                raise ValueError(f"Sample missing hash: {sample}")
            hash_groups[hash_val].append(sample)

        # Create a representative list of groups for splitting
        unique_groups = []
        for hash_val, group in hash_groups.items():
            # Use the primary class of the first item in the group for stratification
            primary_class = group[0]["class_name"]
            unique_groups.append(
                {"hash": hash_val, "class_name": primary_class, "group": group}
            )

        labels = [g["class_name"] for g in unique_groups]
        val_test_ratio = val_ratio + test_ratio

        if val_test_ratio > 0:
            try:
                train_groups, val_test_groups, _, val_test_labels = train_test_split(
                    unique_groups,
                    labels,
                    test_size=val_test_ratio,
                    random_state=self.seed,
                    stratify=labels,
                )
            except ValueError as e:
                # Fallback if stratification fails due to too few samples per class
                logger.warning(f"Stratification failed during train/val_test split: {e}. Falling back to random split.")
                train_groups, val_test_groups = train_test_split(
                    unique_groups,
                    test_size=val_test_ratio,
                    random_state=self.seed,
                )
                val_test_labels = [g["class_name"] for g in val_test_groups]

            if test_ratio > 0:
                test_relative_ratio = test_ratio / val_test_ratio
                try:
                    val_groups, test_groups = train_test_split(
                        val_test_groups,
                        test_size=test_relative_ratio,
                        random_state=self.seed,
                        stratify=val_test_labels,
                    )
                except ValueError as e:
                    logger.warning(
                        f"Stratification failed during val/test split: {e}. "
                        "Falling back to random split."
                    )
                    val_groups, test_groups = train_test_split(
                        val_test_groups,
                        test_size=test_relative_ratio,
                        random_state=self.seed,
                    )
            else:
                val_groups = val_test_groups
                test_groups = []
        else:
            train_groups = unique_groups
            val_groups = []
            test_groups = []

        # Flatten back into samples
        splits = {
            "train": [s for g in train_groups for s in g["group"]],
            "val": [s for g in val_groups for s in g["group"]],
            "test": [s for g in test_groups for s in g["group"]],
        }

        return splits
