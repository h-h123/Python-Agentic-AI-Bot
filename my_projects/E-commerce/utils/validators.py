from flask import current_app, flash, request
from werkzeug.datastructures import MultiDict
from wtforms import ValidationError
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
import phonenumbers
from ..models.product import Product
from ..models.user import User

def validate_product_data(form_data):
    """Validate product data before creation or update."""
    errors = {}

    name = form_data.get('name', '').strip()
    if not name:
        errors['name'] = 'Product name is required'
    elif len(name) > 100:
        errors['name'] = 'Product name must be 100 characters or less'

    description = form_data.get('description', '').strip()
    if description and len(description) > 2000:
        errors['description'] = 'Description must be 2000 characters or less'

    try:
        price = Decimal(str(form_data.get('price', 0)))
        if price <= 0:
            errors['price'] = 'Price must be greater than zero'
    except (InvalidOperation, ValueError):
        errors['price'] = 'Invalid price format'

    try:
        stock = int(form_data.get('stock', 0))
        if stock < 0:
            errors['stock'] = 'Stock cannot be negative'
    except (ValueError, TypeError):
        errors['stock'] = 'Invalid stock value'

    sku = form_data.get('sku', '').strip()
    if not sku:
        errors['sku'] = 'SKU is required'
    elif len(sku) > 50:
        errors['sku'] = 'SKU must be 50 characters or less'
    else:
        existing_product = Product.query.filter(Product.sku == sku).first()
        product_id = form_data.get('id')
        if existing_product and (not product_id or str(existing_product.id) != str(product_id)):
            errors['sku'] = 'SKU already exists'

    category_id = form_data.get('category_id')
    if not category_id or not str(category_id).isdigit():
        errors['category_id'] = 'Valid category is required'

    return errors

def validate_user_data(form_data, is_update=False):
    """Validate user registration or profile update data."""
    errors = {}

    username = form_data.get('username', '').strip()
    if not is_update and not username:
        errors['username'] = 'Username is required'
    elif username and len(username) > 80:
        errors['username'] = 'Username must be 80 characters or less'
    else:
        existing_user = User.query.filter(User.username == username).first()
        user_id = form_data.get('id')
        if existing_user and (not user_id or str(existing_user.id) != str(user_id)):
            errors['username'] = 'Username already taken'

    email = form_data.get('email', '').strip()
    if not is_update and not email:
        errors['email'] = 'Email is required'
    elif email and not validate_email(email):
        errors['email'] = 'Invalid email format'
    elif email:
        existing_user = User.query.filter(User.email == email).first()
        user_id = form_data.get('id')
        if existing_user and (not user_id or str(existing_user.id) != str(user_id)):
            errors['email'] = 'Email already registered'

    if not is_update:
        password = form_data.get('password', '')
        if not password:
            errors['password'] = 'Password is required'
        elif not validate_password(password):
            errors['password'] = 'Password must be at least 8 characters with letters and numbers'

        confirm_password = form_data.get('confirm_password', '')
        if password and confirm_password and password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'

    first_name = form_data.get('first_name', '').strip()
    if first_name and len(first_name) > 50:
        errors['first_name'] = 'First name must be 50 characters or less'

    last_name = form_data.get('last_name', '').strip()
    if last_name and len(last_name) > 50:
        errors['last_name'] = 'Last name must be 50 characters or less'

    phone_number = form_data.get('phone_number', '').strip()
    if phone_number and not validate_phone_number(phone_number):
        errors['phone_number'] = 'Invalid phone number format'

    return errors

def validate_address_data(form_data):
    """Validate address data."""
    errors = {}

    street = form_data.get('street', '').strip()
    if not street:
        errors['street'] = 'Street address is required'
    elif len(street) > 100:
        errors['street'] = 'Street address must be 100 characters or less'

    city = form_data.get('city', '').strip()
    if not city:
        errors['city'] = 'City is required'
    elif len(city) > 50:
        errors['city'] = 'City must be 50 characters or less'

    state = form_data.get('state', '').strip()
    if not state:
        errors['state'] = 'State is required'
    elif len(state) > 50:
        errors['state'] = 'State must be 50 characters or less'

    postal_code = form_data.get('postal_code', '').strip()
    if not postal_code:
        errors['postal_code'] = 'Postal code is required'
    elif len(postal_code) > 20:
        errors['postal_code'] = 'Postal code must be 20 characters or less'

    country = form_data.get('country', '').strip()
    if not country:
        errors['country'] = 'Country is required'
    elif len(country) > 50:
        errors['country'] = 'Country must be 50 characters or less'

    return errors

