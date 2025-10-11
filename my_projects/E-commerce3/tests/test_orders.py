import pytest
from flask import url_for
from src.models.order import Order, OrderItem, OrderStatus
from src.models.user import User
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.services.order_service import OrderService

class TestOrderRoutes:
    def test_checkout_route_empty_cart(self, logged_in_client):
        response = logged_in_client.get('/orders/checkout')
        assert response.status_code == 302  # Redirect
        assert response.location.endswith('/cart')

    def test_checkout_route_with_items(self, logged_in_client, test_cart_with_items):
        response = logged_in_client.get('/orders/checkout')
        assert response.status_code == 200
        assert b'Checkout' in response.data

    def test_order_list_route(self, logged_in_client, test_order):
        response = logged_in_client.get('/orders/')
        assert response.status_code == 200
        assert b'My Orders' in response.data

    def test_order_detail_route(self, logged_in_client, test_order):
        response = logged_in_client.get(f'/orders/{test_order.id}')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data

    def test_cancel_order_route(self, logged_in_client, test_order):
        response = logged_in_client.post(f'/orders/{test_order.id}/cancel', follow_redirects=True)
        assert response.status_code == 200
        assert b'Your order has been cancelled successfully' in response.data

    def test_admin_order_list_route(self, admin_client, test_order):
        response = admin_client.get('/orders/admin')
        assert response.status_code == 200
        assert b'All Orders' in response.data

    def test_admin_order_detail_route(self, admin_client, test_order):
        response = admin_client.get(f'/orders/admin/{test_order.id}')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data

    def test_update_order_status_route(self, admin_client, test_order):
        response = admin_client.post(f'/orders/admin/{test_order.id}/update_status',
                                     data={'status': 'Processing'},
                                     follow_redirects=True)
        assert response.status_code == 200
        assert b'Order status updated successfully' in response.data

class TestOrderService:
    def test_generate_order_number(self):
        order_number = OrderService.generate_order_number()
        assert order_number.startswith('ORD-')
        assert len(order_number) == 23  # ORD-YYYYMMDDHHMMSS-XXXX

    def test_create_order(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        # Add product to cart first
        cart = Cart(user_id=user.id)
        cart.save()
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        cart_item.save()

        order, error = OrderService.create_order(
            user_id=user.id,
            shipping_address='123 Test St',
            payment_method='credit_card'
        )

        assert order is not None
        assert error is None
        assert order.user_id == user.id
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 1

    def test_get_order_by_id(self, init_database, test_order):
        order = OrderService.get_order_by_id(test_order.id)
        assert order is not None
        assert order.id == test_order.id

    def test_get_orders_by_user(self, init_database, test_order):
        user = User.query.filter_by(email='test@example.com').first()
        orders = OrderService.get_orders_by_user(user.id)
        assert orders.total == 1
        assert orders.items[0].id == test_order.id

    def test_get_all_orders(self, init_database, test_order):
        orders = OrderService.get_all_orders()
        assert orders.total == 1
        assert orders.items[0].id == test_order.id

    def test_update_order_status(self, init_database, test_order):
        success, error = OrderService.update_order_status(
            test_order.id,
            OrderStatus.PROCESSING
        )
        assert success is True
        assert error is None

        updated_order = Order.query.get(test_order.id)
        assert updated_order.status == OrderStatus.PROCESSING

    def test_cancel_order(self, init_database, test_order):
        success, error = OrderService.cancel_order(test_order.id, test_order.user_id)
        assert success is True
        assert error is None

        cancelled_order = Order.query.get(test_order.id)
        assert cancelled_order.status == OrderStatus.CANCELLED

    def test_get_order_summary(self, init_database, test_order):
        summary = OrderService.get_order_summary(test_order.id)
        assert summary is not None
        assert summary['order_number'] == test_order.order_number
        assert summary['items_count'] == len(test_order.items)

    def test_process_payment(self, init_database, test_order):
        success, error = OrderService.process_payment(test_order.id, {})
        assert success is True
        assert error is None

        updated_order = Order.query.get(test_order.id)
        assert updated_order.payment_status == 'Completed'

    def test_update_shipping_info(self, init_database, test_order):
        success, error = OrderService.update_shipping_info(
            test_order.id,
            'TRACK12345',
            'express'
        )
        assert success is True
        assert error is None

        updated_order = Order.query.get(test_order.id)
        assert updated_order.tracking_number == 'TRACK12345'
        assert updated_order.shipping_method == 'express'

class TestOrderModel:
    def test_order_creation(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        order = Order(
            user_id=user.id,
            order_number='TEST12345',
            shipping_address='123 Test St',
            payment_method='credit_card',
            total_amount=9.99
        )
        order.save()

        assert order.id is not None
        assert order.user_id == user.id
        assert order.status == OrderStatus.PENDING

    def test_order_status_update(self, init_database, test_order):
        test_order.update_status(OrderStatus.PROCESSING)
        assert test_order.status == OrderStatus.PROCESSING

    def test_order_add_item(self, init_database, test_order):
        product = Product.query.first()
        test_order.add_item(product.id, 2, product.price)

        assert len(test_order.items) == 2  # Original + new
        assert test_order.items[1].product_id == product.id
        assert test_order.items[1].quantity == 2

    def test_order_calculate_totals(self, init_database, test_order):
        original_total = test_order.total_amount
        test_order.calculate_totals()
        assert test_order.total_amount == test_order.grand_total

    def test_order_cancel(self, init_database, test_order):
        product = test_order.items[0].product
        original_stock = product.stock

        test_order.cancel()
        assert test_order.status == OrderStatus.CANCELLED
        assert product.stock == original_stock + test_order.items[0].quantity

    def test_order_to_dict(self, init_database, test_order):
        order_dict = test_order.to_dict()
        assert order_dict['id'] == test_order.id
        assert order_dict['order_number'] == test_order.order_number
        assert order_dict['status'] == test_order.status.value
        assert 'items' in order_dict
        assert len(order_dict['items']) == len(test_order.items)

class TestOrderItemModel:
    def test_order_item_creation(self, init_database, test_order):
        product = Product.query.first()
        order_item = OrderItem(
            order_id=test_order.id,
            product_id=product.id,
            quantity=2,
            price=product.price
        )
        order_item.save()

        assert order_item.id is not None
        assert order_item.order_id == test_order.id
        assert order_item.product_id == product.id
        assert order_item.quantity == 2

    def test_order_item_subtotal(self, init_database, test_order):
        order_item = test_order.items[0]
        expected_subtotal = order_item.quantity * order_item.price
        assert order_item.subtotal == expected_subtotal

    def test_order_item_to_dict(self, init_database, test_order):
        order_item = test_order.items[0]
        item_dict = order_item.to_dict()

        assert item_dict['id'] == order_item.id
        assert item_dict['order_id'] == order_item.order_id
        assert item_dict['product_id'] == order_item.product_id
        assert item_dict['quantity'] == order_item.quantity
        assert 'subtotal' in item_dict
        assert 'product_name' in item_dict