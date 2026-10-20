"""Settings come from environment variables. Secrets are supplied by Azure Container Apps
(Key Vault references), never stored in the repository."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    api_key: str
    storage_account_url: str | None
    storage_container: str
    alteration_limit_cm: float


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ["DATABASE_URL"],
        api_key=os.environ["SERVICE_API_KEY"],
        storage_account_url=os.environ.get("STORAGE_ACCOUNT_URL"),
        storage_container=os.environ.get("STORAGE_CONTAINER", "dxf-files"),
        alteration_limit_cm=float(os.environ.get("ALTERATION_LIMIT_CM", "3")),
    )
