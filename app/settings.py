from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Strategy = Literal["explicit", "cheapest_first", "credits_first", "local_first"]


class Settings(BaseSettings):
    """Every knob is an env var, so swapping a vendor never touches code."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    routing_strategy: Strategy = "local_first"
    providers_file: Path = Path("config/providers.yaml")

    # explicit choices
    llm_provider: str = "echo"
    embeddings_provider: str = "fastembed"
    vector_provider: str = "chroma"
    search_provider: str = "duckduckgo"
    storage_provider: str = "sqlite"
    obs_provider: str = "console"

    # local / free
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    chroma_path: Path = Path("./.data/chroma")
    sqlite_path: Path = Path("./.data/app.db")

    # keyed vendors
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    together_api_key: str = ""
    tavily_api_key: str = ""
    brave_api_key: str = ""
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    database_url: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    agent_max_steps: int = 4


@lru_cache
def settings() -> Settings:
    return Settings()
