from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src import db

carts_bp = Blueprint('carts', __name__, template_folder='../templates/carts')

@carts_bp.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    for item in cart.items:
        item.update_price()

    return render_template('carts/view.html',
                         cart=cart,
                         page_title="Your Shopping Cart")

@carts_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.is_in_stock():
        flash('This product is out of stock.', 'danger')
        return redirect(request.referrer or url_for('products.product_list'))

    if quantity > product.stock_quantity:
        flash(f'Only {product.stock_quantity} items available in stock.', 'warning')
        quantity = product.stock_quantity

    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    cart.add_item(product, quantity)
    flash(f'{product.name} has been added to your cart.', 'success')
    return redirect(request.referrer or url_for('products.product_list'))

@carts_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        cart = Cart.query.get(item.cart_id)
        cart.remove_item(item.product_id)
        flash('Item removed from your cart.', 'info')
    else:
        product = Product.query.get(item.product_id)
        if quantity > product.stock_quantity:
            flash(f'Only {product.stock_quantity} items available in stock.', 'warning')
            quantity = product.stock_quantity

        cart = Cart.query.get(item.cart_id)
        cart.update_item_quantity(item.product_id, quantity)
        flash('Cart updated successfully.', 'success')

    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    cart = Cart.query.get(item.cart_id)
    cart.remove_item(item.product_id)
    flash('Item removed from your cart.', 'success')
    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/cart/clear')
@login_required
def clear_cart():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if cart:
        cart.clear()
        flash('Your cart has been cleared.', 'success')

    return redirect(url_for('carts.view_cart'))