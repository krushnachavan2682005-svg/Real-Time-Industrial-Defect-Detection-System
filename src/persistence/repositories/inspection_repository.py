from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.api.schemas import InspectionResponse
from src.persistence.schemas import InspectionHistoryItem


class InspectionRepository(ABC):
    @abstractmethod
    def save(self, inspection: InspectionResponse, timestamp: str) -> None:
        """Save a new inspection result."""
        pass

    @abstractmethod
    def get_by_id(self, inspection_id: str) -> Optional[InspectionHistoryItem]:
        """Retrieve an inspection by its ID."""
        pass

    @abstractmethod
    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[InspectionHistoryItem], int]:
        """List inspections with pagination and filtering. Returns (items, total_count)."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the database is accessible."""
        pass

    @abstractmethod
    def get_inspection_stats(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregate inspection stats."""
        pass

    @abstractmethod
    def get_defect_distribution(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get defect counts."""
        pass

    @abstractmethod
    def get_trends(
        self,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get trend data."""
        pass
