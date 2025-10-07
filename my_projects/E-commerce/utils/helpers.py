"""
Utility functions and helpers for the e-commerce application.
"""

from flask import current_app, flash, redirect, url_for, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import os
import secrets
import string
import re
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
from decimal import Decimal, InvalidOperation
from ..models import db

def admin_required(f):
    """
    Decorator to ensure the user is an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.login_manager._login_disabled and \
           not getattr(current_app.login_manager._user_callback(), 'is_admin', False):
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_sku(length=10):
    """
    Generate a random SKU for products.
    """
    alphabet = string.ascii_uppercase + string.digits
    return 'SKU-' + ''.join(secrets.choice(alphabet) for _ in range(length))

def allowed_file(filename):
    """
    Check if a file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, upload_folder=None):
    """
    Save an uploaded file to the uploads directory.
    Returns the relative path to the saved file or None if failed.
    """
    if not upload_folder:
        upload_folder = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        return os.path.join('uploads', unique_filename)
    return None

def format_currency(value, currency='USD'):
    """
    Format a decimal value as currency.
    """
    try:
        value = Decimal(str(value))
        if currency == 'USD':
            return f"${value:,.2f}"
        return f"{value:,.2f} {currency}"
    except (InvalidOperation, ValueError):
        return "$0.00"

def calculate_discounted_price(original_price, discount_percentage):
    """
    Calculate the discounted price.
    """
    try:
        original_price = Decimal(str(original_price))
        discount_percentage = Decimal(str(discount_percentage))

        if discount_percentage <= 0:
            return original_price

        discount_amount = original_price * (discount_percentage / 100)
        return original_price - discount_amount
    except (InvalidOperation, ValueError):
        return original_price

def validate_email(email):
    """
    Validate an email address format.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def generate_order_number(user_id):
    """
    Generate a unique order number.
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"ORD-{timestamp}-{user_id}-{random_part}"

def get_paginated_url(endpoint, **kwargs):
    """
    Generate a paginated URL for a given endpoint.
    """
    kwargs['page'] = kwargs.get('page', 1)
    return url_for(endpoint, **kwargs)

def flash_errors(form, category='warning'):
    """
    Flash all errors for a form.
    """
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", category)

def commit_or_rollback(db_session, success_message=None, error_message="An error occurred. Please try again."):
    """
    Helper function to commit or rollback database changes.
    Returns True if commit was successful, False otherwise.
    """
    try:
        db_session.commit()
        if success_message:
            flash(success_message, 'success')
        return True
    except Exception as e:
        db_session.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        flash(error_message, 'danger')
        return False

def get_redirect_target():
    """
    Get the redirect target from the request or default to index.
    """
    for target in request.args.get('next'), request.referrer:
        if target and target != request.url and is_safe_url(target):
            return target
    return url_for('products.index')

def is_safe_url(target):
    """
    Check if a URL is safe for redirection.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def send_email(subject, recipients, text_body, html_body=None):
    """
    Send an email (placeholder for actual implementation).
    In a real application, this would integrate with an email service.
    """
    current_app.logger.info(f"Email would be sent to {recipients} with subject: {subject}")
    return True

def generate_slug(text, max_length=50):
    """
    Generate a URL slug from text.
    """
    # Convert to lowercase
    slug = text.lower()

    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)

    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Trim hyphens from start/end
    slug = slug.strip('-')

    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length]
        # Ensure we don't end with a hyphen after truncation
        if slug.endswith('-'):
            slug = slug[:-1]

    return slug

def generate_random_string(length=10):
    """
    Generate a random string of fixed length.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def calculate_cart_total(cart_items):
    """
    Calculate the total price of cart items.
    """
    total = Decimal('0.00')
    for item in cart_items:
        total += item.product.get_current_price() * item.quantity
    return total

def get_client_ip():
    """
    Get the client's IP address from the request.
    """
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def json_response(data=None, status=200, message=None):
    """
    Create a standardized JSON response.
    """
    response = {
        'success': 200 <= status < 300,
        'status': status,
    }

    if data is not None:
        response['data'] = data
    if message is not None:
        response['message'] = message

    return jsonify(response), status

def validate_phone_number(phone):
    """
    Validate a phone number format.
    """
    # Basic validation - allows for international numbers
    pattern = r'^\+?[0-9\s\-\(\)]{7,}$'
    return re.match(pattern, phone) is not None

def sanitize_html(text):
    """
    Basic HTML sanitization to prevent XSS.
    In a production app, use a proper HTML sanitizer library.
    """
    if not text:
        return text

    # Remove script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove onerror attributes
    text = re.sub(r'onerror\s*=', '', text, flags=re.IGNORECASE)
    # Remove javascript: links
    text = re.sub(r'href\s*=\s*["\']javascript:', 'href="#', text, flags=re.IGNORECASE)

    return text

def get_file_extension(filename):
    """
    Get the file extension from a filename.
    """
    return os.path.splitext(filename)[1].lower()

def delete_file(filepath):
    """
    Delete a file from the filesystem.
    """
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError as e:
            current_app.logger.error(f"Error deleting file {filepath}: {str(e)}")
    return False