import os
import re
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from flask import current_app, flash, redirect, url_for, request
from werkzeug.utils import secure_filename
from slugify import slugify

def generate_slug(text, model_class, field='slug', max_length=100):
    """
    Generate a unique slug for a model instance.
    """
    if not text:
        text = "untitled"

    base_slug = slugify(text)[:max_length]
    slug = base_slug
    num = 1

    while model_class.query.filter(getattr(model_class, field) == slug).first():
        slug = f"{base_slug}-{num}"
        num += 1

    return slug

def generate_sku(name, category_prefix=None, length=8):
    """
    Generate a unique SKU for a product.
    """
    if category_prefix:
        prefix = category_prefix[:3].upper()
    else:
        prefix = "PRD"

    # Generate random suffix
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(length))

    return f"{prefix}-{suffix}"

def generate_order_number(user_id):
    """
    Generate a unique order number.
    """
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"ORD-{user_id}-{timestamp}-{random_part}"

def format_currency(value, currency='USD'):
    """
    Format a decimal value as currency.
    """
    if not isinstance(value, (int, float, Decimal)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return "N/A"

    return f"{current_app.config.get('CURRENCY_SYMBOL', '$')}{value:,.2f}"

def calculate_tax(amount, tax_rate):
    """
    Calculate tax amount based on a tax rate.
    """
    if not isinstance(amount, (int, float, Decimal)):
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return Decimal('0.00')

    if not isinstance(tax_rate, (int, float, Decimal)):
        try:
            tax_rate = float(tax_rate)
        except (ValueError, TypeError):
            return Decimal('0.00')

    return Decimal(str(amount)) * Decimal(str(tax_rate)) / Decimal('100')

def calculate_shipping_cost(weight, rate_per_kg, base_cost=0):
    """
    Calculate shipping cost based on weight.
    """
    try:
        weight = float(weight)
        rate_per_kg = float(rate_per_kg)
        base_cost = float(base_cost)
    except (ValueError, TypeError):
        return Decimal('0.00')

    return Decimal(str(base_cost)) + Decimal(str(weight)) * Decimal(str(rate_per_kg))

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """
    Validate an uploaded file.
    """
    if not file:
        return False, "No file provided"

    if allowed_extensions:
        filename = file.filename.lower()
        if not ('.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions):
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    if max_size:
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        if file_length > max_size:
            return False, f"File too large. Maximum size: {max_size / (1024 * 1024)}MB"

    return True, "File is valid"

def save_uploaded_file(file, upload_folder, filename=None):
    """
    Save an uploaded file to the specified folder.
    """
    if not filename:
        filename = secure_filename(file.filename)

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath

def generate_random_string(length=10):
    """
    Generate a random string of fixed length.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_paginated_items(query, page=1, per_page=10):
    """
    Get paginated items from a query.
    """
    return query.paginate(page=page, per_page=per_page, error_out=False)

def flash_errors(form, category='warning'):
    """
    Flash all errors for a form.
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", category)

def redirect_back(default='main.index', **kwargs):
    """
    Redirect to the previous page or a default endpoint.
    """
    for target in request.args.get('next'), request.referrer:
        if target:
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def format_date(date, format='%Y-%m-%d'):
    """
    Format a date object as a string.
    """
    if not date:
        return ""
    return date.strftime(format)

def parse_date(date_string, format='%Y-%m-%d'):
    """
    Parse a date string into a date object.
    """
    try:
        return datetime.strptime(date_string, format).date()
    except (ValueError, TypeError):
        return None

def calculate_discount(original_price, discount_percent):
    """
    Calculate the discounted price.
    """
    if not isinstance(original_price, (int, float, Decimal)):
        try:
            original_price = float(original_price)
        except (ValueError, TypeError):
            return Decimal('0.00')

    if not isinstance(discount_percent, (int, float, Decimal)):
        try:
            discount_percent = float(discount_percent)
        except (ValueError, TypeError):
            return Decimal(str(original_price))

    discount_amount = Decimal(str(original_price)) * Decimal(str(discount_percent)) / Decimal('100')
    return Decimal(str(original_price)) - discount_amount

def get_file_extension(filename):
    """
    Get the file extension from a filename.
    """
    return os.path.splitext(filename)[1].lower() if filename else ""

def validate_email(email):
    """
    Validate an email address format.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate a phone number format.
    """
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', phone)
    return len(digits) >= 7 and len(digits) <= 15

def generate_password(length=12):
    """
    Generate a random password.
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)):
            return password

def get_client_ip():
    """
    Get the client's IP address from the request.
    """
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def format_datetime(dt, format='%Y-%m-%d %H:%M'):
    """
    Format a datetime object as a string.
    """
    if not dt:
        return ""
    return dt.strftime(format)

def days_between_dates(date1, date2):
    """
    Calculate the number of days between two dates.
    """
    if not date1 or not date2:
        return 0
    delta = date2 - date1
    return delta.days

def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a maximum length.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + suffix

def sanitize_html(text):
    """
    Basic HTML sanitization to prevent XSS.
    """
    if not text:
        return ""
    # Remove script tags and attributes that can execute code
    sanitized = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    return sanitized