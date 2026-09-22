from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WAFI_",
        extra="ignore",
    )

    model_path: Path = Field(
        default=Path("models/wafi_model.joblib"),
    )


settings = Settings()
