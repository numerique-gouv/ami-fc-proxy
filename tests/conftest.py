from pathlib import Path

import pytest
from litestar import Litestar
from litestar.stores.file import FileStore
from litestar.testing import TestClient

from app import create_app


@pytest.fixture()
def oidc_session_store(tmp_path: Path) -> FileStore:
    return FileStore(path=tmp_path / "oidc_sessions")


@pytest.fixture
def app(oidc_session_store: FileStore) -> Litestar:
    """Create app with test database connection."""
    app_ = create_app(stores={"oidc_sessions": oidc_session_store})
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app: Litestar):
    with TestClient(app=app) as client:
        yield client
