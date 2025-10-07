import unittest
from decimal import Decimal
from app import create_app, db
from models.user import User, Address
from models.product import Product, Category
from models.cart import Cart, CartItem
from models.order import Order, OrderItem, OrderStatus, PaymentStatus
from services.cart_service import CartService
from services.order_service import OrderService
from services.product_service import ProductService
from services.user_service import UserService
from services.auth_service import AuthService

class TestServices(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Initialize services
        self.cart_service = CartService(self.app)
        self.order_service = OrderService(self.app)
        self.product_service = ProductService(self.app)
        self.user_service = UserService(self.app)
        self.auth_service = AuthService(self.app)

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
            price=Decimal('19.99'),
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

    def test_cart_service(self):
        # Test get_or_create_cart
        cart, _ = self.cart_service.get_or_create_cart(self.user.id)
        self.assertIsNotNone(cart)
        self.assertEqual(cart.user_id, self.user.id)

        # Test add_item_to_cart
        success, message = self.cart_service.add_item_to_cart(self.user.id, self.product.id, 1)
        self.assertTrue(success)
        self.assertIsNone(message)

        # Test update_cart_item
        success, message = self.cart_service.update_cart_item(self.user.id, self.product.id, 3)
        self.assertTrue(success)
        self.assertIsNone(message)

        # Test remove_item_from_cart
        success, message = self.cart_service.remove_item_from_cart(self.user.id, self.product.id)
        self.assertTrue(success)
        self.assertIsNone(message)

        # Test get_cart_total
        total, _ = self.cart_service.get_cart_total(self.user.id)
        self.assertEqual(total, Decimal('0.00'))

        # Test clear_cart
        success, message = self.cart_service.clear_cart(self.user.id)
        self.assertTrue(success)
        self.assertIsNone(message)

    def test_order_service(self):
        # Add item to cart first
        self.cart_service.add_item_to_cart(self.user.id, self.product.id, 2)

        # Test create_order
        order, message = self.order_service.create_order(
            self.user.id,
            self.address.id,
            self.address.id,
            'credit_card'
        )
        self.assertIsNotNone(order)
        self.assertIsNone(message)
        self.assertEqual(order.user_id, self.user.id)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(len(order.items), 1)

        # Test get_order_by_id
        retrieved_order, _ = self.order_service.get_order_by_id(order.id)
        self.assertIsNotNone(retrieved_order)
        self.assertEqual(retrieved_order.id, order.id)

        # Test update_order_status
        success, message = self.order_service.update_order_status(
            order.id,
            OrderStatus.PROCESSING,
            self.user.id
        )
        self.assertTrue(success)
        self.assertIsNone(message)

        # Test cancel_order
        success, message = self.order_service.cancel_order(order.id, self.user.id)
        self.assertTrue(success)
        self.assertIsNone(message)

    def test_product_service(self):
        # Test get_product_by_id
        product, _ = self.product_service.get_product_by_id(self.product.id)
        self.assertIsNotNone(product)
        self.assertEqual(product.id, self.product.id)

        # Test search_products
        products, _ = self.product_service.search_products(query='Test')
        self.assertGreater(len(products.items), 0)

        # Test get_featured_products
        featured, _ = self.product_service.get_featured_products()
        self.assertIsInstance(featured, list)

        # Test get_product_reviews
        reviews, _ = self.product_service.get_product_reviews(self.product.id)
        self.assertIsInstance(reviews, list)

        # Test get_product_rating
        rating, _ = self.product_service.get_product_rating(self.product.id)
        self.assertEqual(rating, 0)

    def test_user_service(self):
        # Test get_user_by_id
        user, _ = self.user_service.get_user_by_id(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user.id)

        # Test get_user_by_email
        user, _ = self.user_service.get_user_by_email('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

        # Test update_user_profile
        success, message = self.user_service.update_user_profile(
            self.user.id,
            first_name='Updated'
        )
        self.assertTrue(success)
        self.assertIsNone(message)
        self.assertEqual(self.user.first_name, 'Updated')

        # Test get_user_addresses
        addresses, _ = self.user_service.get_user_addresses(self.user.id)
        self.assertGreater(len(addresses), 0)

    def test_auth_service(self):
        # Test register_user
        user, message = self.auth_service.register_user(
            'newuser',
            'new@example.com',
            'newpassword123',
            'New',
            'User'
        )
        self.assertIsNotNone(user)
        self.assertIsNone(message)

        # Test authenticate_user
        user = self.auth_service.authenticate_user('new@example.com', 'newpassword123')
        self.assertIsNotNone(user)

        # Test password reset token generation and verification
        token = self.auth_service.generate_password_reset_token('new@example.com')
        self.assertIsNotNone(token)

        user = self.auth_service.verify_password_reset_token(token)
        self.assertIsNotNone(user)

        # Test reset_password
        success, message = self.auth_service.reset_password(user, 'newpassword456')
        self.assertTrue(success)
        self.assertIsNone(message)

        # Test change_password
        success, message = self.auth_service.change_password(
            self.user,
            'password123',
            'newpassword789'
        )
        self.assertTrue(success)
        self.assertIsNone(message)

    def test_service_integration(self):
        # Test cart to order workflow
        self.cart_service.add_item_to_cart(self.user.id, self.product.id, 2)
        cart_total, _ = self.cart_service.get_cart_total(self.user.id)
        self.assertEqual(cart_total, Decimal('39.98'))

        order, _ = self.order_service.create_order(
            self.user.id,
            self.address.id,
            self.address.id,
            'credit_card'
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.total_amount, Decimal('39.98'))

        cart_total, _ = self.cart_service.get_cart_total(self.user.id)
        self.assertEqual(cart_total, Decimal('0.00'))