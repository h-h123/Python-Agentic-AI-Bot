from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.cart import Cart, CartItem
from ..models.user import User, Address
from .. import db
from . import orders_bp
from ..forms.order import CheckoutForm

@orders_bp.route('/')
@login_required
def list_orders():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ORDERS_PER_PAGE']

    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(db.desc(Order.created_at))\
        .paginate(page=page, per_page=per_page)

    return render_template('orders/list.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to view this order', 'danger')
        return redirect(url_for('orders.list_orders'))

    return render_template('orders/detail.html', order=order)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart or not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products.index'))

    form = CheckoutForm()

    # Get user addresses
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    form.shipping_address.choices = [(addr.id, f"{addr.street}, {addr.city}") for addr in addresses]
    form.billing_address.choices = [(addr.id, f"{addr.street}, {addr.city}") for addr in addresses]

    if form.validate_on_submit():
        try:
            # Create new order
            order = Order(
                user_id=current_user.id,
                order_number=f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}",
                status=OrderStatus.PENDING,
                total_amount=cart.get_total_price(),
                shipping_address_id=form.shipping_address.data,
                billing_address_id=form.billing_address.data,
                payment_method=form.payment_method.data,
                notes=form.notes.data
            )
            db.session.add(order)

            # Create order items from cart items
            for item in cart.items:
                order_item = OrderItem.create_from_cart_item(item, order.id)
                db.session.add(order_item)

                # Update product stock
                product = item.product
                product.stock -= item.quantity

            db.session.commit()

            # Clear the cart
            cart.clear()

            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('orders.order_detail', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating order: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'danger')

    return render_template('orders/checkout.html', form=form, cart=cart)

@orders_bp.route('/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash('You are not authorized to cancel this order', 'danger')
        return redirect(url_for('orders.order_detail', order_id=order_id))

    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        flash('This order cannot be cancelled at this stage', 'warning')
        return redirect(url_for('orders.order_detail', order_id=order_id))

    try:
        # Restore product stock
        for item in order.items:
            product = item.product
            product.stock += item.quantity

        order.mark_as_cancelled()
        flash('Your order has been cancelled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling order: {str(e)}")
        flash('An error occurred while cancelling your order. Please try again.', 'danger')

    return redirect(url_for('orders.order_detail', order_id=order_id))

@orders_bp.route('/status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    try:
        order.update_status(new_status)
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'new_status': order.status.value
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@orders_bp.route('/payment-status/<int:order_id>', methods=['POST'])
@login_required
def update_payment_status(order_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('payment_status')

    try:
        order.update_payment_status(new_status)
        return jsonify({
            'success': True,
            'message': 'Payment status updated successfully',
            'new_status': order.payment_status.value
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@orders_bp.route('/invoice/<int:order_id>')
@login_required
def order_invoice(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to view this invoice', 'danger')
        return redirect(url_for('orders.list_orders'))

    return render_template('orders/invoice.html', order=order)