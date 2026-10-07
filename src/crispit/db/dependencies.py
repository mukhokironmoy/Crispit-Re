from collections.abc import Generator

from sqlalchemy.orm import Session

from crispit.db.session import SessionLocal


# This gives FastAPI a safe way to borrow a database session.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()