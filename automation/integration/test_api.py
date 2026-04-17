"""
Integration tests for API endpoints
Run with: pytest automation/integration/ -v
"""
import pytest
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"
ADMIN_CREDS = {"username": "admin", "password": "admin"}


@pytest.fixture(scope="session")
def auth_token():
    """Get admin auth token"""
    resp = requests.post(f"{API_BASE}/api/auth/login", json=ADMIN_CREDS)
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Auth headers with bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """Admin can login"""
        resp = requests.post(f"{API_BASE}/api/auth/login", json=ADMIN_CREDS)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    def test_login_invalid_credentials(self):
        """Invalid credentials rejected"""
        resp = requests.post(
            f"{API_BASE}/api/auth/login",
            json={"username": "admin", "password": "wrong"}
        )
        assert resp.status_code == 401
    
    def test_get_current_user(self, auth_headers):
        """Can fetch current user"""
        resp = requests.get(f"{API_BASE}/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
    
    def test_get_current_user_unauthorized(self):
        """Unauthorized without token"""
        resp = requests.get(f"{API_BASE}/api/auth/me")
        assert resp.status_code == 401


class TestSuiteEndpoints:
    """Test suite CRUD operations"""
    
    def test_list_suites(self, auth_headers):
        """Can list test suites"""
        resp = requests.get(f"{API_BASE}/api/suites", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
    
    def test_create_suite(self, auth_headers):
        """Can create test suite"""
        suite_data = {
            "name": f"Test Suite {datetime.utcnow().timestamp()}",
            "description": "Integration test suite",
            "is_active": True
        }
        resp = requests.post(f"{API_BASE}/api/suites", json=suite_data, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == suite_data["name"]
    
    def test_create_duplicate_suite_fails(self, auth_headers):
        """Duplicate suite names rejected"""
        suite_data = {
            "name": f"Duplicate Suite {datetime.utcnow().timestamp()}",
            "description": "Test"
        }
        # First create succeeds
        resp1 = requests.post(f"{API_BASE}/api/suites", json=suite_data, headers=auth_headers)
        assert resp1.status_code == 201
        
        # Second create fails
        resp2 = requests.post(f"{API_BASE}/api/suites", json=suite_data, headers=auth_headers)
        assert resp2.status_code == 409
    
    def test_get_suite(self, auth_headers):
        """Can get suite by ID"""
        # Get first suite
        resp_list = requests.get(f"{API_BASE}/api/suites", headers=auth_headers)
        suites = resp_list.json()
        if suites:
            suite_id = suites[0]["id"]
            resp = requests.get(f"{API_BASE}/api/suites/{suite_id}", headers=auth_headers)
            assert resp.status_code == 200
    
    def test_update_suite(self, auth_headers):
        """Can update suite"""
        # Create suite
        suite_data = {
            "name": f"Suite to Update {datetime.utcnow().timestamp()}",
            "description": "Original",
            "is_active": True
        }
        resp_create = requests.post(f"{API_BASE}/api/suites", json=suite_data, headers=auth_headers)
        assert resp_create.status_code == 201, f"Create failed: {resp_create.text}"
        suite_id = resp_create.json()["id"]
        
        # Update suite (PATCH method)
        updated_data = {"description": "Updated description", "is_active": False}
        resp = requests.patch(f"{API_BASE}/api/suites/{suite_id}", json=updated_data, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated description"


class TestCaseEndpoints:
    """Test case CRUD operations"""
    
    @pytest.fixture
    def suite_id(self, auth_headers):
        """Create a test suite"""
        suite_data = {
            "name": f"Suite for Cases {datetime.utcnow().timestamp()}",
            "description": "Test"
        }
        resp = requests.post(f"{API_BASE}/api/suites", json=suite_data, headers=auth_headers)
        return resp.json()["id"]
    
    def test_create_test_case(self, suite_id, auth_headers):
        """Can create test case"""
        case_data = {
            "suite_id": suite_id,
            "title": "Test login functionality",
            "priority": "high",
            "status": "active",
            "tags": "smoke,auth"
        }
        resp = requests.post(f"{API_BASE}/api/cases", json=case_data, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == case_data["title"]
    
    def test_list_cases(self, suite_id, auth_headers):
        """Can list test cases"""
        resp = requests.get(f"{API_BASE}/api/cases", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestRunEndpoints:
    """Test run management"""
    
    def test_list_runs(self, auth_headers):
        """Can list test runs"""
        resp = requests.get(f"{API_BASE}/api/runs", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    
    def test_create_run(self, auth_headers):
        """Can create test run"""
        run_data = {
            "name": f"Test Run {datetime.utcnow().timestamp()}",
            "environment": "staging",
            "marker": "smoke"
        }
        resp = requests.post(f"{API_BASE}/api/runs", json=run_data, headers=auth_headers)
        assert resp.status_code == 201, f"Create failed with {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["name"] == run_data["name"]
        assert data["status"] == "pending"


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_get_summary(self, auth_headers):
        """Can get analytics summary"""
        resp = requests.get(f"{API_BASE}/api/analytics/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_suites" in data
        assert "total_cases" in data
        assert "total_runs" in data
    
    def test_get_top_failures(self, auth_headers):
        """Can get top failing tests"""
        resp = requests.get(f"{API_BASE}/api/analytics/top-failures", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
    
    def test_get_flaky_tests(self, auth_headers):
        """Can get flaky test list"""
        resp = requests.get(f"{API_BASE}/api/analytics/flaky", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestErrorHandling:
    """Test error responses"""
    
    def test_404_not_found(self, auth_headers):
        """Non-existent resource returns 404"""
        resp = requests.get(f"{API_BASE}/api/suites/99999", headers=auth_headers)
        assert resp.status_code == 404
    
    def test_401_unauthorized(self):
        """Missing token returns 401"""
        resp = requests.get(f"{API_BASE}/api/suites")
        assert resp.status_code == 401
    
    def test_400_bad_request(self, auth_headers):
        """Invalid data returns 400"""
        resp = requests.post(
            f"{API_BASE}/api/suites",
            json={"invalid": "data"},
            headers=auth_headers
        )
        assert resp.status_code in [400, 422]


class TestPerformance:
    """Test API performance"""
    
    def test_list_suites_under_200ms(self, auth_headers):
        """API should respond quickly"""
        import time
        start = time.time()
        resp = requests.get(f"{API_BASE}/api/suites", headers=auth_headers)
        duration = time.time() - start
        assert duration < 0.2, f"Request took {duration}s, expected < 0.2s"
    
    def test_concurrent_requests(self, auth_headers):
        """API should handle concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return requests.get(f"{API_BASE}/api/suites", headers=auth_headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in results)
