import pytest
from fastapi.testclient import TestClient

from url_shortener.main import create_app


@pytest.fixture
def client():
    app = create_app(database_url="sqlite:///:memory:")
    with TestClient(app) as c:
        yield c
