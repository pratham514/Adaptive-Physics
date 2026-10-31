from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    # Resolve the local settings file from this module, so starting Uvicorn from
    # the project root or the backend folder behaves the same way.
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    # Keep the value in backend/.env (or the process environment), never in code.
    nvidia_api_key: str = ""
    nvidia_model: str = "openai/gpt-oss-20b"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    database_url: str = "sqlite:///./adaptive_physics.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
