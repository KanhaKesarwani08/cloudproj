from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This should be called before initializing Settings
# It will load variables into the environment, which pydantic-settings can then read.
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Budget Tracker FastAPI"
    API_V1_STR: str = "/api/v1"

    # Database settings - will read from loaded env vars or use defaults
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "budget_tracker_db"
    
    # Cloud SQL Connector setting
    INSTANCE_CONNECTION_NAME: Optional[str] = None # e.g., "project:region:instance"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # JWT settings - will read from loaded env vars or use defaults
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env_var_and_be_very_strong"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def model_post_init(self, __context) -> None:
        # Construct the database URI after the settings are loaded
        if self.INSTANCE_CONNECTION_NAME: 
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
        else:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # Configure Pydantic BaseSettings behavior
        case_sensitive = True
        # Specifies the .env file to load settings from if python-dotenv is installed
        # Even though we call load_dotenv() explicitly, this tells pydantic where to look.
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Now `settings` instance will have values loaded from .env or defaults
print(f"Loaded settings: DB_HOST={settings.DB_HOST}, DB_NAME={settings.DB_NAME}") # Example print

# You might need to install pydantic-settings: pip install pydantic-settings 