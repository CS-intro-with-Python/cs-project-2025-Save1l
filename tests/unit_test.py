import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock

from server import app, db
from models import CartItem


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = 1
    user.is_authenticated = True
    return user


@pytest.fixture
def auth_client(client, mock_current_user):
    """Client with mocked authentication."""
    with patch('server.current_user', mock_current_user):
        with patch('flask_login.utils._get_user', return_value=mock_current_user):
            yield client


# =============================================================================
# Input Validation Tests for /api/cart/add
# =============================================================================

class TestAddToCartValidation:
    """Tests for input validation on add to cart endpoint."""

    def test_add_to_cart_missing_product_name(self, auth_client, mock_current_user):
        """Should return 400 when product_name is missing."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.post(
                    '/api/cart/add',
                    json={'product_price': 10.99},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Missing product_name or product_price' in response.data

    def test_add_to_cart_missing_product_price(self, auth_client, mock_current_user):
        """Should return 400 when product_price is missing."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.post(
                    '/api/cart/add',
                    json={'product_name': 'Test Product'},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Missing product_name or product_price' in response.data

    def test_add_to_cart_empty_body(self, auth_client, mock_current_user):
        """Should return 400 when request body is empty."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.post(
                    '/api/cart/add',
                    json={},
                    content_type='application/json'
                )
        assert response.status_code == 400

    def test_add_to_cart_invalid_price_string(self, auth_client, mock_current_user):
        """Should return 400 when product_price is invalid string."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.post(
                    '/api/cart/add',
                    json={'product_name': 'Test', 'product_price': 'not_a_number'},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Invalid product_price' in response.data

    def test_add_to_cart_invalid_price_none(self, auth_client, mock_current_user):
        """Should return 400 when product_price is None."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.post(
                    '/api/cart/add',
                    json={'product_name': 'Test', 'product_price': None},
                    content_type='application/json'
                )
        assert response.status_code == 400


# =============================================================================
# Input Validation Tests for /api/cart/update
# =============================================================================

class TestUpdateCartValidation:
    """Tests for input validation on update cart endpoint."""

    def test_update_cart_missing_quantity(self, auth_client, mock_current_user):
        """Should return 400 when quantity is missing."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.put(
                    '/api/cart/update/1',
                    json={},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Missing quantity' in response.data

    def test_update_cart_invalid_quantity_string(self, auth_client, mock_current_user):
        """Should return 400 when quantity is invalid string."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.put(
                    '/api/cart/update/1',
                    json={'quantity': 'invalid'},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Invalid quantity' in response.data

    def test_update_cart_quantity_less_than_one(self, auth_client, mock_current_user):
        """Should return 400 when quantity is less than 1."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.put(
                    '/api/cart/update/1',
                    json={'quantity': 0},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Quantity must be at least 1' in response.data

    def test_update_cart_negative_quantity(self, auth_client, mock_current_user):
        """Should return 400 when quantity is negative."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.put(
                    '/api/cart/update/1',
                    json={'quantity': -5},
                    content_type='application/json'
                )
        assert response.status_code == 400
        assert b'Quantity must be at least 1' in response.data


# =============================================================================
# Error Handling Tests - 404 Not Found
# =============================================================================

class TestErrorHandling404:
    """Tests for 404 error handling."""

    def test_update_nonexistent_item(self, auth_client, mock_current_user):
        """Should return 404 when updating non-existent item."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.put(
                    '/api/cart/update/99999',
                    json={'quantity': 5},
                    content_type='application/json'
                )
        assert response.status_code == 404
        assert b'Item not found' in response.data

    def test_remove_nonexistent_item(self, auth_client, mock_current_user):
        """Should return 404 when removing non-existent item."""
        with patch('server.current_user', mock_current_user):
            with patch('server.login_required', lambda f: f):
                response = auth_client.delete('/api/cart/remove/99999')
        assert response.status_code == 404
        assert b'Item not found' in response.data


# =============================================================================
# Tests for public routes (no auth required)
# =============================================================================

class TestPublicRoutes:
    """Tests for public routes that don't require authentication."""

    def test_index_returns_200(self, client):
        """Index page should return 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_home_returns_200(self, client):
        """Home page should return 200."""
        response = client.get('/home')
        assert response.status_code == 200

    def test_pricing_returns_200(self, client):
        """Pricing page should return 200."""
        response = client.get('/pricing')
        assert response.status_code == 200