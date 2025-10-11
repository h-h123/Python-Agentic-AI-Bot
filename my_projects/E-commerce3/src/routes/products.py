from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from src.models.product import Product, ProductCategory
from src.models.cart import Cart
from src.extensions import db, photos
from src.forms.product import ProductForm, ProductCategoryForm
from werkzeug.utils import secure_filename
import os

products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates/products')

@products_bp.route('/')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    category_id = request.args.get('category_id', type=int)

    query = Product.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    categories = ProductCategory.query.filter_by(is_active=True).all()

    return render_template('products/list.html',
                         products=products,
                         categories=categories,
                         current_category=category_id)

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.get_by_id(product_id)
    return render_template('products/detail.html', product=product)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in ProductCategory.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        try:
            filename = None
            if form.image.data:
                filename = photos.save(form.image.data)
            else:
                filename = 'default-product.jpg'

            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data,
                category_id=form.category.data,
                sku=form.sku.data,
                discount=form.discount.data,
                image=filename
            )
            product.save()
            flash('Product added successfully!', 'success')
            return redirect(url_for('products.product_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')

    return render_template('products/add.html', title='Add Product', form=form)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    product = Product.get_by_id(product_id)
    form = ProductForm(obj=product)
    form.category.choices = [(c.id, c.name) for c in ProductCategory.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        try:
            if form.image.data:
                if product.image and product.image != 'default-product.jpg':
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], product.image))
                filename = photos.save(form.image.data)
                product.image = filename

            product.update(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data,
                category_id=form.category.data,
                sku=form.sku.data,
                discount=form.discount.data
            )
            flash('Product updated successfully!', 'success')
            return redirect(url_for('products.product_detail', product_id=product.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')

    return render_template('products/edit.html', title='Edit Product', form=form, product=product)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    product = Product.get_by_id(product_id)
    try:
        if product.image and product.image != 'default-product.jpg':
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], product.image))
        product.delete()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')

    return redirect(url_for('products.product_list'))

@products_bp.route('/categories')
def category_list():
    categories = ProductCategory.query.filter_by(is_active=True).all()
    return render_template('products/categories.html', categories=categories)

@products_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    form = ProductCategoryForm()
    form.parent.choices = [(0, 'None')] + [(c.id, c.name) for c in ProductCategory.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        try:
            category = ProductCategory(
                name=form.name.data,
                description=form.description.data,
                parent_id=form.parent.data if form.parent.data != 0 else None
            )
            category.save()
            flash('Category added successfully!', 'success')
            return redirect(url_for('products.category_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding category: {str(e)}', 'danger')

    return render_template('products/add_category.html', title='Add Category', form=form)

@products_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    category = ProductCategory.get_by_id(category_id)
    form = ProductCategoryForm(obj=category)
    form.parent.choices = [(0, 'None')] + [(c.id, c.name) for c in ProductCategory.query.filter(ProductCategory.id != category_id, ProductCategory.is_active == True).all()]

    if form.validate_on_submit():
        try:
            category.update(
                name=form.name.data,
                description=form.description.data,
                parent_id=form.parent.data if form.parent.data != 0 else None
            )
            flash('Category updated successfully!', 'success')
            return redirect(url_for('products.category_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'danger')

    return render_template('products/edit_category.html', title='Edit Category', form=form, category=category)

@products_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    category = ProductCategory.get_by_id(category_id)
    try:
        category.delete()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('products.category_list'))

@products_bp.route('/<int:product_id>/add_to_cart', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.get_by_id(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.in_stock:
        flash('This product is out of stock', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

    if quantity > product.stock:
        flash(f'Not enough stock. Only {product.stock} available', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    cart.add_item(product_id, quantity)
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))