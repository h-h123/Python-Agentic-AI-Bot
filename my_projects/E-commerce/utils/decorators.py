from functools import wraps
from flask import abort, redirect, url_for, flash, current_app, request
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_with_redirect(f):
    """
    Decorator to ensure user is logged in, with custom redirect handling.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator factory to restrict access to specific user roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'info')
                return redirect(url_for('auth.login', next=request.url))

            if not any(getattr(current_user, role, False) for role in roles):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('products.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cart_required(f):
    """
    Decorator to ensure user has items in their cart.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access your cart.', 'info')
            return redirect(url_for('auth.login', next=request.url))

        if not hasattr(current_user, 'cart') or not current_user.cart or not current_user.cart.items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def handle_errors(f):
    """
    Decorator to catch and handle exceptions in route functions.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(request.referrer or url_for('products.index'))
    return decorated_function

def json_required(f):
    """
    Decorator to ensure request contains JSON data.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return {'error': 'Request must be JSON'}, 400
        return f(*args, **kwargs)
    return decorated_function

def validate_form(f):
    """
    Decorator to validate form submission and flash errors.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        form = kwargs.get('form') or args[-1] if args else None
        if form and not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{getattr(form, field).label.text}: {error}", 'danger')
            return redirect(request.referrer or url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def cache_response(timeout=60):
    """
    Decorator to cache route responses.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"view://{request.path}"
            response = current_app.cache.get(cache_key)

            if response is None:
                response = f(*args, **kwargs)
                current_app.cache.set(cache_key, response, timeout=timeout)
            return response
        return decorated_function
    return decorator