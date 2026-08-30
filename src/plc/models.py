from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PLCCommandType(str, Enum):
    CONTINUE_CONVEYOR = "CONTINUE_CONVEYOR"
    FLAG_FOR_MANUAL_INSPECTION = "FLAG_FOR_MANUAL_INSPECTION"
    REJECT_PRODUCT = "REJECT_PRODUCT"


class PLCStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class PLCCommand(BaseModel):
    command_id: str
    command_type: PLCCommandType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    inspection_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PLCResponse(BaseModel):
    success: bool
    status: PLCStatus
    message: str
    command_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PLCCommandConfig(BaseModel):
    action: PLCCommandType


class PLCSimulationConfig(BaseModel):
    enabled: bool = True


class PLCConfig(BaseModel):
    enabled: bool = True
    mode: str = "simulation"
    simulation: PLCSimulationConfig = Field(default_factory=PLCSimulationConfig)
    commands: Dict[str, PLCCommandConfig]
