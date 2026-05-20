from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import mongo
import re

auth_bp = Blueprint('auth', __name__)

HR_EMAIL = 'hr@portal.in'
HR_PASSWORD = 'Admin@123'
HR_NAME = 'HR Portal'


def _ensure_hr_user():
    """Seed the HR recruiter account if it doesn't exist."""
    existing = User.get_by_email(HR_EMAIL)
    if not existing:
        User.create(HR_NAME, HR_EMAIL, HR_PASSWORD, role='recruiter', company='HR Portal')


def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None


def validate_password(password):
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'
    return True, ''


# ------------------------------------------------------------------ #
#  User login / register
# ------------------------------------------------------------------ #

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_recruiter:
            return redirect(url_for('recruiter.dashboard'))
        return redirect(url_for('user_dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')

        user = User.get_by_email(email)
        if user and user.check_password(password):
            # Prevent recruiters from using user login
            if user.is_recruiter:
                flash('Please use the Recruiter Login portal.', 'error')
                return redirect(url_for('auth.recruiter_login'))
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user_dashboard.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters')
        if not validate_email(email):
            errors.append('Please enter a valid email address')
        if User.get_by_email(email):
            errors.append('An account with this email already exists')
        valid_password, password_error = validate_password(password)
        if not valid_password:
            errors.append(password_error)
        if password != confirm_password:
            errors.append('Passwords do not match')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', name=name, email=email)

        user = User.create(name, email, password, role='user')
        login_user(user)
        flash(f'Welcome to Smart Resume Analyser, {name}!', 'success')
        return redirect(url_for('user_dashboard.dashboard'))

    return render_template('auth/register.html')


# ------------------------------------------------------------------ #
#  Recruiter login
# ------------------------------------------------------------------ #

@auth_bp.route('/recruiter/login', methods=['GET', 'POST'])
def recruiter_login():
    if current_user.is_authenticated:
        if current_user.is_recruiter:
            return redirect(url_for('recruiter.dashboard'))
        return redirect(url_for('user_dashboard.dashboard'))

    _ensure_hr_user()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/recruiter_login.html')

        user = User.get_by_email(email)
        if user and user.is_recruiter and user.check_password(password):
            login_user(user)
            flash(f'Welcome, {user.name}! Recruiter portal loaded.', 'success')
            return redirect(url_for('recruiter.dashboard'))
        else:
            flash('Invalid recruiter credentials', 'error')

    return render_template('auth/recruiter_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    is_rec = current_user.is_recruiter
    logout_user()
    flash('You have been logged out successfully', 'info')
    if is_rec:
        return redirect(url_for('auth.recruiter_login'))
    return redirect(url_for('main.index'))
