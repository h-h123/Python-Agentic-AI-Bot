import pytest
from flask import url_for
from src.models.order import Order, OrderItem, OrderStatus
from src.models.product import Product
from src.models.user import User

class TestOrderRoutes:
    """Test cases for order routes"""

    def test_order_list_route_unauthenticated(self, test_client, init_database):
        """Test order list route without authentication"""
        response = test_client.get('/orders/')
        assert response.status_code == 302  # Redirect to login

    def test_order_list_route_authenticated(self, logged_in_client, init_database, test_order):
        """Test order list route with authentication"""
        response = logged_in_client.get('/orders/')
        assert response.status_code == 200
        assert b'Your Orders' in response.data

    def test_order_detail_route_unauthenticated(self, test_client, init_database, test_order):
        """Test order detail route without authentication"""
        response = test_client.get(f'/orders/{test_order.id}')
        assert response.status_code == 302  # Redirect to login

    def test_order_detail_route_authenticated(self, logged_in_client, init_database, test_order):
        """Test order detail route with authentication"""
        response = logged_in_client.get(f'/orders/{test_order.id}')
        assert response.status_code == 200
        assert b'Order Details' in response.data

    def test_order_detail_route_unauthorized(self, logged_in_client, init_database):
        """Test order detail route for another user's order"""
        # Create an order for a different user
        admin = User.query.filter_by(email='admin@example.com').first()
        order = Order(
            user_id=admin.id,
            shipping_address='123 Admin St',
            total_amount=100.00,
            shipping_amount=5.00,
            tax_amount=8.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        response = logged_in_client.get(f'/orders/{order.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'You do not have permission to view this order' in response.data

    def test_cancel_order_route(self, logged_in_client, init_database, test_order):
        """Test cancel order route"""
        response = logged_in_client.post(f'/orders/{test_order.id}/cancel')
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Order cancelled successfully'
        assert response.json['new_status'] == OrderStatus.CANCELLED.value

        # Verify order was cancelled
        cancelled_order = Order.query.get(test_order.id)
        assert cancelled_order.status == OrderStatus.CANCELLED

    def test_cancel_order_route_invalid_order(self, logged_in_client, init_database):
        """Test cancel order route with invalid order ID"""
        response = logged_in_client.post('/orders/999999/cancel')
        assert response.status_code == 404
        assert response.json['success'] is False

    def test_cancel_order_route_unauthorized(self, logged_in_client, init_database):
        """Test cancel order route for another user's order"""
        # Create an order for a different user
        admin = User.query.filter_by(email='admin@example.com').first()
        order = Order(
            user_id=admin.id,
            shipping_address='123 Admin St',
            total_amount=100.00,
            shipping_amount=5.00,
            tax_amount=8.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        response = logged_in_client.post(f'/orders/{order.id}/cancel')
        assert response.status_code == 403
        assert response.json['success'] is False
        assert response.json['message'] == 'Permission denied'

    def test_admin_order_list_route_unauthorized(self, test_client, init_database):
        """Test admin order list route without admin privileges"""
        response = test_client.get('/orders/admin')
        assert response.status_code == 302  # Redirect to login

    def test_admin_order_list_route_authorized(self, admin_client, init_database):
        """Test admin order list route with admin privileges"""
        response = admin_client.get('/orders/admin')
        assert response.status_code == 200
        assert b'Order Management' in response.data

    def test_admin_order_list_route_with_status_filter(self, admin_client, init_database):
        """Test admin order list route with status filter"""
        response = admin_client.get('/orders/admin?status=pending')
        assert response.status_code == 200
        assert b'Order Management' in response.data

    def test_admin_update_order_status_route(self, admin_client, init_database, test_order):
        """Test admin update order status route"""
        response = admin_client.post(f'/orders/admin/{test_order.id}/update_status', data={
            'status': 'processing'
        })
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Order status updated successfully'
        assert response.json['new_status'] == 'processing'

        # Verify status was updated
        updated_order = Order.query.get(test_order.id)
        assert updated_order.status == OrderStatus.PROCESSING

    def test_admin_update_order_status_route_invalid_status(self, admin_client, init_database, test_order):
        """Test admin update order status route with invalid status"""
        response = admin_client.post(f'/orders/admin/{test_order.id}/update_status', data={
            'status': 'invalid_status'
        })
        assert response.status_code == 400
        assert response.json['success'] is False

    def test_admin_update_tracking_number_route(self, admin_client, init_database, test_order):
        """Test admin update tracking number route"""
        tracking_number = 'TRACK123456'
        response = admin_client.post(f'/orders/admin/{test_order.id}/update_tracking', data={
            'tracking_number': tracking_number
        })
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Tracking number updated successfully'
        assert response.json['tracking_number'] == tracking_number

        # Verify tracking number was updated
        updated_order = Order.query.get(test_order.id)
        assert updated_order.tracking_number == tracking_number

    def test_user_orders_route(self, logged_in_client, init_database, test_order):
        """Test user orders route"""
        user = User.query.filter_by(email='test@example.com').first()
        response = logged_in_client.get(f'/orders/user/{user.id}')
        assert response.status_code == 200
        assert b'Orders for' in response.data

    def test_user_orders_route_unauthorized(self, logged_in_client, init_database):
        """Test user orders route for another user"""
        admin = User.query.filter_by(email='admin@example.com').first()
        response = logged_in_client.get(f'/orders/user/{admin.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'You do not have permission to view these orders' in response.data

    def test_order_invoice_route(self, logged_in_client, init_database, test_order):
        """Test order invoice route"""
        response = logged_in_client.get(f'/orders/invoice/{test_order.id}')
        assert response.status_code == 200
        assert b'Invoice' in response.data

    def test_order_invoice_route_unauthorized(self, logged_in_client, init_database):
        """Test order invoice route for another user's order"""
        # Create an order for a different user
        admin = User.query.filter_by(email='admin@example.com').first()
        order = Order(
            user_id=admin.id,
            shipping_address='123 Admin St',
            total_amount=100.00,
            shipping_amount=5.00,
            tax_amount=8.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        response = logged_in_client.get(f'/orders/invoice/{order.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'You do not have permission to view this invoice' in response.data

    def test_admin_update_order_status_route_unauthorized(self, logged_in_client, init_database, test_order):
        """Test admin update order status route without admin privileges"""
        response = logged_in_client.post(f'/orders/admin/{test_order.id}/update_status', data={
            'status': 'processing'
        })
        assert response.status_code == 403
        assert response.json['success'] is False
        assert response.json['message'] == 'Permission denied'

    def test_admin_update_tracking_number_route_unauthorized(self, logged_in_client, init_database, test_order):
        """Test admin update tracking number route without admin privileges"""
        response = logged_in_client.post(f'/orders/admin/{test_order.id}/update_tracking', data={
            'tracking_number': 'TRACK123'
        })
        assert response.status_code == 403
        assert response.json['success'] is False
        assert response.json['message'] == 'Permission denied'