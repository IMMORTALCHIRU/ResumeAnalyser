from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models.job import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    active_jobs = Job.get_all(active_only=True)[:6]
    return render_template('index.html', active_jobs=active_jobs)
