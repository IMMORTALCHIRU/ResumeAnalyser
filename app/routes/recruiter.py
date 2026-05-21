from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.resume import Resume
from app.models.user import User
from app.models.job import Job
from app.services.job_matching_service import JobMatchingService
from functools import wraps
from bson import ObjectId

recruiter_bp = Blueprint('recruiter', __name__)


def recruiter_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.recruiter_login'))
        if not current_user.is_recruiter:
            flash('Access denied. Recruiter account required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------------ #
#  Dashboard
# ------------------------------------------------------------------ #

@recruiter_bp.route('/dashboard')
@recruiter_required
def dashboard():
    all_resumes = Resume.get_all()
    all_users = User.get_all_applicants()
    all_jobs = Job.get_by_recruiter(current_user.id)
    total_jobs = Job.get_all(active_only=False)

    # Stats
    stats = {
        'total_applicants': len(all_users),
        'total_resumes': len(all_resumes),
        'total_jobs': len(total_jobs),
        'active_jobs': sum(1 for j in total_jobs if j.is_active),
    }

    # Field distribution for chart
    field_data = Resume.count_by_field()

    # Top applicants (sorted by score)
    top_applicants = sorted(all_resumes, key=lambda r: r.resume_score, reverse=True)[:5]
    # Ensure display names and emails are attached from the DB (avoid relying on parsed resume)
    for resume in top_applicants:
        user = User.get_by_id(resume.user_id)
        if user:
            resume.user_name = user.get_display_name()
            resume.user_email = user.email
        else:
            resume.user_name = 'Unknown Candidate'
            resume.user_email = ''
    # Recent jobs (limit)
    recent_jobs = all_jobs[:6]

    # Map variables to template names used in recruiter/dashboard.html
    return render_template('recruiter/dashboard.html',
                           total_applicants=stats['total_applicants'],
                           total_resumes=stats['total_resumes'],
                           total_jobs=stats['total_jobs'],
                           active_jobs=stats['active_jobs'],
                           top_resumes=top_applicants,
                           recent_jobs=recent_jobs,
                           recent_jobs_all=all_jobs,
                           field_distribution=field_data)


# ------------------------------------------------------------------ #
#  Applicants
# ------------------------------------------------------------------ #

@recruiter_bp.route('/applicants')
@recruiter_required
def applicants():
    # Filtering
    field_filter = request.args.get('field', '')
    level_filter = request.args.get('level', '')
    min_score = request.args.get('min_score', 0, type=int)

    all_resumes = Resume.get_all()

    if field_filter:
        all_resumes = [r for r in all_resumes if r.predicted_field == field_filter]
    if level_filter:
        all_resumes = [r for r in all_resumes if r.candidate_level == level_filter]
    if min_score:
        all_resumes = [r for r in all_resumes if r.resume_score >= min_score]

    # Attach user info to resume objects
    for resume in all_resumes:
        user = User.get_by_id(resume.user_id)
        if user:
            resume.user_name = user.get_display_name()
            resume.user_email = user.email
        else:
            resume.user_name = 'Unknown Candidate'
            resume.user_email = ''

    fields = ['Data Science', 'Web Development', 'Frontend Development',
              'Backend Development', 'Mobile Development', 'DevOps']
    levels = ['Fresher', 'Intermediate', 'Experienced']

    return render_template('recruiter/applicants.html',
                           resumes=all_resumes,
                           fields=fields,
                           levels=levels,
                           field_filter=field_filter,
                           level_filter=level_filter,
                           min_score=min_score)


@recruiter_bp.route('/applicant/<resume_id>')
@recruiter_required
def applicant_detail(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume:
        flash('Resume not found', 'error')
        return redirect(url_for('recruiter.applicants'))
    user = User.get_by_id(resume.user_id)
    if user:
        resume.user_name = user.get_display_name()
        resume.user_email = user.email
    else:
        resume.user_name = 'Unknown Candidate'
        resume.user_email = ''
    # Job matches for this resume
    job_matches = JobMatchingService.get_jobs_for_resume(resume, top_n=5)
    return render_template('recruiter/applicant_detail.html',
                           resume=resume,
                           user=user,
                           job_matches=job_matches)


# ------------------------------------------------------------------ #
#  Job Management
# ------------------------------------------------------------------ #

@recruiter_bp.route('/jobs')
@recruiter_required
def jobs():
    all_jobs = Job.get_by_recruiter(current_user.id)
    return render_template('recruiter/jobs.html', jobs=all_jobs)


@recruiter_bp.route('/jobs/create', methods=['GET', 'POST'])
@recruiter_required
def create_job():
    if request.method == 'POST':
        required_skills_raw = request.form.get('required_skills', '')
        preferred_skills_raw = request.form.get('preferred_skills', '')

        job_data = {
            'title': request.form.get('title', '').strip(),
            'company': request.form.get('company', current_user.company).strip(),
            'location': request.form.get('location', '').strip(),
            'job_type': request.form.get('job_type', 'Full-Time'),
            'description': request.form.get('description', '').strip(),
            'required_skills': [s.strip() for s in required_skills_raw.split(',') if s.strip()],
            'preferred_skills': [s.strip() for s in preferred_skills_raw.split(',') if s.strip()],
            'experience_min': request.form.get('experience_min', 0),
            'experience_max': request.form.get('experience_max', 0),
            'education_required': request.form.get('education_required', '').strip(),
            'salary_range': request.form.get('salary_range', '').strip(),
        }

        if not job_data['title']:
            flash('Job title is required', 'error')
            return render_template('recruiter/job_form.html', job=None, edit=False)

        Job.create(current_user.id, job_data)
        flash('Job posted successfully!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/job_form.html', job=None, edit=False)


@recruiter_bp.route('/jobs/<job_id>/edit', methods=['GET', 'POST'])
@recruiter_required
def edit_job(job_id):
    job = Job.get_by_id(job_id)
    if not job or job.posted_by != current_user.id:
        flash('Job not found', 'error')
        return redirect(url_for('recruiter.jobs'))

    if request.method == 'POST':
        required_skills_raw = request.form.get('required_skills', '')
        preferred_skills_raw = request.form.get('preferred_skills', '')

        job_data = {
            'title': request.form.get('title', '').strip(),
            'company': request.form.get('company', '').strip(),
            'location': request.form.get('location', '').strip(),
            'job_type': request.form.get('job_type', 'Full-Time'),
            'description': request.form.get('description', '').strip(),
            'required_skills': [s.strip() for s in required_skills_raw.split(',') if s.strip()],
            'preferred_skills': [s.strip() for s in preferred_skills_raw.split(',') if s.strip()],
            'experience_min': int(request.form.get('experience_min', 0)),
            'experience_max': int(request.form.get('experience_max', 0)),
            'education_required': request.form.get('education_required', '').strip(),
            'salary_range': request.form.get('salary_range', '').strip(),
            'is_active': request.form.get('is_active') == 'on',
        }
        job.update(job_data)
        flash('Job updated successfully!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/job_form.html', job=job, edit=True)


@recruiter_bp.route('/jobs/<job_id>/delete', methods=['POST'])
@recruiter_required
def delete_job(job_id):
    job = Job.get_by_id(job_id)
    if job and job.posted_by == current_user.id:
        job.delete()
        flash('Job deleted successfully', 'success')
    return redirect(url_for('recruiter.jobs'))


@recruiter_bp.route('/jobs/<job_id>/candidates')
@recruiter_required
def job_candidates(job_id):
    job = Job.get_by_id(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('recruiter.jobs'))
    candidates = JobMatchingService.get_candidates_for_job(job, top_n=20)
    # Attach user info to resume objects
    for c in candidates:
        user = User.get_by_id(c['resume'].user_id)
        if user:
            c['resume'].user_name = user.get_display_name()
            c['resume'].user_email = user.email
        else:
            c['resume'].user_name = 'Unknown Candidate'
            c['resume'].user_email = ''
    return render_template('recruiter/job_candidates.html', job=job, candidates=candidates)


@recruiter_bp.route('/jobs/<job_id>/shortlist/<resume_id>', methods=['POST'])
@recruiter_required
def toggle_shortlist(job_id, resume_id):
    job = Job.get_by_id(job_id)
    if job and job.posted_by == current_user.id:
        job.toggle_shortlist(resume_id)
    return redirect(request.referrer or url_for('recruiter.job_candidates', job_id=job_id))


@recruiter_bp.route('/shortlisted')
@recruiter_required
def shortlisted():
    """View all shortlisted candidates across all jobs"""
    all_jobs = Job.get_by_recruiter(current_user.id)
    
    # Collect all shortlisted resumes
    shortlisted_resumes = {}
    for job in all_jobs:
        if hasattr(job, 'shortlisted') and job.shortlisted:
            for resume_id in job.shortlisted:
                if resume_id not in shortlisted_resumes:
                    resume = Resume.get_by_id(resume_id)
                    if resume:
                        user = User.get_by_id(resume.user_id)
                        resume.user_name = user.get_display_name() if user else 'Unknown Candidate'
                        resume.user_email = user.email if user else ''
                        shortlisted_resumes[resume_id] = {
                            'resume': resume,
                            'jobs': [job.id]
                        }
                else:
                    shortlisted_resumes[resume_id]['jobs'].append(job.id)
    
    shortlisted_data = list(shortlisted_resumes.values())
    return render_template('recruiter/shortlisted.html',
                           shortlisted_candidates=shortlisted_data,
                           total_shortlisted=len(shortlisted_data),
                           total_jobs=len(all_jobs))
