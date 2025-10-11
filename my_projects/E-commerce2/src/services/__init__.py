from flask import current_app
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem
from src.models.user import User

class ProductService:
    @staticmethod
    def get_active_products():
        return Product.query.filter_by(is_active=True).all()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get_or_404(product_id)

    @staticmethod
    def get_product_by_slug(slug):
        return Product.query.filter_by(slug=slug, is_active=True).first_or_404()

    @staticmethod
    def search_products(query, limit=10):
        return Product.query.filter(
            Product.name.ilike(f'%{query}%'),
            Product.is_active == True
        ).limit(limit).all()

    @staticmethod
    def get_products_by_category(category_id):
        return Product.query.filter_by(
            category_id=category_id,
            is_active=True
        ).all()

    @staticmethod
    def check_stock(product_id, quantity):
        product = Product.query.get(product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity

class CartService:
    @staticmethod
    def get_active_cart(user_id):
        return Cart.query.filter_by(user_id=user_id, is_active=True).first()

    @staticmethod
    def create_cart(user_id):
        cart = Cart(user_id=user_id)
        cart.save()
        return cart

    @staticmethod
    def add_to_cart(cart_id, product_id, quantity=1):
        cart = Cart.query.get(cart_id)
        if not cart:
            return None

        product = Product.query.get(product_id)
        if not product or not product.is_in_stock():
            return None

        if quantity > product.stock_quantity:
            quantity = product.stock_quantity

        return cart.add_item(product, quantity)

    @staticmethod
    def update_cart_item(item_id, quantity):
        item = CartItem.query.get(item_id)
        if not item:
            return None

        if quantity <= 0:
            cart = Cart.query.get(item.cart_id)
            return cart.remove_item(item.product_id)

        product = Product.query.get(item.product_id)
        if quantity > product.stock_quantity:
            return None

        cart = Cart.query.get(item.cart_id)
        return cart.update_item_quantity(item.product_id, quantity)

    @staticmethod
    def remove_cart_item(item_id):
        item = CartItem.query.get(item_id)
        if not item:
            return None

        cart = Cart.query.get(item.cart_id)
        return cart.remove_item(item.product_id)

    @staticmethod
    def clear_cart(cart_id):
        cart = Cart.query.get(cart_id)
        if cart:
            cart.clear()
        return cart

class OrderService:
    @staticmethod
    def create_order(user_id, cart_id, shipping_data):
        cart = Cart.query.get(cart_id)
        if not cart or not cart.items:
            return None

        order_number = f"ORD-{user_id}-{len(Order.query.filter_by(user_id=user_id).all()) + 1}"

        order = Order(
            user_id=user_id,
            order_number=order_number,
            shipping_address=shipping_data['shipping_address'],
            billing_address=shipping_data.get('billing_address', shipping_data['shipping_address']),
            payment_method=shipping_data['payment_method'],
            notes=shipping_data.get('notes', ''),
            status='pending'
        )

        try:
            for item in cart.items:
                product = Product.query.get(item.product_id)
                if not product.decrease_stock(item.quantity):
                    raise ValueError(f"Not enough stock for product {product.id}")

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                order.items.append(order_item)

            order.calculate_total()
            cart.clear()
            return order
        except Exception as e:
            current_app.logger.error(f"Error creating order: {str(e)}")
            return None

    @staticmethod
    def get_order_by_number(order_number, user_id=None):
        query = Order.query.filter_by(order_number=order_number)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first_or_404()

    @staticmethod
    def get_user_orders(user_id):
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def cancel_order(order_number, user_id):
        order = Order.query.filter_by(order_number=order_number, user_id=user_id).first()
        if not order:
            return False

        if order.status not in ['pending', 'processing']:
            return False

        try:
            for item in order.items:
                product = Product.query.get(item.product_id)
                product.increase_stock(item.quantity)

            order.update_status('cancelled')
            return True
        except Exception as e:
            current_app.logger.error(f"Error cancelling order: {str(e)}")
            return False

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get_or_404(user_id)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(user_data):
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone=user_data.get('phone', ''),
            address=user_data.get('address', '')
        )
        user.save()
        return user

    @staticmethod
    def update_user(user_id, update_data):
        user = User.query.get(user_id)
        if not user:
            return None

        for key, value in update_data.items():
            if hasattr(user, key) and key != 'password_hash':
                setattr(user, key, value)

        user.save()
        return user