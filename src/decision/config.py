from pathlib import Path
from typing import Dict

import yaml
from pydantic import BaseModel, Field, ValidationError

from src.core.exceptions import DecisionConfigurationError
from src.decision.models import Decision, Severity


class GlobalRulesConfig(BaseModel):
    minimum_confidence: float = Field(ge=0.0, le=1.0)
    max_allowed_defects: int = Field(ge=0)


class ClassSpecificRuleConfig(BaseModel):
    minimum_confidence: float = Field(ge=0.0, le=1.0)
    severity_if_found: Severity


class SeverityEscalationConfig(BaseModel):
    multiple_defects_threshold: int = Field(ge=0)
    escalate_to: Severity


class DecisionPolicyConfig(BaseModel):
    no_defects: Decision
    low_severity: Decision
    medium_severity: Decision
    high_severity: Decision
    critical_severity: Decision


class DecisionRulesConfig(BaseModel):
    global_rules: GlobalRulesConfig
    class_specific_rules: Dict[str, ClassSpecificRuleConfig] = Field(
        default_factory=dict
    )
    severity_escalation: SeverityEscalationConfig
    decision_policy: DecisionPolicyConfig


def load_decision_config(yaml_path: str | Path) -> DecisionRulesConfig:
    """Loads and validates decision rules from a YAML file."""
    path = Path(yaml_path)
    if not path.exists():
        raise DecisionConfigurationError(
            f"Decision rules configuration file not found at: {path}"
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise DecisionConfigurationError(
                "Invalid YAML format: Root must be a dictionary."
            )

        return DecisionRulesConfig(**data)
    except yaml.YAMLError as e:
        raise DecisionConfigurationError(f"Failed to parse YAML configuration: {e}")
    except ValidationError as e:
        raise DecisionConfigurationError(f"Decision rules validation error: {e}")
