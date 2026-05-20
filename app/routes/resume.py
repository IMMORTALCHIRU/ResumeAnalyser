from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.resume import Resume
from app.models.recommendation import Recommendation
from app.services.resume_parser import ResumeParserService
from app.services.recommendation_service import RecommendationService
from app.services.job_matching_service import JobMatchingService
from app.models.job import Job
import os
from functools import wraps

resume_bp = Blueprint('resume', __name__)


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_recruiter:
            flash('Access denied.', 'error')
            return redirect(url_for('recruiter.dashboard'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}


@resume_bp.route('/upload', methods=['GET', 'POST'])
@user_required
def upload():
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)

        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            parsed_data = ResumeParserService.parse_resume(filepath, filename)
            if parsed_data:
                resume = Resume.create(current_user.id, parsed_data)
                RecommendationService.generate_job_recommendations(current_user.id)
                flash('Resume uploaded and analysed successfully!', 'success')
                return redirect(url_for('resume.analysis', resume_id=resume.id))
            else:
                flash('Error parsing resume. Please try a different file.', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF or DOCX file.', 'error')
            return redirect(request.url)

    return render_template('resume/upload.html')


@resume_bp.route('/analysis/<resume_id>')
@user_required
def analysis(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume.user_id != current_user.id:
        flash('Resume not found', 'error')
        return redirect(url_for('resume.upload'))

    recommendations = Recommendation.get_latest_by_user(current_user.id)
    job_matches = JobMatchingService.get_jobs_for_resume(resume, top_n=6)
    return render_template('resume/analysis.html',
                           resume=resume,
                           recommendations=recommendations,
                           job_matches=job_matches)


@resume_bp.route('/history')
@user_required
def history():
    resumes = Resume.get_by_user(current_user.id)
    return render_template('resume/history.html', resumes=resumes)


@resume_bp.route('/job-recommendations')
@user_required
def job_recommendations():
    resume = Resume.get_latest_by_user(current_user.id)
    if not resume:
        flash('Please upload a resume first to get job recommendations.', 'info')
        return redirect(url_for('resume.upload'))
    job_matches = JobMatchingService.get_jobs_for_resume(resume, top_n=10)
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    return render_template('resume/job_recommendations.html',
                           resume=resume,
                           job_matches=job_matches,
                           recommendations=recommendations)


@resume_bp.route('/skill-gap')
@user_required
def skill_gap():
    resume = Resume.get_latest_by_user(current_user.id)
    if not resume:
        flash('Please upload a resume first.', 'info')
        return redirect(url_for('resume.upload'))
    return render_template('resume/skill_gap.html', resume=resume)
