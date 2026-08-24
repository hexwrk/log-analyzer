"""
Environment-based configuration using pydantic-settings.
All secrets come from environment — never hardcode.
Build target: Month 2.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	app_name: str = "SecureFlow"
	api_key: str = ""
	database_url: str = "sqlite:///./secureflow.db"
	cors_origins: str = "http://localhost:3000"

	model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
