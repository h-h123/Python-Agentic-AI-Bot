import unittest
from flask import url_for
from app import create_app, db
from models.user import User
from models.product import Product, Category
from models.cart import Cart, CartItem
from models.order import Order, OrderItem, OrderStatus, PaymentStatus
from models.user import Address

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        self.user.set_password('password123')
        db.session.add(self.user)

        # Create test admin
        self.admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            is_admin=True
        )
        self.admin.set_password('admin123')
        db.session.add(self.admin)

        # Create test address
        self.address = Address(
            user_id=self.user.id,
            street='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country',
            is_default=True
        )
        db.session.add(self.address)

        # Create test category
        self.category = Category(
            name='Test Category',
            slug='test-category',
            description='Test category description',
            is_active=True
        )
        db.session.add(self.category)

        # Create test product
        self.product = Product(
            name='Test Product',
            description='Test product description',
            price=19.99,
            stock=100,
            sku='TEST123',
            category_id=self.category.id,
            is_active=True
        )
        db.session.add(self.product)

        # Create test cart
        self.cart = Cart(user_id=self.user.id)
        db.session.add(self.cart)

        # Create test cart item
        self.cart_item = CartItem(
            cart_id=self.cart.id,
            product_id=self.product.id,
            quantity=2
        )
        db.session.add(self.cart_item)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post(url_for('auth.login'), data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_auth_routes(self):
        # Test registration
        response = self.client.post(url_for('auth.register'), data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Test login
        response = self.login('new@example.com', 'newpassword123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

        # Test logout
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_product_routes(self):
        # Test product index
        response = self.client.get(url_for('products.index'))
        self.assertEqual(response.status_code, 200)

        # Test product detail
        response = self.client.get(url_for('products.product_detail', product_id=self.product.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

        # Test search
        response = self.client.get(url_for('products.search'), query_string={'q': 'Test'})
        self.assertEqual(response.status_code, 200)

        # Test category
        response = self.client.get(url_for('products.category', slug='test-category'))
        self.assertEqual(response.status_code, 200)

    def test_cart_routes(self):
        # Login first
        self.login('test@example.com', 'password123')

        # Test view cart
        response = self.client.get(url_for('carts.view_cart'))
        self.assertEqual(response.status_code, 200)

        # Test add to cart
        response = self.client.post(
            url_for('carts.add_to_cart', product_id=self.product.id),
            data={'quantity': 1},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'has been added to your cart', response.data)

        # Test update cart item
        response = self.client.post(
            url_for('carts.update_cart_item', item_id=self.cart_item.id),
            data={'quantity': 3},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cart updated successfully', response.data)

        # Test remove from cart
        response = self.client.get(
            url_for('carts.remove_from_cart', item_id=self.cart_item.id),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'has been removed from your cart', response.data)

        # Test clear cart
        response = self.client.get(url_for('carts.clear_cart'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your cart has been cleared', response.data)

    def test_order_routes(self):
        # Login first
        self.login('test@example.com', 'password123')

        # Test order list
        response = self.client.get(url_for('orders.list_orders'))
        self.assertEqual(response.status_code, 200)

        # Test checkout
        response = self.client.get(url_for('orders.checkout'))
        self.assertEqual(response.status_code, 200)

    def test_user_routes(self):
        # Login first
        self.login('test@example.com', 'password123')

        # Test profile
        response = self.client.get(url_for('users.profile'))
        self.assertEqual(response.status_code, 200)

        # Test edit profile
        response = self.client.get(url_for('users.edit_profile'))
        self.assertEqual(response.status_code, 200)

        # Test change password
        response = self.client.get(url_for('users.change_password'))
        self.assertEqual(response.status_code, 200)

        # Test addresses
        response = self.client.get(url_for('users.list_addresses'))
        self.assertEqual(response.status_code, 200)

        # Test reviews
        response = self.client.get(url_for('users.list_reviews'))
        self.assertEqual(response.status_code, 200)

    def test_admin_routes(self):
        # Login as admin
        self.login('admin@example.com', 'admin123')

        # Test admin-only routes would go here
        # For example, testing order status updates

    def test_error_handlers(self):
        # Test 404
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)

        # Test 500 (harder to test without causing actual server errors)

if __name__ == '__main__':
    unittest.main()