from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2] # adjusting root path
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)

class Settings(BaseSettings):
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

    openrouter_api_key: SecretStr

    llm_model: str = "google/gemma-4-31b-it:free"
    llm_temperature: float = 0.0

settings = Settings()
