"""
Database engine and session management.

Provides `SessionLocal` and an `init_db` helper to create tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from .models import Base
import mysql.connector
from mysql.connector import errorcode


engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create database tables based on SQLAlchemy models."""
    # Ensure the database exists (some environments may not create it)
    try:
        create_database_if_not_exists()
    except Exception:
        # If DB creation fails, still attempt to create tables (will raise)
        pass

    Base.metadata.create_all(bind=engine)


def create_database_if_not_exists() -> None:
    """Create the MySQL database if it does not already exist.

    Uses mysql-connector to connect to the server (no database) and runs
    a CREATE DATABASE IF NOT EXISTS statement using the config values.
    """
    config = {
        "user": settings.MYSQL_USER,
        "password": settings.MYSQL_PASSWORD,
        "host": settings.MYSQL_HOST,
        "port": settings.MYSQL_PORT,
    }

    try:
        conn = mysql.connector.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise
        else:
            raise