def validate_review_data(form_data):
    """Validate product review data."""
    errors = {}

    try:
        rating = int(form_data.get('rating', 0))
        if rating < 1 or rating > 5:
            errors['rating'] = 'Rating must be between 1 and 5'
    except (ValueError, TypeError):
        errors['rating'] = 'Invalid rating value'

    comment = form_data.get('comment', '').strip()
    if comment and len(comment) > 1000:
        errors['comment'] = 'Comment must be 1000 characters or less'

    return errors

def validate_order_data(form_data, user_id):
    """Validate order data before submission."""
    errors = {}

    shipping_address_id = form_data.get('shipping_address_id')
    if not shipping_address_id or not str(shipping_address_id).isdigit():
        errors['shipping_address_id'] = 'Valid shipping address is required'

    payment_method = form_data.get('payment_method', '').strip()
    if not payment_method:
        errors['payment_method'] = 'Payment method is required'

    notes = form_data.get('notes', '').strip()
    if notes and len(notes) > 1000:
        errors['notes'] = 'Order notes must be 1000 characters or less'

    return errors

def validate_cart_item_quantity(quantity, product):
    """Validate cart item quantity against product stock."""
    errors = []

    try:
        quantity = int(quantity)
        if quantity <= 0:
            errors.append('Quantity must be at least 1')
        elif product.stock < quantity:
            errors.append(f'Only {product.stock} items available in stock')
    except (ValueError, TypeError):
        errors.append('Invalid quantity')

    return errors

def validate_file_upload(file):
    """Validate file upload."""
    errors = []

    if not file:
        errors.append('No file selected')
        return errors

    if not allowed_file(file.filename):
        errors.append('Invalid file type')

    try:
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            errors.append(f'File too large. Maximum size is {max_size/1024/1024}MB')
    except:
        errors.append('Invalid file')

    return errors

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def validate_phone_number(phone):
    """Validate phone number using phonenumbers library."""
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

def allowed_file(filename):
    """Check if file has an allowed extension."""
    if not filename or '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {})

def validate_slug(slug):
    """Validate URL slug format."""
    if not slug:
        return False
    pattern = r'^[a-z0-9-]+$'
    return re.match(pattern, slug) is not None

def validate_discount(discount_price, original_price):
    """Validate discount price is less than original price."""
    try:
        discount_price = Decimal(str(discount_price))
        original_price = Decimal(str(original_price))

        if discount_price < 0:
            return False, 'Discount price cannot be negative'
        if discount_price > original_price:
            return False, 'Discount price cannot be greater than original price'
        return True, None
    except (InvalidOperation, ValueError):
        return False, 'Invalid price format'

def validate_category_data(form_data):
    """Validate category data."""
    errors = {}

    name = form_data.get('name', '').strip()
    if not name:
        errors['name'] = 'Category name is required'
    elif len(name) > 50:
        errors['name'] = 'Category name must be 50 characters or less'

    slug = form_data.get('slug', '').strip()
    if not slug:
        errors['slug'] = 'Slug is required'
    elif not validate_slug(slug):
        errors['slug'] = 'Slug can only contain lowercase letters, numbers, and hyphens'
    elif len(slug) > 50:
        errors['slug'] = 'Slug must be 50 characters or less'

    description = form_data.get('description', '').strip()
    if description and len(description) > 500:
        errors['description'] = 'Description must be 500 characters or less'

    return errors

def validate_form_errors(form):
    """Flash form validation errors."""
    for field, errors in form.errors.items():
        for error in errors:
            field_label = getattr(form, field).label.text
            flash(f"{field_label}: {error}", 'danger')

def validate_stock_level(stock):
    """Validate product stock level."""
    try:
        stock = int(stock)
        if stock < 0:
            return False, 'Stock cannot be negative'
        return True, None
    except (ValueError, TypeError):
        return False, 'Invalid stock value'

def validate_price(price):
    """Validate product price."""
    try:
        price = Decimal(str(price))
        if price <= 0:
            return False, 'Price must be greater than zero'
        return True, None
    except (InvalidOperation, ValueError):
        return False, 'Invalid price format'