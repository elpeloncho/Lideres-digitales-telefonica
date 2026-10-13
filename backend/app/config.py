from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LUMA_", env_file=".env", extra="ignore")

    api_prefix: str = "/api/v1"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    store_dir: Path = REPOSITORY_ROOT / "data" / "store"
    seed_file: Path = REPOSITORY_ROOT / "data" / "synthetic" / "seed.json"

    # Ámbito geográfico de la demo (aproximado, ajustable).
    lat_min: float = 36.65
    lat_max: float = 36.80
    lon_min: float = -4.60
    lon_max: float = -4.30


settings = Settings()