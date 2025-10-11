import pytest
from decimal import Decimal
from src.models.user import User
from src.models.product import Product, Category
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem, OrderStatus
from src.services.product_service import ProductService
from src.services.cart_service import CartService
from src.services.order_service import OrderService
from src.services.auth_service import AuthService
from werkzeug.security import generate_password_hash

class TestProductService:
    def test_get_all_products(self, session):
        # Create test category
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        # Create test products
        product1 = Product(
            name='Product 1',
            price=Decimal('10.99'),
            stock_quantity=10,
            sku='PROD001',
            slug='product-1',
            category_id=category.id
        )
        product2 = Product(
            name='Product 2',
            price=Decimal('20.99'),
            stock_quantity=5,
            sku='PROD002',
            slug='product-2',
            category_id=category.id
        )
        session.add_all([product1, product2])
        session.commit()

        # Test getting all products
        products = ProductService.get_all_products()
        assert len(products.items) == 2
        assert products.items[0].name == 'Product 2'  # Ordered by created_at desc

    def test_get_product_by_id(self, session):
        # Create test category
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        # Create test product
        product = Product(
            name='Test Product',
            price=Decimal('15.99'),
            stock_quantity=8,
            sku='TEST001',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Test getting product by ID
        fetched_product = ProductService.get_product_by_id(product.id)
        assert fetched_product.id == product.id
        assert fetched_product.name == 'Test Product'

    def test_search_products(self, session):
        # Create test category
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        # Create test products
        product1 = Product(
            name='Search Test Product',
            description='This is a test product for searching',
            price=Decimal('10.99'),
            stock_quantity=10,
            sku='SEARCH001',
            slug='search-test-product',
            category_id=category.id
        )
        product2 = Product(
            name='Another Product',
            description='Not related to search',
            price=Decimal('20.99'),
            stock_quantity=5,
            sku='ANOTHER001',
            slug='another-product',
            category_id=category.id
        )
        session.add_all([product1, product2])
        session.commit()

        # Test search
        results = ProductService.search_products('search')
        assert len(results.items) == 1
        assert results.items[0].name == 'Search Test Product'

    def test_check_product_stock(self, session):
        # Create test category
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        # Create test product
        product = Product(
            name='Stock Test Product',
            price=Decimal('15.99'),
            stock_quantity=5,
            sku='STOCK001',
            slug='stock-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Test stock check
        in_stock = ProductService.check_product_stock(product.id, 3)
        assert in_stock[0] is True

        out_of_stock = ProductService.check_product_stock(product.id, 10)
        assert out_of_stock[0] is False

class TestCartService:
    def test_get_active_cart(self, session):
        # Create test user
        user = User(
            username='cartuser',
            email='cart@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Test getting active cart (should create new one)
        cart = CartService.get_active_cart(user.id)
        assert cart is not None
        assert cart.user_id == user.id
        assert cart.is_active is True

    def test_add_item_to_cart(self, session):
        # Create test user
        user = User(
            username='cartuser2',
            email='cart2@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Cart Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='CART001',
            slug='cart-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Test adding item to cart
        cart_item, error = CartService.add_item_to_cart(user.id, product.id, 2)
        assert error is None
        assert cart_item is not None
        assert cart_item.quantity == 2
        assert cart_item.unit_price == Decimal('19.99')

    def test_update_cart_item(self, session):
        # Create test user
        user = User(
            username='cartuser3',
            email='cart3@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Update Test Product',
            price=Decimal('29.99'),
            stock_quantity=10,
            sku='UPDATE001',
            slug='update-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Add item to cart
        cart = CartService.get_active_cart(user.id)
        cart_item = cart.add_item(product, 1)

        # Test updating item quantity
        updated_item, error = CartService.update_cart_item(user.id, cart_item.id, 3)
        assert error is None
        assert updated_item.quantity == 3

    def test_remove_cart_item(self, session):
        # Create test user
        user = User(
            username='cartuser4',
            email='cart4@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Remove Test Product',
            price=Decimal('39.99'),
            stock_quantity=10,
            sku='REMOVE001',
            slug='remove-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Add item to cart
        cart = CartService.get_active_cart(user.id)
        cart_item = cart.add_item(product, 1)

        # Test removing item
        removed_item, error = CartService.remove_cart_item(user.id, cart_item.id)
        assert error is None
        assert removed_item.product_id == product.id

    def test_clear_cart(self, session):
        # Create test user
        user = User(
            username='cartuser5',
            email='cart5@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Clear Test Product',
            price=Decimal('49.99'),
            stock_quantity=10,
            sku='CLEAR001',
            slug='clear-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Add item to cart
        cart = CartService.get_active_cart(user.id)
        cart.add_item(product, 2)

        # Test clearing cart
        cleared_cart, error = CartService.clear_cart(user.id)
        assert error is None
        assert cleared_cart.is_active is False
        assert len(cleared_cart.items) == 0

    def test_get_cart_summary(self, session):
        # Create test user
        user = User(
            username='cartuser6',
            email='cart6@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and products
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product1 = Product(
            name='Summary Product 1',
            price=Decimal('10.99'),
            stock_quantity=10,
            sku='SUMMARY001',
            slug='summary-product-1',
            category_id=category.id
        )
        product2 = Product(
            name='Summary Product 2',
            price=Decimal('20.99'),
            stock_quantity=5,
            sku='SUMMARY002',
            slug='summary-product-2',
            category_id=category.id
        )
        session.add_all([product1, product2])
        session.commit()

        # Add items to cart
        cart = CartService.get_active_cart(user.id)
        cart.add_item(product1, 2)
        cart.add_item(product2, 1)

        # Test cart summary
        summary = CartService.get_cart_summary(user.id)
        assert summary['item_count'] == 3
        assert summary['total_price'] == Decimal('42.97')
        assert len(summary['items']) == 2

class TestOrderService:
    def test_create_order(self, session):
        # Create test user
        user = User(
            username='orderuser',
            email='order@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Order Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            sku='ORDER001',
            slug='order-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Add product to cart
        cart = CartService.get_active_cart(user.id)
        cart.add_item(product, 1)

        # Test creating order
        shipping_data = {
            'shipping_address': '123 Test St',
            'billing_address': '123 Test St',
            'payment_method': 'credit_card',
            'notes': 'Test order'
        }

        order, error = OrderService.create_order(user.id, shipping_data, cart.id)
        assert error is None
        assert order is not None
        assert order.order_number.startswith('ORD-')
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 1
        assert order.items[0].product_id == product.id
        assert order.items[0].quantity == 1

        # Verify product stock was decreased
        updated_product = Product.query.get(product.id)
        assert updated_product.stock_quantity == 9

    def test_get_order_by_number(self, session):
        # Create test user
        user = User(
            username='orderuser2',
            email='order2@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test order
        order = Order(
            user_id=user.id,
            order_number='TEST12345',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('100.00')
        )
        session.add(order)
        session.commit()

        # Test getting order by number
        fetched_order = OrderService.get_order_by_number('TEST12345')
        assert fetched_order is not None
        assert fetched_order.order_number == 'TEST12345'

    def test_cancel_order(self, session):
        # Create test user
        user = User(
            username='orderuser3',
            email='order3@example.com',
            password_hash=generate_password_hash('password123')
        )
        session.add(user)
        session.commit()

        # Create test category and product
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Cancel Test Product',
            price=Decimal('59.99'),
            stock_quantity=10,
            sku='CANCEL001',
            slug='cancel-test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        # Create test order with item
        order = Order(
            user_id=user.id,
            order_number='CANCEL12345',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('59.99')
        )
        session.add(order)
        session.commit()

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            unit_price=Decimal('59.99')
        )
        session.add(order_item)
        session.commit()

        # Decrease product stock
        product.stock_quantity = 9
        session.commit()

        # Test cancelling order
        success, error = OrderService.cancel_order('CANCEL12345', user.id)
        assert success is True
        assert error is None

        # Verify order status and product stock
        cancelled_order = Order.query.get(order.id)
        assert cancelled_order.status == OrderStatus.CANCELLED

        updated_product = Product.query.get(product.id)
        assert updated_product.stock_quantity == 10

class TestAuthService:
    def test_register_user(self, session):
        # Test user data
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        # Test registration
        user, error = AuthService.register_user(user_data)
        assert error is None
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.verify_password('Password123!') is True

    def test_authenticate_user(self, session):
        # Create test user
        user = User(
            username='authuser',
            email='auth@example.com',
            password_hash=generate_password_hash('Password123!')
        )
        session.add(user)
        session.commit()

        # Test authentication
        authenticated_user = AuthService.authenticate_user('auth@example.com', 'Password123!')
        assert authenticated_user is not None
        assert authenticated_user.email == 'auth@example.com'

        # Test wrong password
        wrong_password_user = AuthService.authenticate_user('auth@example.com', 'wrongpassword')
        assert wrong_password_user is None

    def test_update_password(self, session):
        # Create test user
        user = User(
            username='passworduser',
            email='password@example.com',
            password_hash=generate_password_hash('OldPassword123!')
        )
        session.add(user)
        session.commit()

        # Test password update
        success, error = AuthService.update_password(user.id, 'OldPassword123!', 'NewPassword123!')
        assert success is True
        assert error is None

        # Verify new password
        updated_user = User.query.get(user.id)
        assert updated_user.verify_password('NewPassword123!') is True
        assert updated_user.verify_password('OldPassword123!') is False