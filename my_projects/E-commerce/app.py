import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Blueprints
from products.views import products_bp
from carts.views import carts_bp
from users.views import users_bp
from orders.views import orders_bp
from auth.views import auth_bp

app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(carts_bp, url_prefix='/cart')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)