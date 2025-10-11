"""Utility functions and helpers for the e-commerce application."""

from flask import current_app, jsonify
from functools import wraps
from werkzeug.utils import secure_filename
import os
import secrets
import string
from datetime import datetime, timedelta
from PIL import Image
import bleach

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_random_string(length=8):
    """Generate a random string of fixed length."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_html(input_string):
    """Sanitize HTML input to prevent XSS attacks."""
    if not input_string:
        return ""
    return bleach.clean(input_string)

def resize_image(input_path, output_path, size=(300, 300)):
    """Resize an image while maintaining aspect ratio."""
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size)
            img.save(output_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Error resizing image: {str(e)}")
        return False

def save_uploaded_file(file, upload_folder, filename=None):
    """Save an uploaded file to the specified folder."""
    if not file:
        return None

    if not filename:
        filename = secure_filename(file.filename)
    else:
        filename = secure_filename(filename)

    if not allowed_file(filename):
        return None

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Resize if it's an image
    if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}:
        resize_image(filepath, filepath)

    return filename

def delete_file(filepath):
    """Delete a file from the filesystem."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {str(e)}")
    return False

def admin_required(f):
    """Decorator to check if the current user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or not current_user.is_admin:
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def json_response(data=None, status=200, message=None):
    """Create a standardized JSON response."""
    response = {
        'status': 'success' if status < 400 else 'error',
        'code': status
    }

    if data is not None:
        response['data'] = data

    if message is not None:
        response['message'] = message

    return jsonify(response), status

def generate_pagination_metadata(pagination):
    """Generate pagination metadata for API responses."""
    return {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total_pages': pagination.pages,
        'total_items': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def format_currency(value):
    """Format a numeric value as currency."""
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "$0.00"

def calculate_discounted_price(price, discount):
    """Calculate the discounted price."""
    try:
        price = float(price)
        discount = float(discount)
        return price * (1 - (discount / 100)) if discount > 0 else price
    except (ValueError, TypeError):
        return price

def generate_reset_token():
    """Generate a password reset token."""
    return secrets.token_urlsafe(32)

def validate_reset_token(token, expiration):
    """Validate a password reset token."""
    if not token or not expiration:
        return False
    return datetime.utcnow() < expiration

def get_upload_path(filename=None):
    """Get the full path to the uploads directory."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if filename:
        return os.path.join(upload_folder, filename)
    return upload_folder

def log_activity(user_id, action, details=None):
    """Log user activity (placeholder for actual implementation)."""
    current_app.logger.info(f"User {user_id} performed action: {action}. Details: {details}")