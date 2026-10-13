from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_store
from app.main import app
from app.repositories.json_store import JsonStore


@pytest.fixture
def api_client(tmp_path: Path):
    store = JsonStore(
        store_dir=tmp_path / "store",
        seed_file=Path(__file__).parents[2] / "data" / "synthetic" / "seed.json",
    )
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
