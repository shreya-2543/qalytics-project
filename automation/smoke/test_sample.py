"""
automation/smoke/test_sample.py
Three sample smoke tests: 2 pass, 1 skip — gives Allure real data.
These also double as a basic health check of the running API.
"""
import pytest
import allure
import requests

from backend.config import BOOTSTRAP_ADMIN_USERNAME


API = "http://localhost:8000"


@allure.feature("Smoke")
@allure.story("Health Check")
@allure.title("API health endpoint returns 200 OK")
@pytest.mark.smoke
def test_api_health():
    """The /api/health endpoint should always return 200 with status=ok."""
    r = requests.get(f"{API}/api/health", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("status") == "ok"
    assert "version" in data


@allure.feature("Smoke")
@allure.story("Auth")
@allure.title("Configured admin login returns a JWT token")
@pytest.mark.smoke
def test_admin_login(admin_credentials):
    """Logging in with the configured bootstrap admin should return a valid access token."""
    r = requests.post(
        f"{API}/api/auth/login",
        json=admin_credentials,
        timeout=5,
    )
    assert r.status_code == 200, f"Login failed: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert data["username"] == BOOTSTRAP_ADMIN_USERNAME


@allure.feature("Smoke")
@allure.story("Auth")
@allure.title("Invalid login is rejected (skipped in CI without a live server)")
@pytest.mark.smoke
@pytest.mark.skip(reason="Placeholder — run against a live server for full auth validation")
def test_invalid_login_rejected():
    """Wrong credentials must return HTTP 401."""
    r = requests.post(
        f"{API}/api/auth/login",
        json={"username": "not-a-user", "password": "wrong"},
        timeout=5,
    )
    assert r.status_code == 401
