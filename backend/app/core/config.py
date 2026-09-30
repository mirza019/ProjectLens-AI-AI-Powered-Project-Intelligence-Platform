from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ProjectLens AI"
    database_url: str = "postgresql+psycopg://projectlens:projectlens@localhost:5432/projectlens"
    document_root: str = "output/documents"
    embedding_dimensions: int = 768
    embedding_model: str = "text-embedding-004"
    gemini_api_key: str = ""
    jwt_secret: str = "development-only-change-me"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    gemini_model: str = "gemini-2.5-flash"
    access_token_minutes: int = 480
    ai_rate_limit_per_minute: int = 20
    model_config = SettingsConfigDict(env_file=(".env", "backend/.env"), extra="ignore")

settings = Settings()
