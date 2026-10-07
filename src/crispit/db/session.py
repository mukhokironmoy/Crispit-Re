from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crispit.core.config import get_settings

settings = get_settings()

# creates SQLAlchemy’s connection interface to PostgreSQL.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
)

# creates a reusable factory for database sessions.
# will later give us one unit of work with the database.
SessionLocal = sessionmaker(        
    bind=engine,
    autoflush=False,
    autocommit=False,
)