from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

load_dotenv()

mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smart_resume_analyser')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.resume import resume_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.recruiter import recruiter_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    app.register_blueprint(api_bp, url_prefix='/api')

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Jinja helper to fetch a user's display name by DB id (avoid relying on resume-parsed names)
    def _get_user_display_name(user_id):
        try:
            if not user_id:
                return 'Unknown Candidate'
            u = User.get_by_id(user_id)
            return u.get_display_name() if u else 'Unknown Candidate'
        except Exception:
            return 'Unknown Candidate'

    app.jinja_env.globals['get_user_display_name'] = _get_user_display_name

    # Jinja filter: format datetime to IST
    def format_datetime_ist(value, fmt: str = "%d %b %Y, %I:%M %p %Z", default: str = 'Unknown date'):
        """Format a datetime (or ISO string) into IST timezone for templates.

        - If `value` is falsy, returns `default`.
        - If `value` is a naive datetime it's assumed to be UTC and converted to IST.
        - If `value` is a string, attempt ISO parsing; otherwise return the raw string.
        """
        if not value:
            return default
        try:
            # Parse strings if necessary
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value)
                except Exception:
                    return value
            else:
                dt = value

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            ist = dt.astimezone(ZoneInfo("Asia/Kolkata"))
            return ist.strftime(fmt)
        except Exception as e:
            app.logger.exception("Failed to format datetime to IST: %s", e)
            return default

    app.jinja_env.filters['format_datetime_ist'] = format_datetime_ist

    return app