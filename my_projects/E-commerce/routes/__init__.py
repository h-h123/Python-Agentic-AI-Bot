from flask import Blueprint

# Create blueprints for each module
products_bp = Blueprint('products', __name__)
carts_bp = Blueprint('carts', __name__)
users_bp = Blueprint('users', __name__)
orders_bp = Blueprint('orders', __name__)
auth_bp = Blueprint('auth', __name__)

# Import routes to register them with the blueprints
from . import products, carts, users, orders, auth

__all__ = ['products_bp', 'carts_bp', 'users_bp', 'orders_bp', 'auth_bp']