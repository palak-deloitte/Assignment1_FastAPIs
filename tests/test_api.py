import pytest
from fastapi.testclient import TestClient

from app import config, services
from app.main import app

client = TestClient(app)
KEY = "test-key"


@pytest.fixture(autouse=True)
def set_service_key(monkeypatch):
    monkeypatch.setattr(config, "SERVICE_API_KEY", KEY)


def raises(exc):
    """Build a fake function that raises the given exception."""
    def _fake(*args, **kwargs):
        raise exc
    return _fake


# ---------- /weather ----------

def test_weather_success(monkeypatch):
    fake = {"city": "London", "temperature": 14.2,
            "condition": "overcast clouds", "humidity": 81}
    monkeypatch.setattr(services, "fetch_weather", lambda city: fake)
    r = client.get("/weather", params={"city": "London"})
    assert r.status_code == 200
    assert r.json() == fake


def test_weather_city_not_found(monkeypatch):
    monkeypatch.setattr(services, "fetch_weather", raises(services.CityNotFound("x")))
    r = client.get("/weather", params={"city": "Fakecityxyz"})
    assert r.status_code == 404


def test_weather_upstream_failure(monkeypatch):
    monkeypatch.setattr(services, "fetch_weather", raises(services.UpstreamError("down")))
    r = client.get("/weather", params={"city": "London"})
    assert r.status_code == 502


def test_weather_missing_city():
    r = client.get("/weather")
    assert r.status_code == 422


# ---------- /joke ----------

def test_joke_success(monkeypatch):
    fake = {"joke": "A funny joke", "category": "Misc"}
    monkeypatch.setattr(services, "fetch_joke", lambda: fake)
    r = client.get("/joke")
    assert r.status_code == 200
    assert r.json() == fake


def test_joke_upstream_failure(monkeypatch):
    monkeypatch.setattr(services, "fetch_joke", raises(services.UpstreamError("down")))
    r = client.get("/joke")
    assert r.status_code == 502


# ---------- /summary ----------

def test_summary_missing_key():
    r = client.post("/summary", json={"text": "hello"})
    assert r.status_code == 401


def test_summary_wrong_key():
    r = client.post("/summary", json={"text": "hello"}, headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_summary_auth_checked_before_validation():
    r = client.post("/summary", json={"text": ""})
    assert r.status_code == 401


def test_summary_empty_text():
    r = client.post("/summary", json={"text": "   "}, headers={"X-API-Key": KEY})
    assert r.status_code == 400


def test_summary_too_long():
    text = "a" * (config.MAX_TEXT_LENGTH + 1)
    r = client.post("/summary", json={"text": text}, headers={"X-API-Key": KEY})
    assert r.status_code == 400


def test_summary_success(monkeypatch):
    monkeypatch.setattr(services, "summarize_text", lambda text: "A short summary.")
    r = client.post("/summary", json={"text": "Some long text."},
                    headers={"X-API-Key": KEY})
    assert r.status_code == 200
    assert r.json() == {"summary": "A short summary."}


def test_summary_llm_failure(monkeypatch):
    monkeypatch.setattr(services, "summarize_text", raises(services.UpstreamError("down")))
    r = client.post("/summary", json={"text": "Some text."}, headers={"X-API-Key": KEY})
    assert r.status_code == 502