import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/interview_prep_tracker')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # Interview types
    INTERVIEW_TYPES = [
        'Data Structures & Algorithms',
        'Web Development',
        'Machine Learning',
        'System Design',
        'Database',
        'Python Programming',
        'JavaScript',
        'DevOps'
    ]
    
    # Skill categories
    SKILL_CATEGORIES = {
        'data_science': ['python', 'tensorflow', 'keras', 'pytorch', 'machine learning', 
                         'deep learning', 'pandas', 'numpy', 'scikit-learn', 'data analysis',
                         'statistics', 'r', 'sql', 'tableau', 'power bi'],
        'web_development': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 
                            'node.js', 'express', 'django', 'flask', 'php', 'laravel',
                            'ruby on rails', 'typescript', 'next.js'],
        'mobile_development': ['android', 'ios', 'swift', 'kotlin', 'flutter', 
                               'react native', 'java', 'objective-c'],
        'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 
                   'terraform', 'ansible', 'ci/cd', 'linux'],
        'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                     'oracle', 'sql server', 'cassandra', 'dynamodb'],
        'dsa': ['algorithms', 'data structures', 'leetcode', 'competitive programming',
                'problem solving', 'system design']
    }
    
    # Job role mappings
    JOB_ROLE_MAPPINGS = {
        'Backend Developer': ['python', 'java', 'node.js', 'django', 'flask', 'spring', 'sql'],
        'Frontend Developer': ['javascript', 'react', 'angular', 'vue', 'html', 'css', 'typescript'],
        'Full Stack Developer': ['javascript', 'python', 'react', 'node.js', 'mongodb', 'sql'],
        'Data Scientist': ['python', 'machine learning', 'tensorflow', 'pandas', 'statistics'],
        'Data Analyst': ['sql', 'python', 'tableau', 'excel', 'power bi', 'statistics'],
        'ML Engineer': ['python', 'tensorflow', 'pytorch', 'docker', 'kubernetes', 'mlops'],
        'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'jenkins', 'terraform', 'linux'],
        'Mobile Developer': ['android', 'ios', 'flutter', 'react native', 'kotlin', 'swift'],
        'Cloud Architect': ['aws', 'azure', 'gcp', 'terraform', 'kubernetes', 'docker'],
        'Database Administrator': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle']
    }