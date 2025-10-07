from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models.cart import Cart, CartItem
from ..models.product import Product
from .. import db
from . import carts_bp

@carts_bp.route('/')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    return render_template('cart/view.html', cart=cart)

@carts_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_active or not product.is_in_stock():
        flash('This product is not available for purchase.', 'danger')
        return redirect(request.referrer or url_for('products.index'))

    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        flash('Quantity must be at least 1', 'danger')
        return redirect(request.referrer or url_for('products.index'))

    if quantity > product.stock:
        flash(f'Only {product.stock} items available in stock', 'danger')
        return redirect(request.referrer or url_for('products.index'))

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    cart.add_item(product, quantity)
    flash(f'{product.name} has been added to your cart!', 'success')

    return redirect(request.referrer or url_for('products.index'))

@carts_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.get_or_404(item_id)

    if cart_item.cart.user_id != current_user.id:
        flash('You are not authorized to update this item', 'danger')
        return redirect(url_for('carts.view_cart'))

    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        cart_item.cart.remove_item(cart_item.product)
        flash(f'{cart_item.product.name} has been removed from your cart', 'info')
    else:
        if quantity > cart_item.product.stock:
            flash(f'Only {cart_item.product.stock} items available in stock', 'danger')
            return redirect(url_for('carts.view_cart'))

        cart_item.cart.update_item_quantity(cart_item.product, quantity)
        flash(f'Cart updated successfully', 'success')

    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)

    if cart_item.cart.user_id != current_user.id:
        flash('You are not authorized to remove this item', 'danger')
        return redirect(url_for('carts.view_cart'))

    cart_item.cart.remove_item(cart_item.product)
    flash(f'{cart_item.product.name} has been removed from your cart', 'success')

    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/clear')
@login_required
def clear_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if cart:
        cart.clear()
        flash('Your cart has been cleared', 'success')

    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/checkout')
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart or not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products.index'))

    return render_template('cart/checkout.html', cart=cart)