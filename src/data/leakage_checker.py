import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class LeakageChecker:
    """Verifies that no data leakage exists between dataset splits."""

    @staticmethod
    def check_leakage(
        train_samples: List[Dict[str, Any]],
        val_samples: List[Dict[str, Any]],
        test_samples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Checks for overlap in content hashes between train, val, and test splits.

        Args:
            train_samples: List of training sample dictionaries containing 'hash'.
            val_samples: List of validation sample dictionaries containing 'hash'.
            test_samples: List of testing sample dictionaries containing 'hash'.

        Returns:
            Dictionary containing leakage report results.
        """

        def get_hashes(samples: List[Dict[str, Any]]) -> Set[str]:
            return {s["hash"] for s in samples if "hash" in s}

        train_hashes = get_hashes(train_samples)
        val_hashes = get_hashes(val_samples)
        test_hashes = get_hashes(test_samples)

        train_val_overlap = train_hashes.intersection(val_hashes)
        train_test_overlap = train_hashes.intersection(test_hashes)
        val_test_overlap = val_hashes.intersection(test_hashes)

        overlap_count = (
            len(train_val_overlap) + len(train_test_overlap) + len(val_test_overlap)
        )

        passed = overlap_count == 0

        if not passed:
            logger.error(f"Data leakage detected! Total overlaps: {overlap_count}")

        return {
            "passed": passed,
            "overlap_count": overlap_count,
            "overlaps": {
                "train_val": list(train_val_overlap),
                "train_test": list(train_test_overlap),
                "val_test": list(val_test_overlap),
            },
        }
