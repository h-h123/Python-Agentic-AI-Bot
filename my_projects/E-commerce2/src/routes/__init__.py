from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import products, carts, users, orders, auth

__all__ = ['main_bp']