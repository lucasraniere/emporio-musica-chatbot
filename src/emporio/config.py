from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT_DIR = Path(__file__).resolve().parents[2] # adjusting root path
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)

class Settings(BaseSettings):
    timezone: str = "America/Campo_Grande"
    reference_date: date | None = None  # demo aid: pretend today is this date

    def now(self) -> datetime:
        now = datetime.now(ZoneInfo(self.timezone))
        if self.reference_date:
            d = self.reference_date
            now = now.replace(year=d.year, month=d.month, day=d.day)
        return now

    # inputs
    data_dir: Path = ROOT_DIR / "data"
    policies_filename: str = "politicas_da_loja.pdf"

    # outputs
    storage_dir: Path = ROOT_DIR / "storage"

    # policy index
    embedding_model: str = "intfloat/multilingual-e5-base"
    chroma_collection: str = "politicas"
    retriever_k: int = 6

    @property
    def policies_path(self) -> Path:
        return self.data_dir / self.policies_filename

    @property
    def sqlite_path(self) -> Path:
        return self.storage_dir / "emporio.db"

    @property
    def chroma_dir(self) -> Path:
        return self.storage_dir / "chroma"

    @property
    def checkpoint_path(self) -> Path:
        return self.storage_dir / "checkpoints.db"

    # llm config
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore", # ignoring LANGSMITH keys
    )

    # "openrouter" or "google" (Gemini API). Each provider needs its own key and
    # its own model name format, so set LLM_PROVIDER and LLM_MODEL together.
    llm_provider: Literal["openrouter", "google"] = "openrouter"
    openrouter_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None

    # llm_model: str = "google/gemma-4-31b-it:free"
    llm_model: str = "nvidia/nemotron-3.5-lightning:free"
    llm_temperature: float = 0.0

    @model_validator(mode="after")
    def _require_provider_key(self) -> "Settings":
        key = self.google_api_key if self.llm_provider == "google" else self.openrouter_api_key
        if key is None or not key.get_secret_value().strip():
            name = "GOOGLE_API_KEY" if self.llm_provider == "google" else "OPENROUTER_API_KEY"
            raise ValueError(f"LLM_PROVIDER={self.llm_provider} requires {name} in .env")
        return self

settings = Settings()
