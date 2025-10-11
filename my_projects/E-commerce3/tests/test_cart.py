import pytest
from flask import url_for
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from src.services.cart_service import CartService

class TestCartRoutes:
    def test_view_cart_route(self, logged_in_client, test_cart_with_items):
        response = logged_in_client.get('/cart/')
        assert response.status_code == 200
        assert b'Your Cart' in response.data

    def test_add_to_cart_route(self, logged_in_client, test_product):
        response = logged_in_client.post(f'/cart/add/{test_product.id}', data={
            'quantity': '1'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Product added to cart successfully!' in response.data

    def test_update_cart_item_route(self, logged_in_client, test_cart_with_items):
        cart_item = CartItem.query.first()
        response = logged_in_client.post(f'/cart/update/{cart_item.id}', data={
            'quantity': '3'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Cart updated successfully!' in response.data

    def test_remove_from_cart_route(self, logged_in_client, test_cart_with_items):
        cart_item = CartItem.query.first()
        response = logged_in_client.post(f'/cart/remove/{cart_item.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Item removed from cart successfully!' in response.data

    def test_clear_cart_route(self, logged_in_client, test_cart_with_items):
        response = logged_in_client.post('/cart/clear', follow_redirects=True)
        assert response.status_code == 200
        assert b'Your cart has been cleared' in response.data

class TestCartService:
    def test_get_active_cart(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = CartService.get_active_cart(user.id)
        assert cart is not None
        assert cart.user_id == user.id
        assert cart.is_active is True

    def test_add_item_to_cart(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        success, message = CartService.add_item_to_cart(user.id, product.id, 2)
        assert success is True
        assert message == "Item added to cart successfully"

        cart = Cart.query.filter_by(user_id=user.id, is_active=True).first()
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2

    def test_update_cart_item(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        # Add item first
        CartService.add_item_to_cart(user.id, product.id, 1)

        cart_item = CartItem.query.first()
        success, message = CartService.update_cart_item(user.id, cart_item.id, 3)
        assert success is True
        assert message == "Cart item updated successfully"

        updated_item = CartItem.query.get(cart_item.id)
        assert updated_item.quantity == 3

    def test_remove_cart_item(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        # Add item first
        CartService.add_item_to_cart(user.id, product.id, 1)

        cart_item = CartItem.query.first()
        success, message = CartService.remove_cart_item(user.id, cart_item.id)
        assert success is True
        assert message == "Item removed from cart successfully"

        assert CartItem.query.get(cart_item.id) is None

    def test_clear_cart(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        # Add item first
        CartService.add_item_to_cart(user.id, product.id, 1)

        success, message = CartService.clear_cart(user.id)
        assert success is True
        assert message == "Cart cleared successfully"

        cart = Cart.query.filter_by(user_id=user.id, is_active=True).first()
        assert len(cart.items) == 0
        assert cart.is_active is False

    def test_get_cart_summary(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        product = Product.query.first()

        # Add item first
        CartService.add_item_to_cart(user.id, product.id, 2)

        summary = CartService.get_cart_summary(user.id)
        assert summary['total_items'] == 2
        assert summary['total_price'] == float(product.price) * 2
        assert len(summary['items']) == 1

    def test_merge_carts(self, init_database):
        user1 = User.query.filter_by(email='test@example.com').first()
        user2 = User(
            username='testuser2',
            email='test2@example.com',
            password_hash='pbkdf2:sha256:150000$test$test'
        )
        user2.set_password('password123')
        user2.save()

        product = Product.query.first()

        # Add items to both carts
        CartService.add_item_to_cart(user1.id, product.id, 1)
        CartService.add_item_to_cart(user2.id, product.id, 2)

        # Merge user2's cart into user1's cart
        success, message = CartService.merge_carts(user2.id, user1.id)
        assert success is True

        # Check user1's cart
        cart1 = Cart.query.filter_by(user_id=user1.id, is_active=True).first()
        assert len(cart1.items) == 1
        assert cart1.items[0].quantity == 3

        # Check user2's cart is cleared
        cart2 = Cart.query.filter_by(user_id=user2.id, is_active=True).first()
        assert cart2 is None or len(cart2.items) == 0

class TestCartModel:
    def test_cart_creation(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()
        assert cart.id is not None
        assert cart.user_id == user.id
        assert cart.is_active is True

    def test_cart_total_price(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product1 = Product.query.first()
        product2 = Product(
            name='Second Product',
            description='Second test product',
            price=19.99,
            stock=50,
            category_id=product1.category_id
        )
        product2.save()

        cart_item1 = CartItem(cart_id=cart.id, product_id=product1.id, quantity=2)
        cart_item2 = CartItem(cart_id=cart.id, product_id=product2.id, quantity=1)
        cart_item1.save()
        cart_item2.save()

        expected_total = (product1.price * 2) + product2.price
        assert cart.total_price == expected_total

    def test_cart_add_item(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart.add_item(product.id, 3)

        assert len(cart.items) == 1
        assert cart.items[0].quantity == 3

    def test_cart_update_item_quantity(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart.add_item(product.id, 2)

        cart_item = CartItem.query.first()
        cart.update_item_quantity(product.id, 5)

        updated_item = CartItem.query.get(cart_item.id)
        assert updated_item.quantity == 5

    def test_cart_remove_item(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart.add_item(product.id, 1)

        cart_item = CartItem.query.first()
        cart.remove_item(product.id)

        assert CartItem.query.get(cart_item.id) is None

    def test_cart_clear(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart.add_item(product.id, 2)

        cart.clear()
        assert len(cart.items) == 0
        assert cart.is_active is False

    def test_cart_to_dict(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart.add_item(product.id, 1)

        cart_dict = cart.to_dict()
        assert cart_dict['id'] == cart.id
        assert cart_dict['user_id'] == user.id
        assert cart_dict['total_items'] == 1
        assert 'total_price' in cart_dict
        assert len(cart_dict['items']) == 1

class TestCartItemModel:
    def test_cart_item_creation(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=2)
        cart_item.save()

        assert cart_item.id is not None
        assert cart_item.cart_id == cart.id
        assert cart_item.product_id == product.id
        assert cart_item.quantity == 2

    def test_cart_item_subtotal(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=3)
        cart_item.save()

        expected_subtotal = product.price * 3
        assert cart_item.subtotal == expected_subtotal

    def test_cart_item_to_dict(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()
        cart = Cart(user_id=user.id)
        cart.save()

        product = Product.query.first()
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        cart_item.save()

        item_dict = cart_item.to_dict()
        assert item_dict['id'] == cart_item.id
        assert item_dict['cart_id'] == cart.id
        assert item_dict['product_id'] == product.id
        assert item_dict['quantity'] == 1
        assert 'subtotal' in item_dict
        assert 'product' in item_dict