from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models.product import Product, Category, ProductImage
from ..models.cart import Cart, CartItem
from .. import db
from . import products_bp
from ..forms.product import ProductSearchForm, ReviewForm

@products_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PRODUCTS_PER_PAGE']

    # Get featured products
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(4).all()

    # Get new arrivals (products created in the last 30 days)
    new_arrivals = Product.query.filter(
        Product.is_active == True,
        Product.created_at >= datetime.utcnow() - timedelta(days=30)
    ).order_by(Product.created_at.desc()).limit(8).all()

    # Get best sellers (this would be more accurate with actual order data)
    best_sellers = Product.query.filter_by(is_active=True).order_by(Product.stock.asc()).limit(8).all()

    return render_template(
        'products/index.html',
        featured_products=featured_products,
        new_arrivals=new_arrivals,
        best_sellers=best_sellers
    )

@products_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = ProductSearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PRODUCTS_PER_PAGE']

    if form.validate_on_submit():
        search_query = form.search.data
        category_id = form.category.data

        query = Product.query.filter(Product.is_active == True)

        if search_query:
            query = query.filter(
                Product.name.ilike(f'%{search_query}%') |
                Product.description.ilike(f'%{search_query}%') |
                Product.sku.ilike(f'%{search_query}%')
            )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        products = query.order_by(Product.name).paginate(page=page, per_page=per_page)
    else:
        products = Product.query.filter_by(is_active=True).order_by(Product.name).paginate(page=page, per_page=per_page)

    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()

    return render_template(
        'products/search.html',
        products=products,
        form=form,
        categories=categories
    )

@products_bp.route('/category/<slug>')
def category(slug):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PRODUCTS_PER_PAGE']

    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(category_id=category.id, is_active=True).paginate(page=page, per_page=per_page)

    return render_template(
        'products/category.html',
        category=category,
        products=products
    )

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_active:
        flash('This product is not available.', 'warning')
        return redirect(url_for('products.index'))

    # Get related products (same category)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()

    # Get reviews for the product
    reviews = product.reviews.filter_by(is_approved=True).order_by(db.desc('created_at')).all()

    # Calculate average rating
    avg_rating = product.get_rating()

    # Initialize review form
    review_form = ReviewForm()

    return render_template(
        'products/detail.html',
        product=product,
        related_products=related_products,
        reviews=reviews,
        avg_rating=avg_rating,
        review_form=review_form
    )

@products_bp.route('/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    if form.validate_on_submit():
        # Check if user already reviewed this product
        existing_review = product.reviews.filter_by(user_id=current_user.id).first()

        if existing_review:
            flash('You have already reviewed this product.', 'warning')
        else:
            review = Review(
                user_id=current_user.id,
                product_id=product.id,
                rating=form.rating.data,
                comment=form.comment.data,
                is_approved=True  # In production, you might want to moderate reviews first
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')

    return redirect(url_for('products.product_detail', product_id=product_id))

@products_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_active or not product.is_in_stock():
        flash('This product is not available for purchase.', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        flash('Quantity must be at least 1', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

    if quantity > product.stock:
        flash(f'Only {product.stock} items available in stock', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

    # Get or create cart for the user
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    cart.add_item(product, quantity)
    flash(f'{product.name} has been added to your cart!', 'success')

    return redirect(url_for('products.product_detail', product_id=product_id))

from datetime import datetime, timedelta
from ..models.review import Review