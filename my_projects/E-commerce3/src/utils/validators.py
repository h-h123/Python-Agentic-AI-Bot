from flask import current_app, jsonify
from werkzeug.security import check_password_hash
from werkzeug.datasets import validate_email
import re
import phonenumbers
from datetime import datetime
from decimal import Decimal, InvalidOperation
from src.models.user import User
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderStatus

class Validators:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False, "Email is required"
        if not validate_email(email):
            return False, "Invalid email format"
        return True, None

    @staticmethod
    def validate_password(password, min_length=6):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        return True, None

    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username:
            return False, "Username is required"
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, None

    @staticmethod
    def validate_phone_number(phone):
        """Validate phone number format"""
        if not phone:
            return False, "Phone number is required"
        try:
            parsed = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed):
                return False, "Invalid phone number"
            return True, None
        except phonenumbers.phonenumberutil.NumberParseException:
            return False, "Invalid phone number format"

    @staticmethod
    def validate_price(price):
        """Validate price format"""
        if price is None:
            return False, "Price is required"
        try:
            Decimal(str(price))
            if Decimal(str(price)) <= 0:
                return False, "Price must be greater than 0"
            return True, None
        except InvalidOperation:
            return False, "Invalid price format"

    @staticmethod
    def validate_quantity(quantity, max_available=None):
        """Validate product quantity"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Quantity must be greater than 0"
            if max_available is not None and quantity > max_available:
                return False, f"Quantity cannot exceed available stock ({max_available})"
            return True, quantity
        except (ValueError, TypeError):
            return False, "Invalid quantity"

    @staticmethod
    def validate_product_stock(product_id, quantity):
        """Validate if product has enough stock"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        if not product.in_stock:
            return False, "Product is out of stock"
        if quantity > product.stock:
            return False, f"Only {product.stock} items available in stock"
        return True, None

    @staticmethod
    def validate_order_status_transition(current_status, new_status):
        """Validate if order status transition is allowed"""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [],
            OrderStatus.REFUNDED: []
        }

        if new_status not in valid_transitions.get(current_status, []):
            return False, f"Cannot transition from {current_status.value} to {new_status.value}"
        return True, None

    @staticmethod
    def validate_user_exists(user_id):
        """Validate if user exists"""
        user = User.get_by_id(user_id)
        if not user:
            return False, "User not found"
        return True, None

    @staticmethod
    def validate_product_exists(product_id):
        """Validate if product exists"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"
        return True, None

    @staticmethod
    def validate_cart_item_ownership(user_id, item_id):
        """Validate if cart item belongs to user"""
        item = CartItem.get_by_id(item_id)
        if not item or item.cart.user_id != user_id:
            return False, "Cart item not found or doesn't belong to you"
        return True, None

    @staticmethod
    def validate_order_ownership(user_id, order_id, is_admin=False):
        """Validate if order belongs to user or user is admin"""
        order = Order.get_by_id(order_id)
        if not order:
            return False, "Order not found"
        if not is_admin and order.user_id != user_id:
            return False, "You don't have permission to access this order"
        return True, None

    @staticmethod
    def validate_payment_method(method):
        """Validate payment method"""
        valid_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
        if method not in valid_methods:
            return False, "Invalid payment method"
        return True, None

    @staticmethod
    def validate_shipping_method(method):
        """Validate shipping method"""
        valid_methods = ['standard', 'express']
        if method not in valid_methods:
            return False, "Invalid shipping method"
        return True, None

    @staticmethod
    def validate_discount(discount):
        """Validate discount percentage"""
        try:
            discount = Decimal(str(discount))
            if discount < 0 or discount > 100:
                return False, "Discount must be between 0 and 100"
            return True, None
        except InvalidOperation:
            return False, "Invalid discount format"

    @staticmethod
    def validate_sku(sku):
        """Validate product SKU format"""
        if not sku:
            return False, "SKU is required"
        if len(sku) > 50:
            return False, "SKU must be less than 50 characters"
        if not re.match(r"^[a-zA-Z0-9\-_]+$", sku):
            return False, "SKU can only contain letters, numbers, hyphens, and underscores"
        return True, None

    @staticmethod
    def validate_address(address):
        """Validate shipping/billing address"""
        if not address:
            return False, "Address is required"
        if len(address) > 500:
            return False, "Address must be less than 500 characters"
        return True, None

    @staticmethod
    def validate_file_extension(filename, allowed_extensions=None):
        """Validate file extension"""
        if not filename:
            return False, "Filename is required"

        if allowed_extensions is None:
            allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']

        if '.' not in filename:
            return False, "File must have an extension"

        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return False, f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"

        return True, None

    @staticmethod
    def validate_file_size(file, max_size=None):
        """Validate file size"""
        if not file:
            return False, "File is required"

        if max_size is None:
            max_size = current_app.config['MAX_CONTENT_LENGTH']

        if file.content_length > max_size:
            return False, f"File too large. Max size: {max_size/1024/1024}MB"

        return True, None

    @staticmethod
    def validate_current_password(user, current_password):
        """Validate current password for password change"""
        if not check_password_hash(user.password_hash, current_password):
            return False, "Current password is incorrect"
        return True, None

    @staticmethod
    def validate_password_match(password, confirm_password):
        """Validate if password and confirmation match"""
        if password != confirm_password:
            return False, "Passwords do not match"
        return True, None

    @staticmethod
    def validate_date_format(date_str, format="%Y-%m-%d"):
        """Validate date string format"""
        try:
            datetime.strptime(date_str, format)
            return True, None
        except ValueError:
            return False, f"Invalid date format. Expected format: {format}"