"""API tests run without a database or Azure: the DB and storage are replaced by fakes."""

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.test_sizing import CHART

KEY = "test-key"


class FakeDb:
    def __init__(self, chart):
        self.chart = chart

    def fetch_chart(self, product_id):
        return self.chart if product_id == "tee-1" else []


class FakeStorage:
    def get_base_dxf(self, product_id, size):
        return b"0\nSECTION\n0\nENDSEC\n0\nEOF\n" if size == "M" else None


def client(chart=CHART):
    settings = Settings(
        database_url="unused",
        api_key=KEY,
        storage_account_url=None,
        storage_container="dxf-files",
        alteration_limit_cm=3.0,
    )
    return TestClient(create_app(settings, db=FakeDb(chart), storage=FakeStorage()))


def test_health_needs_no_key():
    assert client().get("/healthz").json() == {"status": "ok"}


def test_best_fit_requires_key():
    r = client().post("/v1/best-fit", json={"product_id": "tee-1", "measurements": {"bust": 94}})
    assert r.status_code == 401


def test_best_fit_returns_decision():
    r = client().post(
        "/v1/best-fit",
        json={"product_id": "tee-1", "measurements": {"bust": 94.5, "waist": 75.5}},
        headers={"x-api-key": KEY},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["base_size"] == "M"
    assert body["decision"] == "standard"


def test_best_fit_unknown_product_is_404():
    r = client().post(
        "/v1/best-fit",
        json={"product_id": "missing", "measurements": {"bust": 94}},
        headers={"x-api-key": KEY},
    )
    assert r.status_code == 404


def test_base_dxf_returns_file():
    r = client().get("/v1/products/tee-1/base-dxf?size=M", headers={"x-api-key": KEY})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/dxf")


def test_base_dxf_missing_size_is_404():
    r = client().get("/v1/products/tee-1/base-dxf?size=XL", headers={"x-api-key": KEY})
    assert r.status_code == 404


def test_dxf_validate_rejects_garbage():
    r = client().post(
        "/v1/dxf/validate", json={"dxf_text": "not a dxf file"}, headers={"x-api-key": KEY}
    )
    assert r.json()["valid"] is False
