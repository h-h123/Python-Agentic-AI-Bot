from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from src.models.cart import Cart, CartItem
from src.models.product import Product

carts_bp = Blueprint('carts', __name__, url_prefix='/cart', template_folder='../templates/carts')

@carts_bp.route('/')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    return render_template('carts/view.html', cart=cart)

@carts_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.get_by_id(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.in_stock:
        flash('This product is out of stock', 'danger')
        return redirect(request.referrer or url_for('products.product_list'))

    if quantity > product.stock:
        flash(f'Not enough stock. Only {product.stock} available', 'danger')
        return redirect(request.referrer or url_for('products.product_list'))

    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        cart.save()

    cart.add_item(product_id, quantity)
    flash('Product added to cart successfully!', 'success')
    return redirect(request.referrer or url_for('products.product_list'))

@carts_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.get_by_id(item_id)
    if not cart_item or cart_item.cart.user_id != current_user.id:
        flash('Item not found in your cart', 'danger')
        return redirect(url_for('carts.view_cart'))

    new_quantity = int(request.form.get('quantity', 1))
    product = cart_item.product

    if new_quantity > product.stock:
        flash(f'Not enough stock. Only {product.stock} available', 'danger')
        return redirect(url_for('carts.view_cart'))

    cart_item.cart.update_item_quantity(product.id, new_quantity)
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.get_by_id(item_id)
    if not cart_item or cart_item.cart.user_id != current_user.id:
        flash('Item not found in your cart', 'danger')
        return redirect(url_for('carts.view_cart'))

    cart_item.cart.remove_item(cart_item.product_id)
    flash('Item removed from cart successfully!', 'success')
    return redirect(url_for('carts.view_cart'))

@carts_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if cart:
        cart.clear()
        flash('Your cart has been cleared', 'success')
    return redirect(url_for('carts.view_cart'))