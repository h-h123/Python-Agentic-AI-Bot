from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models.user import User, Address, Review
from ..models.product import Product
from .. import db
from . import users_bp
from ..forms.user import ProfileForm, AddressForm, ChangePasswordForm

@users_bp.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    return render_template('users/profile.html', user=user)

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone_number = form.phone_number.data

        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('users.profile'))

    return render_template('users/edit_profile.html', form=form, user=user)

@users_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('users.change_password'))

        if form.new_password.data != form.confirm_password.data:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('users.change_password'))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('users.profile'))

    return render_template('users/change_password.html', form=form)

@users_bp.route('/addresses')
@login_required
def list_addresses():
    addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc()).all()
    return render_template('users/addresses.html', addresses=addresses)

@users_bp.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    form = AddressForm()

    if form.validate_on_submit():
        # If this is the first address, make it default
        is_default = not Address.query.filter_by(user_id=current_user.id).first()

        address = Address(
            user_id=current_user.id,
            street=form.street.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            is_default=is_default
        )

        db.session.add(address)

        # If this is the first address, update all others to not be default
        if is_default:
            Address.query.filter(
                Address.user_id == current_user.id,
                Address.id != address.id
            ).update({'is_default': False})

        db.session.commit()
        flash('Address added successfully!', 'success')
        return redirect(url_for('users.list_addresses'))

    return render_template('users/add_address.html', form=form)

@users_bp.route('/addresses/<int:address_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    address = Address.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    form = AddressForm(obj=address)

    if form.validate_on_submit():
        address.street = form.street.data
        address.city = form.city.data
        address.state = form.state.data
        address.postal_code = form.postal_code.data
        address.country = form.country.data

        if form.is_default.data:
            # Update all other addresses to not be default
            Address.query.filter(
                Address.user_id == current_user.id,
                Address.id != address.id
            ).update({'is_default': False})
            address.is_default = True

        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('users.list_addresses'))

    return render_template('users/edit_address.html', form=form, address=address)

@users_bp.route('/addresses/<int:address_id>/delete', methods=['POST'])
@login_required
def delete_address(address_id):
    address = Address.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    if address.is_default:
        flash('Cannot delete default address. Set another address as default first.', 'danger')
        return redirect(url_for('users.list_addresses'))

    db.session.delete(address)
    db.session.commit()
    flash('Address deleted successfully!', 'success')
    return redirect(url_for('users.list_addresses'))

@users_bp.route('/addresses/<int:address_id>/set-default', methods=['POST'])
@login_required
def set_default_address(address_id):
    address = Address.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()

    # Update all addresses to not be default
    Address.query.filter(
        Address.user_id == current_user.id
    ).update({'is_default': False})

    address.is_default = True
    db.session.commit()

    flash('Default address updated successfully!', 'success')
    return redirect(url_for('users.list_addresses'))

@users_bp.route('/reviews')
@login_required
def list_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('REVIEWS_PER_PAGE', 10)

    reviews = Review.query.filter_by(user_id=current_user.id)\
        .order_by(db.desc(Review.created_at))\
        .paginate(page=page, per_page=per_page)

    return render_template('users/reviews.html', reviews=reviews)

@users_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('users.list_reviews'))