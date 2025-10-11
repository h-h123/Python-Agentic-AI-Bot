import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from src.models.product import Product, ProductCategory

main_bp = Blueprint('main', __name__, template_folder='../templates/main')

@main_bp.route('/')
@main_bp.route('/home')
def index():
    page = 1
    per_page = current_app.config['ITEMS_PER_PAGE']

    featured_products = Product.query.filter_by(is_active=True)\
        .order_by(Product.created_at.desc())\
        .limit(8)\
        .all()

    categories = ProductCategory.query.filter_by(is_active=True, parent_id=None)\
        .limit(6)\
        .all()

    return render_template('main/index.html',
                         featured_products=featured_products,
                         categories=categories)

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title='About Us')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact Us')

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']

    if query:
        products = Product.query.filter(
            Product.is_active == True,
            Product.name.ilike(f'%{query}%')
        ).paginate(page=page, per_page=per_page)
    else:
        products = Product.query.filter_by(is_active=True)\
            .paginate(page=page, per_page=per_page)

    return render_template('main/search_results.html',
                         products=products,
                         query=query,
                         title=f'Search Results for "{query}"')

@main_bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html', title='Privacy Policy')

@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html', title='Terms of Service')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('orders.admin_order_list'))

    return render_template('main/dashboard.html', title='Dashboard')