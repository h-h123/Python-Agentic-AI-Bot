from flask import Blueprint

# Create blueprints for each module
products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates/products')
carts_bp = Blueprint('carts', __name__, url_prefix='/cart', template_folder='../templates/carts')
users_bp = Blueprint('users', __name__, url_prefix='/users', template_folder='../templates/users')
orders_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='../templates/orders')
main_bp = Blueprint('main', __name__, template_folder='../templates/main')

# Import routes to register them with the blueprints
from . import products, carts, users, orders, main