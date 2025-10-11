from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_env='development'):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from src.products.routes import products_bp
    from src.carts.routes import carts_bp
    from src.users.routes import users_bp
    from src.orders.routes import orders_bp
    from src.auth.routes import auth_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)

    return app