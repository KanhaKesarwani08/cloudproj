from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession # Renamed to avoid conflict from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

from app.core.config import settings
from google.cloud.sql.connector import Connector, IPTypes

engine = None
SessionLocal = None

if settings.INSTANCE_CONNECTION_NAME and "cloudsql" in settings.SQLALCHEMY_DATABASE_URI:
    # Using Google Cloud SQL Connector
    print(f"Initializing database connection using Google Cloud SQL Connector for instance: {settings.INSTANCE_CONNECTION_NAME}")
    connector = Connector()

    def get_conn(): # type: ignore
        conn = connector.connect(
            settings.INSTANCE_CONNECTION_NAME, # "project:region:instance"
            "pg8000", # We are using psycopg2, but connector needs a driver name. pg8000 is a common one it expects for PG.
                      # Actual driver used by SQLAlchemy is psycopg2 as per SQLALCHEMY_DATABASE_URI
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            db=settings.DB_NAME,
            ip_type=IPTypes.PUBLIC # or IPTypes.PRIVATE, based on your setup
        )
        return conn

    engine = create_engine(
        # The URL format for Cloud SQL connector might just be "postgresql+psycopg2://",
        # as user/pass/db are handled by the connector. Or specify dummy host.
        # The connector.connect method handles the actual connection details.
        # So, the SQLALCHEMY_DATABASE_URI from settings might need adjustment if using connector explicitly this way.
        # A common pattern for connector + SQLAlchemy is to pass creator=get_conn to create_engine.
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@/{settings.DB_NAME}", # Host is managed by connector
        creator=get_conn,
        pool_size=5, # Adjust as needed
        max_overflow=10 # Adjust as needed
    )
    print("SQLAlchemy engine created with Cloud SQL Connector.")

elif settings.SQLALCHEMY_DATABASE_URI:
    print(f"Initializing database connection using direct URI: {settings.SQLALCHEMY_DATABASE_URI}")
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI, 
        pool_pre_ping=True, # Good practice for ensuring connections are live
        pool_size=5, # Adjust as needed
        max_overflow=10 # Adjust as needed
    )
    print("SQLAlchemy engine created with direct URI.")
else:
    print("Error: SQLALCHEMY_DATABASE_URI is not set. Database engine not created.")
    # Application might not be able to start or will fail on DB operations

if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    print("SessionLocal not created because engine initialization failed.")

Base = declarative_base()

# Dependency to get a DB session
def get_db() -> Generator[SQLAlchemySession, None, None]:
    if not SessionLocal:
        print("Error: SessionLocal is not initialized. Cannot create DB session.")
        # This would ideally raise an exception or be handled to prevent app from running improperly
        raise RuntimeError("Database session is not configured.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create database tables (call this from main.py or a script)
# def create_tables():
#     if engine:
#         Base.metadata.create_all(bind=engine)
#         print("Database tables created (if they didn't exist).")
#     else:
#         print("Engine not initialized, cannot create tables.") 