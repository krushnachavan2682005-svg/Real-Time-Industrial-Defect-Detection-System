from typing import Any, Dict

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = "unsafe-default-secret"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BOOTSTRAP_ADMIN_ENABLED: bool = False
    BOOTSTRAP_ADMIN_USERNAME: str = "admin"
    BOOTSTRAP_ADMIN_PASSWORD: str = "admin"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


auth_settings = AuthSettings()


def load_security_config() -> Dict[str, Any]:
    try:
        with open("configs/security/security.yaml", "r") as f:
            config = yaml.safe_load(f)
            return config.get("security", {})
    except Exception:
        return {}


security_config = load_security_config()

# Validate that JWT_SECRET_KEY is not the default if we are in production
# However, we only have APP_ENV from core settings, so let's check it.
from src.core.config import settings

if (
    settings.APP_ENV == "production"
    and auth_settings.JWT_SECRET_KEY == "unsafe-default-secret"
    or auth_settings.JWT_SECRET_KEY == "change-this-in-production"
):
    raise RuntimeError("JWT_SECRET_KEY must be properly set in production environment!")
