from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from src.models.order import Order, OrderItem, OrderStatus
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.forms.order import CheckoutForm
from datetime import datetime
import secrets
import string

orders_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='../templates/orders')

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"ORD-{timestamp}-{random_part}"

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart or not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('carts.view_cart'))

    form = CheckoutForm()

    if form.validate_on_submit():
        try:
            # Create order
            order_number = generate_order_number()
            order = Order(
                user_id=current_user.id,
                order_number=order_number,
                shipping_address=form.shipping_address.data,
                billing_address=form.billing_address.data or form.shipping_address.data,
                payment_method=form.payment_method.data,
                shipping_method=form.shipping_method.data,
                notes=form.notes.data,
                tax_amount=0.00,
                shipping_cost=10.00 if form.shipping_method.data == 'express' else 5.00,
                total_amount=0.00
            )
            order.save()

            # Add order items and reduce stock
            for item in cart.items:
                product = item.product
                if not product.reduce_stock(item.quantity):
                    order.cancel()
                    flash(f'Not enough stock for {product.name}', 'danger')
                    return redirect(url_for('carts.view_cart'))

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.discounted_price
                )
                order_item.save()

            # Calculate totals
            order.calculate_totals()

            # Clear cart
            cart.clear()

            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('orders.order_detail', order_id=order.id))

        except Exception as e:
            current_app.logger.error(f"Error during checkout: {str(e)}")
            flash('An error occurred during checkout. Please try again.', 'danger')
            return redirect(url_for('carts.view_cart'))

    return render_template('orders/checkout.html',
                         title='Checkout',
                         form=form,
                         cart=cart)

@orders_bp.route('/')
@login_required
def order_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']

    orders = Order.query.filter_by(user_id=current_user.id)\
                       .order_by(Order.order_date.desc())\
                       .paginate(page=page, per_page=per_page)

    return render_template('orders/list.html',
                         orders=orders,
                         title='My Orders')

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.get_by_id(order_id)

    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this order', 'danger')
        return redirect(url_for('main.index'))

    return render_template('orders/detail.html',
                         order=order,
                         title=f'Order #{order.order_number}')

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.get_by_id(order_id)

    if order.user_id != current_user.id:
        flash('You do not have permission to cancel this order', 'danger')
        return redirect(url_for('orders.order_list'))

    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        flash('This order cannot be cancelled at this stage', 'warning')
        return redirect(url_for('orders.order_detail', order_id=order_id))

    try:
        order.cancel()
        flash('Your order has been cancelled successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error cancelling order: {str(e)}")
        flash('An error occurred while cancelling your order', 'danger')

    return redirect(url_for('orders.order_detail', order_id=order_id))

@orders_bp.route('/admin')
@login_required
def admin_order_list():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    status_filter = request.args.get('status')

    query = Order.query.order_by(Order.order_date.desc())

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.paginate(page=page, per_page=per_page)

    return render_template('orders/admin_list.html',
                         orders=orders,
                         title='All Orders')

@orders_bp.route('/admin/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash('You do not have permission to update order status', 'danger')
        return redirect(url_for('main.index'))

    order = Order.get_by_id(order_id)
    new_status = request.form.get('status')

    try:
        order.update_status(new_status)
        flash('Order status updated successfully', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        current_app.logger.error(f"Error updating order status: {str(e)}")
        flash('An error occurred while updating order status', 'danger')

    return redirect(url_for('orders.admin_order_detail', order_id=order_id))

@orders_bp.route('/admin/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    if not current_user.is_admin:
        flash('You do not have permission to view this order', 'danger')
        return redirect(url_for('main.index'))

    order = Order.get_by_id(order_id)
    return render_template('orders/admin_detail.html',
                         order=order,
                         title=f'Order #{order.order_number}')