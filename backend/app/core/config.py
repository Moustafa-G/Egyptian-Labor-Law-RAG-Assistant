from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    vector_store_dir: str = "data/vector_store"
    collection_name: str = "labor_law"

    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama3.2:3b"

    top_k: int = 3

    cors_origins: str = "http://localhost:8501"

    @property
    def vector_store_path(self) -> Path:
        return Path(self.vector_store_dir)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
