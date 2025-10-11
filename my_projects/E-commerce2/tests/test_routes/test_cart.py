import pytest
from flask import url_for
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.models.user import User

class TestCartRoutes:
    """Test cases for cart routes"""

    def test_view_cart_route_unauthenticated(self, test_client, init_database):
        """Test view cart route without authentication"""
        response = test_client.get('/cart/')
        assert response.status_code == 302  # Redirect to login

    def test_view_cart_route_authenticated(self, logged_in_client, init_database, test_cart):
        """Test view cart route with authentication"""
        response = logged_in_client.get('/cart/')
        assert response.status_code == 200
        assert b'Your Shopping Cart' in response.data

    def test_add_to_cart_route_unauthenticated(self, test_client, init_database):
        """Test add to cart route without authentication"""
        product = Product.query.first()
        response = test_client.post('/cart/add', data={
            'product_id': product.id,
            'quantity': 1
        })
        assert response.status_code == 302  # Redirect to login

    def test_add_to_cart_route_authenticated(self, logged_in_client, init_database):
        """Test add to cart route with authentication"""
        product = Product.query.first()
        response = logged_in_client.post('/cart/add', data={
            'product_id': product.id,
            'quantity': 1
        })
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == f'{product.name} added to cart'

    def test_add_to_cart_route_invalid_product(self, logged_in_client, init_database):
        """Test add to cart route with invalid product"""
        response = logged_in_client.post('/cart/add', data={
            'product_id': 999999,
            'quantity': 1
        })
        assert response.status_code == 404
        assert response.json['success'] is False
        assert response.json['message'] == 'Product not found'

    def test_add_to_cart_route_out_of_stock(self, logged_in_client, init_database):
        """Test add to cart route with out of stock product"""
        product = Product.query.first()
        product.stock_quantity = 0
        init_database.session.commit()

        response = logged_in_client.post('/cart/add', data={
            'product_id': product.id,
            'quantity': 1
        })
        assert response.status_code == 400
        assert response.json['success'] is False
        assert response.json['message'] == 'Product is out of stock'

    def test_add_to_cart_route_exceeds_stock(self, logged_in_client, init_database):
        """Test add to cart route with quantity exceeding stock"""
        product = Product.query.first()
        response = logged_in_client.post('/cart/add', data={
            'product_id': product.id,
            'quantity': product.stock_quantity + 1
        })
        assert response.status_code == 400
        assert response.json['success'] is False
        assert f'Only {product.stock_quantity} items available in stock' in response.json['message']

    def test_update_cart_item_route(self, logged_in_client, init_database, test_cart):
        """Test update cart item route"""
        cart_item = test_cart.items[0]
        new_quantity = 3

        response = logged_in_client.post('/cart/update', data={
            'item_id': cart_item.id,
            'quantity': new_quantity
        })
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Cart updated successfully'

        # Verify quantity was updated
        updated_item = CartItem.query.get(cart_item.id)
        assert updated_item.quantity == new_quantity

    def test_update_cart_item_route_invalid_item(self, logged_in_client, init_database):
        """Test update cart item route with invalid item"""
        response = logged_in_client.post('/cart/update', data={
            'item_id': 999999,
            'quantity': 1
        })
        assert response.status_code == 404
        assert response.json['success'] is False
        assert response.json['message'] == 'Item not found in your cart'

    def test_update_cart_item_route_exceeds_stock(self, logged_in_client, init_database, test_cart):
        """Test update cart item route with quantity exceeding stock"""
        cart_item = test_cart.items[0]
        product = Product.query.get(cart_item.product_id)

        response = logged_in_client.post('/cart/update', data={
            'item_id': cart_item.id,
            'quantity': product.stock_quantity + 1
        })
        assert response.status_code == 400
        assert response.json['success'] is False
        assert f'Only {product.stock_quantity} items available in stock' in response.json['message']

    def test_remove_cart_item_route(self, logged_in_client, init_database, test_cart):
        """Test remove cart item route"""
        cart_item = test_cart.items[0]
        product_name = cart_item.product.name

        response = logged_in_client.post(f'/cart/remove/{cart_item.id}')
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == f'{product_name} removed from cart'

        # Verify item was removed
        removed_item = CartItem.query.get(cart_item.id)
        assert removed_item is None

    def test_remove_cart_item_route_invalid_item(self, logged_in_client, init_database):
        """Test remove cart item route with invalid item"""
        response = logged_in_client.post('/cart/remove/999999')
        assert response.status_code == 404
        assert response.json['success'] is False
        assert response.json['message'] == 'Item not found in your cart'

    def test_clear_cart_route(self, logged_in_client, init_database, test_cart):
        """Test clear cart route"""
        response = logged_in_client.post('/cart/clear')
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Cart cleared successfully'

        # Verify cart is empty
        cart = Cart.query.filter_by(user_id=test_cart.user_id).first()
        assert len(cart.items) == 0

    def test_checkout_route_empty_cart(self, logged_in_client, init_database):
        """Test checkout route with empty cart"""
        response = logged_in_client.get('/cart/checkout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Your cart is empty' in response.data

    def test_checkout_route_with_items(self, logged_in_client, init_database, test_cart):
        """Test checkout route with items in cart"""
        response = logged_in_client.get('/cart/checkout')
        assert response.status_code == 200
        assert b'Checkout' in response.data
        assert b'Order Summary' in response.data

    def test_process_order_route_empty_cart(self, logged_in_client, init_database):
        """Test process order route with empty cart"""
        response = logged_in_client.post('/cart/process_order', follow_redirects=True)
        assert response.status_code == 200
        assert b'Your cart is empty' in response.data

    def test_process_order_route_success(self, logged_in_client, init_database, test_cart):
        """Test successful order processing"""
        # Update user shipping address
        user = User.query.filter_by(email='test@example.com').first()
        user.shipping_address = '123 Test St, Test City'
        init_database.session.commit()

        response = logged_in_client.post('/cart/process_order', data={
            'shipping_address': user.shipping_address,
            'billing_address': user.shipping_address,
            'payment_method': 'credit_card'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Your order has been placed successfully' in response.data

        # Verify cart is empty
        cart = Cart.query.filter_by(user_id=user.id).first()
        assert len(cart.items) == 0

    def test_get_cart_summary_route(self, logged_in_client, init_database, test_cart):
        """Test get cart summary route"""
        response = logged_in_client.get('/cart/get_cart_summary')
        assert response.status_code == 200
        assert response.json['item_count'] == test_cart.get_item_count()
        assert response.json['total'] == test_cart.calculate_total()