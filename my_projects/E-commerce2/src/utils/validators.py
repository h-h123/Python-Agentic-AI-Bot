import re
from decimal import Decimal
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import current_app

class Validators:
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not email:
            return False, "Email is required"
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, None

    @staticmethod
    def validate_password(password, min_length=8):
        """Validate password strength."""
        if not password:
            return False, "Password is required"
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, None

    @staticmethod
    def validate_username(username, min_length=4):
        """Validate username format."""
        if not username:
            return False, "Username is required"
        if len(username) < min_length:
            return False, f"Username must be at least {min_length} characters long"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, None

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format."""
        if not phone:
            return False, "Phone number is required"
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) < 7 or len(digits) > 15:
            return False, "Phone number must be between 7 and 15 digits"
        return True, None

    @staticmethod
    def validate_price(price):
        """Validate price value."""
        if price is None:
            return False, "Price is required"
        try:
            price = Decimal(str(price))
            if price <= 0:
                return False, "Price must be greater than zero"
            if price > Decimal('999999.99'):
                return False, "Price is too large"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid price format"

    @staticmethod
    def validate_quantity(quantity):
        """Validate product quantity."""
        if quantity is None:
            return False, "Quantity is required"
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Quantity must be greater than zero"
            if quantity > 1000:
                return False, "Quantity is too large"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid quantity format"

    @staticmethod
    def validate_stock_quantity(stock):
        """Validate product stock quantity."""
        if stock is None:
            return False, "Stock quantity is required"
        try:
            stock = int(stock)
            if stock < 0:
                return False, "Stock quantity cannot be negative"
            if stock > 100000:
                return False, "Stock quantity is too large"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid stock quantity format"

    @staticmethod
    def validate_sku(sku):
        """Validate product SKU format."""
        if not sku:
            return False, "SKU is required"
        if len(sku) > 50:
            return False, "SKU is too long (max 50 characters)"
        if not re.match(r'^[a-zA-Z0-9\-_]+$', sku):
            return False, "SKU can only contain letters, numbers, hyphens, and underscores"
        return True, None

    @staticmethod
    def validate_slug(slug):
        """Validate URL slug format."""
        if not slug:
            return False, "Slug is required"
        if len(slug) > 100:
            return False, "Slug is too long (max 100 characters)"
        if not re.match(r'^[a-z0-9\-]+$', slug):
            return False, "Slug can only contain lowercase letters, numbers, and hyphens"
        return True, None

    @staticmethod
    def validate_name(name, min_length=2, max_length=100):
        """Validate product or category name."""
        if not name:
            return False, "Name is required"
        if len(name) < min_length:
            return False, f"Name must be at least {min_length} characters long"
        if len(name) > max_length:
            return False, f"Name is too long (max {max_length} characters)"
        return True, None

    @staticmethod
    def validate_description(description, max_length=2000):
        """Validate product description."""
        if not description:
            return False, "Description is required"
        if len(description) > max_length:
            return False, f"Description is too long (max {max_length} characters)"
        return True, None

    @staticmethod
    def validate_address(address, min_length=10, max_length=500):
        """Validate shipping/billing address."""
        if not address:
            return False, "Address is required"
        if len(address) < min_length:
            return False, f"Address must be at least {min_length} characters long"
        if len(address) > max_length:
            return False, f"Address is too long (max {max_length} characters)"
        return True, None

    @staticmethod
    def validate_payment_method(method):
        """Validate payment method."""
        valid_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
        if not method:
            return False, "Payment method is required"
        if method.lower() not in valid_methods:
            return False, f"Invalid payment method. Valid methods: {', '.join(valid_methods)}"
        return True, None

    @staticmethod
    def validate_shipping_method(method):
        """Validate shipping method."""
        valid_methods = ['standard', 'express', 'overnight', 'pickup']
        if not method:
            return False, "Shipping method is required"
        if method.lower() not in valid_methods:
            return False, f"Invalid shipping method. Valid methods: {', '.join(valid_methods)}"
        return True, None

    @staticmethod
    def validate_date(date_str, date_format='%Y-%m-%d'):
        """Validate date format."""
        if not date_str:
            return False, "Date is required"
        try:
            datetime.strptime(date_str, date_format)
            return True, None
        except ValueError:
            return False, f"Invalid date format. Expected format: {date_format}"

    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """Validate file extension."""
        if not filename:
            return False, "Filename is required"
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in allowed_extensions:
            return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
        return True, None

    @staticmethod
    def validate_file_size(file, max_size_mb):
        """Validate file size."""
        if not file:
            return False, "File is required"
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        max_size = max_size_mb * 1024 * 1024
        if size > max_size:
            return False, f"File is too large. Maximum size: {max_size_mb}MB"
        return True, None

    @staticmethod
    def validate_current_password(user, current_password):
        """Validate current password for password change."""
        if not current_password:
            return False, "Current password is required"
        if not user.verify_password(current_password):
            return False, "Current password is incorrect"
        return True, None

    @staticmethod
    def validate_new_password(new_password, current_password=None):
        """Validate new password for password change."""
        if not new_password:
            return False, "New password is required"
        if current_password and new_password == current_password:
            return False, "New password must be different from current password"
        return Validators.validate_password(new_password)

    @staticmethod
    def validate_order_status(status):
        """Validate order status."""
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
        if not status:
            return False, "Order status is required"
        if status.lower() not in valid_statuses:
            return False, f"Invalid order status. Valid statuses: {', '.join(valid_statuses)}"
        return True, None

    @staticmethod
    def validate_tracking_number(tracking_number):
        """Validate shipping tracking number."""
        if not tracking_number:
            return False, "Tracking number is required"
        if len(tracking_number) > 100:
            return False, "Tracking number is too long (max 100 characters)"
        return True, None

    @staticmethod
    def validate_discount(discount):
        """Validate discount percentage."""
        if discount is None:
            return True, None  # Discount is optional
        try:
            discount = float(discount)
            if discount < 0:
                return False, "Discount cannot be negative"
            if discount > 100:
                return False, "Discount cannot be more than 100%"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid discount format"