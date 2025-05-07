from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Budget Tracker FastAPI"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DB_USER: Optional[str] = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD", "password")
    DB_HOST: Optional[str] = os.getenv("DB_HOST", "localhost")
    DB_PORT: Optional[str] = os.getenv("DB_PORT", "5432")
    DB_NAME: Optional[str] = os.getenv("DB_NAME", "budget_tracker_db")
    
    # Constructed Database URL
    # For local development or standard connections:
    DATABASE_URL: Optional[str] = None
    # For Google Cloud SQL using the connector:
    INSTANCE_CONNECTION_NAME: Optional[str] = os.getenv("INSTANCE_CONNECTION_NAME") # e.g., "project:region:instance"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        if self.INSTANCE_CONNECTION_NAME: # Prioritize Cloud SQL Connector if configured
            # The google-cloud-sqlconnector will use this format with its own engine wrapper
            # The actual URL might be slightly different when using the connector directly,
            # often just needing db_user, db_pass, db_name, and instance_connection_name for the connector.
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
        elif self.DB_HOST and self.DB_PORT and self.DB_NAME and self.DB_USER and self.DB_PASSWORD:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db" # Fallback to SQLite for simplicity if no full PG config
            print("Warning: Full PostgreSQL connection details not found, falling back to SQLite for SQLALCHEMY_DATABASE_URI.")

    # Firebase Admin SDK credentials path (can be set via environment variable)
    # GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # JWT settings for custom authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env_var_and_be_very_strong")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) # Default to 30 minutes

    class Config:
        case_sensitive = True
        # env_file = ".env" # Uncomment to load from a .env file
        # env_file_encoding = 'utf-8'

settings = Settings()

# You might need to install pydantic-settings: pip install pydantic-settings 