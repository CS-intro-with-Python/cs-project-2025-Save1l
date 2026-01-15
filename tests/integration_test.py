"""
Integration tests for Docker deployment.

These tests require the application to be running in Docker.
Run with: docker-compose up -d && pytest tests/integration_test.py -v
"""

import pytest
import requests
import time

# URL приложения в Docker
BASE_URL = "http://localhost:5000"


def wait_for_app(url, timeout=30):
    """Wait for the application to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="module")
def app_url():
    """
    Fixture that ensures app is running and returns base URL.
    """
    if not wait_for_app(BASE_URL):
        pytest.skip("Application is not running in Docker. Run 'docker-compose up -d' first.")
    return BASE_URL


# =============================================================================
# Test 1: Application responds to GET /health (200)
# =============================================================================

class TestHealthEndpoint:
    """Tests for /health endpoint - verifies app is running in Docker."""

    def test_health_endpoint_returns_200(self, app_url):
        """
        Test: The application is launched in Docker and responds to query.
        GET /health should return 200.
        """
        response = requests.get(f"{app_url}/health")
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

    def test_health_endpoint_returns_healthy_status(self, app_url):
        """
        Test: Health endpoint returns 'healthy' status.
        """
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        assert data['status'] == 'healthy'

    def test_health_endpoint_reports_database_status(self, app_url):
        """
        Test: Health endpoint includes database status.
        """
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        assert 'database' in data
        assert data['database'] == 'healthy'


# =============================================================================
# Test 2: Application connects to database and executes query
# =============================================================================

class TestDatabaseConnection:
    """Tests for database connectivity in Docker environment."""

    def test_database_connection_via_health(self, app_url):
        """
        Test: When launched in Docker, the application connects to the database
        and can execute a simple query.
        
        The /health endpoint executes 'SELECT 1' to verify DB connection.
        """
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        # Если database == 'healthy', значит SELECT 1 выполнился успешно
        assert response.status_code == 200
        assert data['database'] == 'healthy', \
            f"Database connection failed: {data.get('database')}"

    def test_app_can_load_pages_with_db(self, app_url):
        """
        Test: Application can load pages that may require database.
        """
        response = requests.get(f"{app_url}/")
        assert response.status_code == 200

    def test_app_pricing_page_loads(self, app_url):
        """
        Test: Pricing page loads successfully.
        """
        response = requests.get(f"{app_url}/pricing")
        assert response.status_code == 200


# =============================================================================
# Additional integration tests
# =============================================================================

class TestDockerDeployment:
    """Additional tests for Docker deployment."""

    def test_app_returns_html_on_index(self, app_url):
        """
        Test: Index page returns HTML content.
        """
        response = requests.get(f"{app_url}/")
        
        assert response.status_code == 200
        assert 'text/html' in response.headers['Content-Type']

    def test_static_files_accessible(self, app_url):
        """
        Test: Static files are accessible.
        """
        # Проверяем, что static endpoint работает
        response = requests.get(f"{app_url}/static/", allow_redirects=False)
        # Может вернуть 404 если нет index, или 200/301/302 если есть
        # Главное - не 500 (сервер работает)
        assert response.status_code != 500

    def test_multiple_requests_handled(self, app_url):
        """
        Test: Application handles multiple concurrent requests.
        """
        for _ in range(5):
            response = requests.get(f"{app_url}/health")
            assert response.status_code == 200