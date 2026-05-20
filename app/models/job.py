from bson import ObjectId
from datetime import datetime
from app import mongo


class Job:
    def __init__(self, job_data):
        self.id = str(job_data.get('_id'))
        self.title = job_data.get('title', '')
        self.company = job_data.get('company', '')
        self.location = job_data.get('location', '')
        self.job_type = job_data.get('job_type', 'Full-Time')   # Full-Time / Part-Time / Contract / Remote
        self.description = job_data.get('description', '')
        self.required_skills = job_data.get('required_skills', [])
        self.preferred_skills = job_data.get('preferred_skills', [])
        self.experience_min = job_data.get('experience_min', 0)
        self.experience_max = job_data.get('experience_max', 0)
        self.education_required = job_data.get('education_required', '')
        self.salary_range = job_data.get('salary_range', '')
        self.posted_by = str(job_data.get('posted_by', ''))     # recruiter user_id
        self.created_at = job_data.get('created_at', datetime.utcnow())
        self.is_active = job_data.get('is_active', True)
        self.applicant_count = job_data.get('applicant_count', 0)
        self.shortlisted = job_data.get('shortlisted', [])      # list of resume_ids

    @staticmethod
    def create(recruiter_id, job_data):
        doc = {
            'title': job_data.get('title', '').strip(),
            'company': job_data.get('company', '').strip(),
            'location': job_data.get('location', '').strip(),
            'job_type': job_data.get('job_type', 'Full-Time'),
            'description': job_data.get('description', '').strip(),
            'required_skills': [s.strip() for s in job_data.get('required_skills', []) if s.strip()],
            'preferred_skills': [s.strip() for s in job_data.get('preferred_skills', []) if s.strip()],
            'experience_min': int(job_data.get('experience_min', 0)),
            'experience_max': int(job_data.get('experience_max', 0)),
            'education_required': job_data.get('education_required', '').strip(),
            'salary_range': job_data.get('salary_range', '').strip(),
            'posted_by': ObjectId(recruiter_id),
            'created_at': datetime.utcnow(),
            'is_active': True,
            'applicant_count': 0,
            'shortlisted': [],
        }
        result = mongo.db.jobs.insert_one(doc)
        doc['_id'] = result.inserted_id
        return Job(doc)

    @staticmethod
    def get_all(active_only=True):
        query = {'is_active': True} if active_only else {}
        jobs = mongo.db.jobs.find(query).sort('created_at', -1)
        return [Job(j) for j in jobs]

    @staticmethod
    def get_by_recruiter(recruiter_id, active_only=False):
        query = {'posted_by': ObjectId(recruiter_id)}
        if active_only:
            query['is_active'] = True
        jobs = mongo.db.jobs.find(query).sort('created_at', -1)
        return [Job(j) for j in jobs]

    @staticmethod
    def get_by_id(job_id):
        try:
            doc = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
            if doc:
                return Job(doc)
        except Exception:
            pass
        return None

    def update(self, data):
        allowed = ('title', 'company', 'location', 'job_type', 'description',
                   'required_skills', 'preferred_skills', 'experience_min',
                   'experience_max', 'education_required', 'salary_range', 'is_active')
        update_doc = {k: v for k, v in data.items() if k in allowed}
        if update_doc:
            mongo.db.jobs.update_one({'_id': ObjectId(self.id)}, {'$set': update_doc})
            return True
        return False

    def toggle_shortlist(self, resume_id):
        if resume_id in self.shortlisted:
            mongo.db.jobs.update_one(
                {'_id': ObjectId(self.id)},
                {'$pull': {'shortlisted': resume_id}}
            )
        else:
            mongo.db.jobs.update_one(
                {'_id': ObjectId(self.id)},
                {'$addToSet': {'shortlisted': resume_id}}
            )

    def delete(self):
        mongo.db.jobs.delete_one({'_id': ObjectId(self.id)})

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'description': self.description,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'experience_min': self.experience_min,
            'experience_max': self.experience_max,
            'education_required': self.education_required,
            'salary_range': self.salary_range,
            'posted_by': self.posted_by,
            'created_at': self.created_at,
            'is_active': self.is_active,
        }
