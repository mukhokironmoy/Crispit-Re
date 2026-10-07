import pytest
from fastapi.testclient import TestClient

from crispit.main import app

client = TestClient(app)


@pytest.mark.integration
def test_readiness_endpoint() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}