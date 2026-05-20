from bson import ObjectId
from datetime import datetime
from app import mongo

class Resume:
    def __init__(self, resume_data):
        self.id = str(resume_data.get('_id'))
        self.user_id = str(resume_data.get('user_id'))
        self.filename = resume_data.get('filename')
        self.upload_date = resume_data.get('upload_date', datetime.utcnow())
        self.skills = resume_data.get('skills', [])
        self.experience_years = resume_data.get('experience_years', 0)
        self.education = resume_data.get('education', [])
        self.certifications = resume_data.get('certifications', [])
        self.technical_keywords = resume_data.get('technical_keywords', [])
        self.work_history = resume_data.get('work_history', [])
        self.resume_score = resume_data.get('resume_score', 0)
        self.candidate_level = resume_data.get('candidate_level', 'Fresher')
        self.predicted_field = resume_data.get('predicted_field', '')
        self.recommended_skills = resume_data.get('recommended_skills', [])
        self.skill_gap = resume_data.get('skill_gap', [])
        self.strengths = resume_data.get('strengths', [])
        self.improvements = resume_data.get('improvements', [])
        self.ats_score = resume_data.get('ats_score', 0)        # ATS compatibility score
        self.formatting_score = resume_data.get('formatting_score', 0)
        self.keyword_density = resume_data.get('keyword_density', 0.0)
        self.contact_info = resume_data.get('contact_info', {})
        self.has_objective = resume_data.get('has_objective', False)
        self.has_declaration = resume_data.get('has_declaration', False)
        self.has_hobbies = resume_data.get('has_hobbies', False)
        self.has_achievements = resume_data.get('has_achievements', False)
        self.has_projects = resume_data.get('has_projects', False)
        self.raw_text = resume_data.get('raw_text', '')
        self.page_count = resume_data.get('page_count', 1)
    
    @staticmethod
    def create(user_id, resume_data):
        resume_data['user_id'] = ObjectId(user_id)
        resume_data['upload_date'] = datetime.utcnow()
        result = mongo.db.resumes.insert_one(resume_data)
        resume_data['_id'] = result.inserted_id
        return Resume(resume_data)

    @staticmethod
    def get_by_user(user_id):
        resumes = mongo.db.resumes.find({'user_id': ObjectId(user_id)}).sort('upload_date', -1)
        return [Resume(r) for r in resumes]

    @staticmethod
    def get_latest_by_user(user_id):
        resume_data = mongo.db.resumes.find_one(
            {'user_id': ObjectId(user_id)},
            sort=[('upload_date', -1)]
        )
        if resume_data:
            return Resume(resume_data)
        return None

    @staticmethod
    def get_by_id(resume_id):
        try:
            resume_data = mongo.db.resumes.find_one({'_id': ObjectId(resume_id)})
            if resume_data:
                return Resume(resume_data)
        except Exception:
            pass
        return None

    @staticmethod
    def get_all():
        """Return all resumes (recruiter view), latest per user, sorted by score desc."""
        pipeline = [
            {'$sort': {'upload_date': -1}},
            {'$group': {
                '_id': '$user_id',
                'doc': {'$first': '$$ROOT'}
            }},
            {'$replaceRoot': {'newRoot': '$doc'}},
            {'$sort': {'resume_score': -1}}
        ]
        resumes = mongo.db.resumes.aggregate(pipeline)
        return [Resume(r) for r in resumes]

    @staticmethod
    def count_by_field():
        pipeline = [
            {'$group': {'_id': '$predicted_field', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        return list(mongo.db.resumes.aggregate(pipeline))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'upload_date': self.upload_date,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'education': self.education,
            'certifications': self.certifications,
            'technical_keywords': self.technical_keywords,
            'work_history': self.work_history,
            'resume_score': self.resume_score,
            'ats_score': self.ats_score,
            'formatting_score': self.formatting_score,
            'candidate_level': self.candidate_level,
            'predicted_field': self.predicted_field,
            'recommended_skills': self.recommended_skills,
            'skill_gap': self.skill_gap,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'page_count': self.page_count
        }