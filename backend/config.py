import os

class Config:
    """Backend Configuration for PostgreSQL & Environment Settings"""
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # PostgreSQL Database Credentials
    PG_HOST = os.environ.get('PGHOST', 'localhost')
    PG_PORT = int(os.environ.get('PGPORT', 5432))
    PG_DB = os.environ.get('PGDATABASE', 'apex_finance')
    PG_USER = os.environ.get('PGUSER', 'postgres')
    PG_PASSWORD = os.environ.get('PGPASSWORD', 'postgres')

    # Connection URI
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )

    # Local SQLite Fallback File
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apex_finance.db')

    # Security & CORS
    CORS_ORIGINS = ["*"]
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-apex-key-2026')
