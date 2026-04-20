from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./hcp_crm.db"
    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"
    groq_model_context: str = "llama-3.3-70b-versatile"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
