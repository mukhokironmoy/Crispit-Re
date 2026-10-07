import pytest
from sqlalchemy import text

from crispit.db.session import SessionLocal


@pytest.mark.integration
def test_database_connection() -> None:
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar_one() == 1

        db_name_result = db.execute(text("SELECT current_database()"))
        assert db_name_result.scalar_one() == "crispit_test"
    finally:
        db.close()