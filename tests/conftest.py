import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app import create_app


@pytest.fixture
def app() -> Litestar:
    """Create app with test database connection."""
    app_ = create_app()
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app: Litestar):
    with TestClient(app=app) as client:
        yield client
