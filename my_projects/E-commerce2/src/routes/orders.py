from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from src.models.order import Order, OrderItem, OrderStatus
from src.models.cart import Cart
from src.models.product import Product
from src import db
import uuid
from datetime import datetime

orders_bp = Blueprint('orders', __name__, template_folder='../templates/orders')

@orders_bp.route('/orders')
@login_required
def order_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ORDERS_PER_PAGE', 10)

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('orders/list.html',
                         orders=orders,
                         page_title="Your Orders")

@orders_bp.route('/orders/<order_number>')
@login_required
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('orders/detail.html',
                         order=order,
                         page_title=f"Order #{order_number}")

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not cart or not cart.items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('carts.view_cart'))

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        billing_address = request.form.get('billing_address', shipping_address)
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')

        if not shipping_address or not payment_method:
            flash('Please provide shipping address and payment method.', 'danger')
            return redirect(url_for('orders.checkout'))

        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%y%m%d')}"

        order = Order(
            user_id=current_user.id,
            order_number=order_number,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            notes=notes,
            status=OrderStatus.PENDING
        )

        try:
            db.session.add(order)
            db.session.flush()

            for item in cart.items:
                product = Product.query.get(item.product_id)
                if not product.decrease_stock(item.quantity):
                    db.session.rollback()
                    flash(f'Not enough stock for {product.name}', 'danger')
                    return redirect(url_for('orders.checkout'))

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                db.session.add(order_item)

            order.calculate_total()
            cart.clear()
            db.session.commit()

            flash(f'Your order #{order_number} has been placed successfully!', 'success')
            return redirect(url_for('orders.order_detail', order_number=order_number))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating order: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'danger')
            return redirect(url_for('orders.checkout'))

    return render_template('orders/checkout.html',
                         cart=cart,
                         page_title="Checkout")

@orders_bp.route('/orders/<order_number>/cancel', methods=['POST'])
@login_required
def cancel_order(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()

    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        flash('This order cannot be cancelled at this stage.', 'warning')
        return redirect(url_for('orders.order_detail', order_number=order_number))

    try:
        for item in order.items:
            product = Product.query.get(item.product_id)
            product.increase_stock(item.quantity)

        order.cancel()
        flash('Your order has been cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling your order.', 'danger')

    return redirect(url_for('orders.order_detail', order_number=order_number))