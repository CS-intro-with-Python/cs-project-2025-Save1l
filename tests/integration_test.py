import pytest
import requests
import time

BASE_URL = "http://localhost:5000"


def wait_for_app(url, timeout=30):
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
    if not wait_for_app(BASE_URL):
        pytest.skip("Application is not running in Docker. Run 'docker-compose up -d' first.")
    return BASE_URL


class TestHealthEndpoint:

    def test_health_endpoint_returns_200(self, app_url):
        response = requests.get(f"{app_url}/health")
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

    def test_health_endpoint_returns_healthy_status(self, app_url):
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        assert data['status'] == 'healthy'

    def test_health_endpoint_reports_database_status(self, app_url):
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        assert 'database' in data
        assert data['database'] == 'healthy'


class TestDatabaseConnection:

    def test_database_connection_via_health(self, app_url):
        response = requests.get(f"{app_url}/health")
        data = response.json()
        
        assert response.status_code == 200
        assert data['database'] == 'healthy', \
            f"Database connection failed: {data.get('database')}"

    def test_app_can_load_pages_with_db(self, app_url):
        response = requests.get(f"{app_url}/")
        assert response.status_code == 200

    def test_app_pricing_page_loads(self, app_url):
        response = requests.get(f"{app_url}/pricing")
        assert response.status_code == 200


class TestDockerDeployment:

    def test_app_returns_html_on_index(self, app_url):
        response = requests.get(f"{app_url}/")
        
        assert response.status_code == 200
        assert 'text/html' in response.headers['Content-Type']

    def test_static_files_accessible(self, app_url):
        response = requests.get(f"{app_url}/static/", allow_redirects=False)
        assert response.status_code != 500

    def test_multiple_requests_handled(self, app_url):
        for _ in range(5):
            response = requests.get(f"{app_url}/health")
            assert response.status_code == 200