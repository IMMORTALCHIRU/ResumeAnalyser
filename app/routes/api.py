from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.resume import Resume
from app.models.job import Job
from app.services.job_matching_service import JobMatchingService

api_bp = Blueprint('api', __name__)


@api_bp.route('/resume/score/<resume_id>')
@login_required
def resume_score(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return jsonify({'error': 'Resume not found'}), 404
    return jsonify({
        'resume_score': resume.resume_score,
        'ats_score': resume.ats_score,
        'formatting_score': resume.formatting_score,
        'skills': resume.skills,
        'candidate_level': resume.candidate_level,
    })


@api_bp.route('/jobs/match/<resume_id>')
@login_required
def job_matches(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return jsonify({'error': 'Resume not found'}), 404
    matches = JobMatchingService.get_jobs_for_resume(resume, top_n=5)
    result = []
    for m in matches:
        result.append({
            'job_title': m['job'].title,
            'company': m['job'].company,
            'match_score': m['match']['match_score'],
            'recommendation': m['match']['recommendation'],
        })
    return jsonify(result)


@api_bp.route('/jobs')
def get_jobs():
    jobs = Job.get_all(active_only=True)
    return jsonify([j.to_dict() for j in jobs])


@api_bp.route('/field-distribution')
def field_distribution():
    data = Resume.count_by_field()
    return jsonify(data)
