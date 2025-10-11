import pytest
from flask import url_for
from src.models.user import User
from src.models.product import Product
from src.models.cart import Cart, CartItem

class TestAuthRoutes:
    """Test cases for authentication routes"""

    def test_login_route_get(self, test_client, init_database):
        """Test GET request to login route"""
        response = test_client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_route_post_success(self, test_client, init_database):
        """Test successful POST request to login route"""
        response = test_client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'test123',
            'remember': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Welcome' in response.data

    def test_login_route_post_invalid_credentials(self, test_client, init_database):
        """Test POST request to login route with invalid credentials"""
        response = test_client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'remember': False
        })

        assert response.status_code == 200
        assert b'Invalid email, password, or account is not active' in response.data

    def test_logout_route(self, logged_in_client):
        """Test logout route"""
        response = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data

    def test_register_route_get(self, test_client):
        """Test GET request to register route"""
        response = test_client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_route_post_success(self, test_client, init_database):
        """Test successful POST request to register route"""
        response = test_client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Registration successful! Please log in' in response.data

        # Verify user was created
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        assert user.username == 'newuser'

    def test_register_route_post_existing_email(self, test_client, init_database):
        """Test POST request to register route with existing email"""
        response = test_client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'test@example.com',  # Existing email
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Email already registered. Please log in' in response.data

    def test_register_route_post_password_mismatch(self, test_client):
        """Test POST request to register route with password mismatch"""
        response = test_client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'confirm_password': 'different123'
        })

        assert response.status_code == 200
        assert b'Field must be equal to password' in response.data

    def test_reset_password_request_route_get(self, test_client):
        """Test GET request to reset password request route"""
        response = test_client.get('/auth/reset_password_request')
        assert response.status_code == 200
        assert b'Reset Password' in response.data

    def test_reset_password_request_route_post(self, test_client, init_database):
        """Test POST request to reset password request route"""
        response = test_client.post('/auth/reset_password_request', data={
            'email': 'test@example.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'If an account with that email exists, a password reset link has been sent' in response.data

    def test_account_route(self, logged_in_client):
        """Test account route"""
        response = logged_in_client.get('/auth/account')
        assert response.status_code == 200
        assert b'Account Information' in response.data

    def test_update_account_route(self, logged_in_client, init_database):
        """Test updating account information"""
        response = logged_in_client.post('/auth/account/update', data={
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '1234567890',
            'shipping_address': '123 Updated St',
            'billing_address': '123 Updated St'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Your account has been updated!' in response.data

        # Verify changes were saved
        user = User.query.filter_by(email='test@example.com').first()
        assert user.username == 'updateduser'
        assert user.first_name == 'Updated'
        assert user.last_name == 'User'
        assert user.phone_number == '1234567890'

    def test_change_password_route(self, logged_in_client, init_database):
        """Test changing password"""
        response = logged_in_client.post('/auth/account/change_password', data={
            'current_password': 'test123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Your password has been changed!' in response.data

        # Verify password was changed
        user = User.query.filter_by(email='test@example.com').first()
        assert user.check_password('newpassword123') is True
        assert user.check_password('test123') is False

    def test_change_password_route_invalid_current(self, logged_in_client):
        """Test changing password with invalid current password"""
        response = logged_in_client.post('/auth/account/change_password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })

        assert response.status_code == 200
        assert b'Current password is incorrect' in response.data

    def test_change_password_route_mismatch(self, logged_in_client):
        """Test changing password with mismatched new passwords"""
        response = logged_in_client.post('/auth/account/change_password', data={
            'current_password': 'test123',
            'new_password': 'newpassword123',
            'confirm_password': 'different123'
        })

        assert response.status_code == 200
        assert b'New passwords do not match' in response.data

    def test_auth_routes_redirect_when_logged_in(self, logged_in_client):
        """Test that auth routes redirect when user is already logged in"""
        routes = [
            '/auth/login',
            '/auth/register',
            '/auth/reset_password_request'
        ]

        for route in routes:
            response = logged_in_client.get(route, follow_redirects=True)
            assert response.status_code == 200
            assert b'Welcome' in response.data