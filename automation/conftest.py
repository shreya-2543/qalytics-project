"""
conftest.py — Shared pytest fixtures for automation suite
"""
import pytest
import requests

from backend.config import BOOTSTRAP_ADMIN_PASSWORD, BOOTSTRAP_ADMIN_USERNAME


@pytest.fixture(scope="session")
def base_url():
    """FastAPI server base URL."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def admin_credentials():
    """Configured bootstrap credentials for authenticated API tests."""
    if not BOOTSTRAP_ADMIN_USERNAME or not BOOTSTRAP_ADMIN_PASSWORD:
        pytest.skip("Bootstrap admin credentials are not configured in the environment.")
    return {
        "username": BOOTSTRAP_ADMIN_USERNAME,
        "password": BOOTSTRAP_ADMIN_PASSWORD,
    }


@pytest.fixture(scope="session")
def auth_token(base_url, admin_credentials):
    """Obtain a valid JWT token for the configured admin user."""
    resp = requests.post(
        f"{base_url}/api/auth/login",
        json=admin_credentials,
        timeout=10,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
