from bson import ObjectId
from datetime import datetime
from app import mongo

class Recommendation:
    def __init__(self, rec_data):
        self.id = str(rec_data.get('_id'))
        self.user_id = str(rec_data.get('user_id'))
        self.recommended_roles = rec_data.get('recommended_roles', [])
        self.recommended_courses = rec_data.get('recommended_courses', [])
        self.recommended_skills = rec_data.get('recommended_skills', [])
        self.created_at = rec_data.get('created_at', datetime.utcnow())
        self.based_on_resume = rec_data.get('based_on_resume', '')
        self.confidence_scores = rec_data.get('confidence_scores', {})
    
    @staticmethod
    def create(user_id, rec_data):
        rec_data['user_id'] = ObjectId(user_id)
        rec_data['created_at'] = datetime.utcnow()
        result = mongo.db.recommendations.insert_one(rec_data)
        rec_data['_id'] = result.inserted_id
        return Recommendation(rec_data)
    
    @staticmethod
    def get_latest_by_user(user_id):
        rec_data = mongo.db.recommendations.find_one(
            {'user_id': ObjectId(user_id)},
            sort=[('created_at', -1)]
        )
        if rec_data:
            return Recommendation(rec_data)
        return None
    
    @staticmethod
    def update_or_create(user_id, rec_data):
        rec_data['user_id'] = ObjectId(user_id)
        rec_data['created_at'] = datetime.utcnow()
        result = mongo.db.recommendations.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': rec_data},
            upsert=True
        )
        return Recommendation.get_latest_by_user(user_id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommended_roles': self.recommended_roles,
            'recommended_courses': self.recommended_courses,
            'recommended_skills': self.recommended_skills,
            'created_at': self.created_at,
            'confidence_scores': self.confidence_scores
        }