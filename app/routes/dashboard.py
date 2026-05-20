from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.resume import Resume
from app.models.recommendation import Recommendation
from app.models.job import Job
from app.services.recommendation_service import RecommendationService
from app.services.job_matching_service import JobMatchingService
from functools import wraps

dashboard_bp = Blueprint('user_dashboard', __name__)


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_recruiter:
            flash('Access denied. Please use the recruiter portal.', 'error')
            return redirect(url_for('recruiter.dashboard'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/')
@user_required
def dashboard():
    resume = Resume.get_latest_by_user(current_user.id)
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    all_resumes = Resume.get_by_user(current_user.id)
    job_matches = []
    if resume:
        job_matches = JobMatchingService.get_jobs_for_resume(resume, top_n=5)
    return render_template('user/dashboard.html',
                           resume=resume,
                           recommendations=recommendations,
                           all_resumes=all_resumes,
                           job_matches=job_matches)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@user_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        preferred_roles = request.form.getlist('preferred_roles')
        profile_summary = request.form.get('profile_summary', '').strip()

        if name and len(name) >= 2:
            current_user.update_profile({
                'name': name,
                'phone': phone,
                'preferred_roles': preferred_roles,
                'profile_summary': profile_summary,
            })
            flash('Profile updated successfully!', 'success')
        else:
            flash('Name must be at least 2 characters', 'error')
        return redirect(url_for('user_dashboard.profile'))

    resume = Resume.get_latest_by_user(current_user.id)
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    return render_template('user/profile.html',
                           resume=resume,
                           recommendations=recommendations)
