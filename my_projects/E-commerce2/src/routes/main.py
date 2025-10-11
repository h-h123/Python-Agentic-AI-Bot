import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, render_template, current_app
from src.models.product import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True, is_featured=True).limit(8).all()
    categories = Category.query.filter_by(is_active=True).limit(6).all()

    return render_template('main/index.html',
                         featured_products=featured_products,
                         categories=categories,
                         page_title="Home")

@main_bp.route('/about')
def about():
    return render_template('main/about.html', page_title="About Us")

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html', page_title="Contact Us")

@main_bp.route('/faq')
def faq():
    return render_template('main/faq.html', page_title="Frequently Asked Questions")

@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html', page_title="Terms and Conditions")

@main_bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html', page_title="Privacy Policy")