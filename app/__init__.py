from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

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

    return app