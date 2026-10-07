from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str          # direct, used by Alembic
    database_url_pooled: str   # pooled, used by the app
    secret_key: str
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

