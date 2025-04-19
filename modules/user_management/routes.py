from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User
from . import user_management_bp
from .forms import RegisterForm, LoginForm, EditProfileForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_management_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('user_management.login'))
    return render_template('user_management/register.html', form=form)

@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('user_management.profile'))
        flash('Invalid username or password.', 'danger')
    return render_template('user_management/login.html', form=form)

@user_management_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('user_management.login'))

@user_management_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('user_management.profile'))
    return render_template('user_management/profile.html', form=form)

@user_management_bp.route('/list')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('user_management.profile'))
    users = User.query.all()
    return render_template('user_management/user_list.html', users=users)
