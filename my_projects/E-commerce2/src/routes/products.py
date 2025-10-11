from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from src.models.product import Product, Category
from src.models.cart import Cart
from src import db

products_bp = Blueprint('products', __name__, template_folder='../templates/products')

@products_bp.route('/')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 8)
    category_slug = request.args.get('category')

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug, is_active=True).first_or_404()
        query = query.filter_by(category_id=category.id)
        products = query.paginate(page=page, per_page=per_page)
        return render_template('products/list.html',
                             products=products,
                             category=category,
                             page_title=f"Products in {category.name}")

    search_query = request.args.get('q')
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
        products = query.paginate(page=page, per_page=per_page)
        return render_template('products/list.html',
                             products=products,
                             search_query=search_query,
                             page_title=f"Search results for '{search_query}'")

    products = query.paginate(page=page, per_page=per_page)
    return render_template('products/list.html',
                         products=products,
                         page_title="All Products")

@products_bp.route('/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template('products/detail.html',
                         product=product,
                         page_title=product.name)

@products_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.is_in_stock():
        flash('This product is out of stock.', 'danger')
        return redirect(url_for('products.product_detail', slug=product.slug))

    if quantity > product.stock_quantity:
        flash(f'Only {product.stock_quantity} items available in stock.', 'warning')
        quantity = product.stock_quantity

    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    cart.add_item(product, quantity)
    flash(f'{product.name} has been added to your cart.', 'success')
    return redirect(url_for('products.product_detail', slug=product.slug))

@products_bp.route('/categories')
def category_list():
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    return render_template('products/categories.html',
                         categories=categories,
                         page_title="Product Categories")

@products_bp.route('/category/<slug>')
def category_detail(slug):
    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 8)

    products = Product.query.filter_by(
        category_id=category.id,
        is_active=True
    ).paginate(page=page, per_page=per_page)

    return render_template('products/list.html',
                         products=products,
                         category=category,
                         page_title=f"Products in {category.name}")