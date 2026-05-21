from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from app import mongo

AVATAR_COLORS = [
    '#667eea', '#f093fb', '#4facfe', '#43e97b',
    '#fa709a', '#fee140', '#30cfd0', '#a18cd1'
]

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'user')           # 'user' or 'recruiter'
        self.preferred_roles = user_data.get('preferred_roles', [])
        self.date_joined = user_data.get('date_joined', datetime.utcnow())
        self.profile_summary = user_data.get('profile_summary', '')
        self.avatar_color = user_data.get('avatar_color', '#667eea')
        self.phone = user_data.get('phone', '')
        self.company = user_data.get('company', '')         # recruiter's company
        self.is_active_account = user_data.get('is_active_account', True)

    @property
    def is_recruiter(self):
        return self.role == 'recruiter'

    @staticmethod
    def create(name, email, password, role='user', company=''):
        password_hash = generate_password_hash(password)
        idx = abs(hash(email)) % len(AVATAR_COLORS)
        user_data = {
            'name': name,
            'email': email.lower(),
            'password_hash': password_hash,
            'role': role,
            'preferred_roles': [],
            'date_joined': datetime.utcnow(),
            'profile_summary': '',
            'avatar_color': AVATAR_COLORS[idx],
            'phone': '',
            'company': company,
            'is_active_account': True,
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({'email': email.lower()})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except Exception:
            pass
        return None

    @staticmethod
    def get_all_applicants():
        """Return all users with role='user'"""
        users = mongo.db.users.find({'role': 'user'}).sort('date_joined', -1)
        return [User(u) for u in users]

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_profile(self, data):
        update_data = {}
        for field in ('name', 'preferred_roles', 'profile_summary', 'phone'):
            if field in data:
                update_data[field] = data[field]
        if update_data:
            mongo.db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': update_data}
            )
            return True
        return False

    def get_initials(self):
        try:
            if self.name and self.name.strip():
                names = self.name.split()
                if len(names) >= 2:
                    return (names[0][0] + names[1][0]).upper()
                return self.name[0:2].upper()
            if self.email and self.email.strip():
                prefix = self.email.split('@')[0]
                return prefix[0:2].upper()
        except Exception:
            pass
        return 'UU'

    def get_display_name(self):
        """Return a safe display name for UI.

        Priority: `name` -> email prefix -> 'Unknown User'
        """
        if self.name and str(self.name).strip():
            return str(self.name).strip()
        if self.email and str(self.email).strip():
            return str(self.email).split('@')[0]
        return 'Unknown User'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.get_display_name(),
            'email': self.email,
            'role': self.role,
            'preferred_roles': self.preferred_roles,
            'date_joined': self.date_joined,
            'profile_summary': self.profile_summary,
            'avatar_color': self.avatar_color,
            'phone': self.phone,
            'company': self.company,
        }