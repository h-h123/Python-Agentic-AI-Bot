from functools import wraps
from flask import abort, redirect, url_for, flash, current_app
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('users.login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def login_required_with_redirect(f):
    """
    Decorator to require login and redirect to login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def cart_required(f):
    """
    Decorator to ensure user has an active cart.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from src.models.cart import Cart
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not cart:
            flash('Your cart is empty or inactive.', 'warning')
            return redirect(url_for('products.product_list'))
        return f(*args, **kwargs)
    return decorated_function

def validate_product_stock(f):
    """
    Decorator to validate product stock before processing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from src.models.product import Product
        product_id = kwargs.get('product_id') or request.args.get('product_id') or request.form.get('product_id')
        if product_id:
            product = Product.get_by_id(product_id)
            if not product.in_stock:
                flash('This product is out of stock.', 'danger')
                return redirect(url_for('products.product_detail', product_id=product_id))
        return f(*args, **kwargs)
    return decorated_function

def handle_exceptions(f):
    """
    Decorator to handle exceptions and provide user feedback.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(request.referrer or url_for('main.index'))
    return decorated_function

def cache_response(timeout=60):
    """
    Decorator to cache responses for a specified timeout.
    """
    from flask import make_response, request
    from werkzeug.contrib.cache import SimpleCache

    cache = SimpleCache()

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{request.path}?{request.query_string.decode('utf-8')}"
            response = cache.get(cache_key)

            if response is None:
                response = make_response(f(*args, **kwargs))
                cache.set(cache_key, response, timeout=timeout)

            return response
        return decorated_function
    return decorator

def rate_limit(limit=100, per=60):
    """
    Decorator to limit the rate of requests.
    """
    from flask import request
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["{}/{}second".format(limit, per)]
    )

    def decorator(f):
        return limiter.limit("{}/{}second".format(limit, per))(f)
    return decorator