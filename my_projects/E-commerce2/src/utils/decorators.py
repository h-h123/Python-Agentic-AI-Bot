from functools import wraps
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()

            if not any(getattr(current_user, role, False) for role in roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cart_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from src.models.cart import Cart
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not cart:
            flash('You need to have an active cart for this action.', 'warning')
            return redirect(url_for('products.product_list'))
        return f(*args, **kwargs)
    return decorated_function

def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(request.referrer or url_for('main.index'))
    return decorated_function

def validate_form(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        form = kwargs.get('form')
        if form and not form.validate_on_submit():
            return render_template(f'{f.__module__.split(".")[-1]}/{f.__name__}.html', form=form)
        return f(*args, **kwargs)
    return decorated_function

def ajax_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_xhr:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function

def login_required_with_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def product_exists(f):
    @wraps(f)
    def decorated_function(product_id, *args, **kwargs):
        from src.models.product import Product
        product = Product.query.get(product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products.product_list'))
        return f(product_id, *args, **kwargs)
    return decorated_function

def order_exists(f):
    @wraps(f)
    def decorated_function(order_number, *args, **kwargs):
        from src.models.order import Order
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('orders.order_list'))
        return f(order_number, *args, **kwargs)
    return decorated_function

def user_exists(f):
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        from src.models.user import User
        user = User.query.get(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('main.index'))
        return f(user_id, *args, **kwargs)
    return decorated_function