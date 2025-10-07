"""Utility functions and helpers for the e-commerce application."""

from flask import current_app, flash, redirect, url_for, request
from functools import wraps
from datetime import datetime, timedelta
import os
import secrets
import string
import re
from werkzeug.utils import secure_filename
from ..models import db

def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.login_manager._login_disabled and \
           not getattr(current_app.login_manager._user_callback(), 'is_admin', False):
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_sku(length=10):
    """Generate a random SKU for products."""
    alphabet = string.ascii_uppercase + string.digits
    return 'SKU-' + ''.join(secrets.choice(alphabet) for _ in range(length))

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, upload_folder=None):
    """Save an uploaded file to the uploads directory."""
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

def format_currency(value):
    """Format a decimal value as currency."""
    return f"${value:,.2f}"

def calculate_discounted_price(original_price, discount_percentage):
    """Calculate the discounted price."""
    if discount_percentage <= 0:
        return original_price
    discount_amount = original_price * (discount_percentage / 100)
    return original_price - discount_amount

def validate_email(email):
    """Validate an email address format."""
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

def generate_order_number(user_id):
    """Generate a unique order number."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"ORD-{timestamp}-{user_id}"

def get_paginated_url(endpoint, **kwargs):
    """Generate a paginated URL for a given endpoint."""
    kwargs['page'] = kwargs.get('page', 1)
    return url_for(endpoint, **kwargs)

def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", category)

def commit_or_rollback(db_session, success_message=None, error_message="An error occurred. Please try again."):
    """Helper function to commit or rollback database changes."""
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
    """Get the redirect target from the request or default to index."""
    for target in request.args.get('next'), request.referrer:
        if target and target != request.url and is_safe_url(target):
            return target
    return url_for('products.index')

def is_safe_url(target):
    """Check if a URL is safe for redirection."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def send_email(subject, recipients, text_body, html_body=None):
    """Send an email (placeholder for actual implementation)."""
    current_app.logger.info(f"Email would be sent to {recipients} with subject: {subject}")
    return True

from urllib.parse import urlparse, urljoin