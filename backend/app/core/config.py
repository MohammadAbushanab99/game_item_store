from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://game:game@localhost:5432/game_store"
    jwt_secret_key: str = "change-me-please-use-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:4200"]


settings = Settings()
