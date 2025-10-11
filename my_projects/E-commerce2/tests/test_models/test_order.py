import pytest
from datetime import datetime
from src.models.order import Order, OrderItem, OrderStatus
from src.models.product import Product
from src.models.user import User

class TestOrderModel:
    """Test cases for the Order model"""

    def test_order_creation(self, init_database):
        """Test creating a new order"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00,
            shipping_amount=5.00,
            tax_amount=8.00
        )
        order.generate_order_number()
        init_database.session.add(order)
        init_database.session.commit()

        assert order.id is not None
        assert order.user_id == user.id
        assert order.order_number is not None
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == 100.00
        assert order.shipping_amount == 5.00
        assert order.tax_amount == 8.00
        assert order.shipping_address == '123 Test St, Test City'
        assert order.payment_status == 'unpaid'
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_calculate_total(self, init_database):
        """Test calculating order total"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product1 = Product(
            name='Test Product 1',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product1)

        product2 = Product(
            name='Test Product 2',
            price=29.99,
            stock_quantity=5
        )
        init_database.session.add(product2)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            shipping_amount=5.00,
            tax_amount=4.00
        )
        init_database.session.add(order)

        order_item1 = OrderItem(
            order_id=order.id,
            product_id=product1.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item1)

        order_item2 = OrderItem(
            order_id=order.id,
            product_id=product2.id,
            quantity=1,
            unit_price=29.99
        )
        init_database.session.add(order_item2)

        init_database.session.commit()

        total = order.calculate_total()
        subtotal = (19.99 * 2) + (29.99 * 1)
        expected_total = subtotal + 5.00 + 4.00
        assert total == expected_total

    def test_order_update_status(self, init_database):
        """Test updating order status"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        order.update_status(OrderStatus.PROCESSING)
        assert order.status == OrderStatus.PROCESSING

        order.update_status('shipped')
        assert order.status == OrderStatus.SHIPPED

        with pytest.raises(ValueError):
            order.update_status('invalid_status')

    def test_order_add_item(self, init_database):
        """Test adding an item to the order"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=0
        )
        init_database.session.add(order)
        init_database.session.commit()

        order_item = order.add_item(
            product_id=product.id,
            quantity=2,
            unit_price=19.99
        )

        assert order_item is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == product.id
        assert order_item.quantity == 2
        assert order_item.unit_price == 19.99

    def test_order_update_total(self, init_database):
        """Test updating order total"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product1 = Product(
            name='Test Product 1',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product1)

        product2 = Product(
            name='Test Product 2',
            price=29.99,
            stock_quantity=5
        )
        init_database.session.add(product2)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            shipping_amount=5.00,
            tax_amount=4.00,
            total_amount=0
        )
        init_database.session.add(order)

        order_item1 = OrderItem(
            order_id=order.id,
            product_id=product1.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item1)

        order_item2 = OrderItem(
            order_id=order.id,
            product_id=product2.id,
            quantity=1,
            unit_price=29.99
        )
        init_database.session.add(order_item2)

        init_database.session.commit()

        order.update_total()
        subtotal = (19.99 * 2) + (29.99 * 1)
        expected_total = subtotal + 5.00 + 4.00
        assert order.total_amount == expected_total

    def test_order_cancel(self, init_database):
        """Test cancelling an order"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00,
            status=OrderStatus.PENDING
        )
        init_database.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item)

        init_database.session.commit()

        # Reduce stock to simulate order processing
        product.stock_quantity = 8
        init_database.session.commit()

        order.cancel()
        assert order.status == OrderStatus.CANCELLED
        assert product.stock_quantity == 10

    def test_order_mark_as_paid(self, init_database):
        """Test marking order as paid"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        order.mark_as_paid()
        assert order.payment_status == 'paid'

    def test_order_mark_as_shipped(self, init_database):
        """Test marking order as shipped"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        order.mark_as_shipped('TRACK123')
        assert order.status == OrderStatus.SHIPPED
        assert order.tracking_number == 'TRACK123'

    def test_order_mark_as_delivered(self, init_database):
        """Test marking order as delivered"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        order.mark_as_delivered()
        assert order.status == OrderStatus.DELIVERED

    def test_order_generate_order_number(self, init_database):
        """Test generating order number"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)
        init_database.session.commit()

        order.generate_order_number()
        assert order.order_number is not None
        assert order.order_number.startswith('ORD-')

    def test_order_repr(self, init_database):
        """Test the string representation of an order"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        order.generate_order_number()
        init_database.session.add(order)
        init_database.session.commit()

        assert repr(order) == f'<Order {order.order_number} (User: {user.id})>'

class TestOrderItemModel:
    """Test cases for the OrderItem model"""

    def test_order_item_creation(self, init_database):
        """Test creating a new order item"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item)
        init_database.session.commit()

        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == product.id
        assert order_item.quantity == 2
        assert order_item.unit_price == 19.99
        assert order_item.created_at is not None
        assert order_item.updated_at is not None

    def test_order_item_calculate_subtotal(self, init_database):
        """Test calculating subtotal for order item"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item)
        init_database.session.commit()

        subtotal = order_item.calculate_subtotal()
        assert subtotal == 19.99 * 2

    def test_order_item_repr(self, init_database):
        """Test the string representation of an order item"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)

        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=100.00
        )
        init_database.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=19.99
        )
        init_database.session.add(order_item)
        init_database.session.commit()

        assert repr(order_item) == f'<OrderItem {order_item.id} (Order: {order.id}, Product: {product.id})>'