import pytest
from datetime import datetime
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User

class TestCartModel:
    """Test cases for the Cart model"""

    def test_cart_creation(self, init_database):
        """Test creating a new cart"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)
        init_database.session.commit()

        assert cart.id is not None
        assert cart.user_id == user.id
        assert cart.is_active is True
        assert cart.created_at is not None
        assert cart.updated_at is not None

    def test_cart_calculate_total(self, init_database):
        """Test calculating cart total"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item1 = CartItem(
            cart_id=cart.id,
            product_id=product1.id,
            quantity=2
        )
        init_database.session.add(cart_item1)

        cart_item2 = CartItem(
            cart_id=cart.id,
            product_id=product2.id,
            quantity=1
        )
        init_database.session.add(cart_item2)

        init_database.session.commit()

        total = cart.calculate_total()
        assert total == (19.99 * 2) + (29.99 * 1)

    def test_cart_get_item_count(self, init_database):
        """Test getting total item count in cart"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item1 = CartItem(
            cart_id=cart.id,
            product_id=product1.id,
            quantity=2
        )
        init_database.session.add(cart_item1)

        cart_item2 = CartItem(
            cart_id=cart.id,
            product_id=product2.id,
            quantity=1
        )
        init_database.session.add(cart_item2)

        init_database.session.commit()

        item_count = cart.get_item_count()
        assert item_count == 3

    def test_cart_add_item(self, init_database):
        """Test adding an item to the cart"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)
        init_database.session.commit()

        cart_item = cart.add_item(product.id, 2)
        assert cart_item is not None
        assert cart_item.cart_id == cart.id
        assert cart_item.product_id == product.id
        assert cart_item.quantity == 2

        # Test adding same product again (should update quantity)
        cart_item = cart.add_item(product.id, 1)
        assert cart_item.quantity == 3

    def test_cart_remove_item(self, init_database):
        """Test removing an item from the cart"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2
        )
        init_database.session.add(cart_item)
        init_database.session.commit()

        result = cart.remove_item(product.id)
        assert result is True
        assert len(cart.items) == 0

    def test_cart_clear(self, init_database):
        """Test clearing all items from the cart"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item1 = CartItem(
            cart_id=cart.id,
            product_id=product1.id,
            quantity=2
        )
        init_database.session.add(cart_item1)

        cart_item2 = CartItem(
            cart_id=cart.id,
            product_id=product2.id,
            quantity=1
        )
        init_database.session.add(cart_item2)
        init_database.session.commit()

        cart.clear()
        assert len(cart.items) == 0

    def test_cart_merge_with_session_cart(self, init_database):
        """Test merging session cart with user cart"""
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

        # Create user cart
        user_cart = Cart(user_id=user.id)
        init_database.session.add(user_cart)

        # Create session cart
        session_cart = Cart(session_id='test_session')
        init_database.session.add(session_cart)

        # Add items to session cart
        session_cart_item1 = CartItem(
            cart_id=session_cart.id,
            product_id=product1.id,
            quantity=2
        )
        init_database.session.add(session_cart_item1)

        session_cart_item2 = CartItem(
            cart_id=session_cart.id,
            product_id=product2.id,
            quantity=1
        )
        init_database.session.add(session_cart_item2)

        init_database.session.commit()

        user_cart.merge_with_session_cart(session_cart)

        assert len(user_cart.items) == 2
        assert user_cart.items[0].quantity == 2
        assert user_cart.items[1].quantity == 1
        assert session_cart.is_active is False

    def test_cart_repr(self, init_database):
        """Test the string representation of a cart"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)
        init_database.session.commit()

        assert repr(cart) == f'<Cart {cart.id} (User: {user.id})>'

class TestCartItemModel:
    """Test cases for the CartItem model"""

    def test_cart_item_creation(self, init_database):
        """Test creating a new cart item"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2
        )
        init_database.session.add(cart_item)
        init_database.session.commit()

        assert cart_item.id is not None
        assert cart_item.cart_id == cart.id
        assert cart_item.product_id == product.id
        assert cart_item.quantity == 2
        assert cart_item.created_at is not None
        assert cart_item.updated_at is not None

    def test_cart_item_calculate_subtotal(self, init_database):
        """Test calculating subtotal for cart item"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2
        )
        init_database.session.add(cart_item)
        init_database.session.commit()

        subtotal = cart_item.calculate_subtotal()
        assert subtotal == 19.99 * 2

    def test_cart_item_update_quantity(self, init_database):
        """Test updating cart item quantity"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2
        )
        init_database.session.add(cart_item)
        init_database.session.commit()

        # Update quantity
        cart_item.update_quantity(3)
        assert cart_item.quantity == 3

        # Update to 0 (should delete the item)
        cart_item.update_quantity(0)
        assert CartItem.query.get(cart_item.id) is None

    def test_cart_item_repr(self, init_database):
        """Test the string representation of a cart item"""
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

        cart = Cart(user_id=user.id)
        init_database.session.add(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2
        )
        init_database.session.add(cart_item)
        init_database.session.commit()

        assert repr(cart_item) == f'<CartItem {cart_item.id} (Product: {product.id}, Qty: 2)>'