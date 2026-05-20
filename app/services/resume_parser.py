import os
import re
from PyPDF2 import PdfReader
from docx import Document
from app.config import Config


class ResumeParserService:

    SKILL_KEYWORDS = {
        'programming_languages': [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
            'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'perl', 'typescript',
            'objective-c', 'shell', 'bash', 'powershell', 'sql', 'html', 'css',
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'node.js', 'rails', 'laravel', 'asp.net', 'fastapi', 'next.js',
            'nuxt.js', 'gatsby', 'svelte', 'ember', 'backbone', 'jquery',
            'bootstrap', 'tailwind', 'material-ui', 'redux', 'mobx',
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'oracle', 'sql server', 'sqlite', 'dynamodb',
            'firebase', 'neo4j', 'mariadb', 'couchdb',
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'puppet', 'chef', 'circleci', 'travis ci', 'gitlab ci',
            'github actions', 'prometheus', 'grafana', 'nginx', 'apache',
        ],
        'data_science_ml': [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'spark', 'hadoop', 'tableau', 'power bi',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data analysis', 'statistics', 'data visualization', 'mlflow',
            'huggingface', 'transformers', 'xgboost', 'lightgbm',
        ],
        'tools': [
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
            'slack', 'trello', 'asana', 'figma', 'sketch', 'adobe xd',
            'postman', 'swagger', 'vs code', 'intellij', 'eclipse',
        ],
        'mobile': [
            'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic',
            'swift', 'kotlin', 'objective-c', 'swiftui', 'jetpack compose',
        ],
    }

    EDUCATION_KEYWORDS = [
        'bachelor', 'master', 'phd', 'doctorate', 'b.tech', 'm.tech', 'b.e', 'm.e',
        'b.sc', 'm.sc', 'bca', 'mca', 'bba', 'mba', 'b.com', 'm.com', 'diploma',
        'certification', 'degree', 'university', 'college', 'institute', 'school',
    ]

    CERTIFICATION_KEYWORDS = [
        'certified', 'certification', 'certificate', 'aws certified', 'google certified',
        'microsoft certified', 'oracle certified', 'cisco', 'pmp', 'scrum master',
        'comptia', 'itil', 'six sigma', 'azure', 'gcp', 'professional',
    ]

    FIELD_SKILL_MAP = {
        'Data Science': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-Learn', 'Pandas',
                         'NumPy', 'SQL', 'Statistics', 'Machine Learning', 'Deep Learning',
                         'Data Visualization', 'Matplotlib', 'Seaborn', 'NLP', 'Spark'],
        'Web Development': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.Js', 'MongoDB',
                            'SQL', 'REST APIs', 'Git', 'Docker', 'TypeScript', 'GraphQL'],
        'Frontend Development': ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript',
                                 'Redux', 'Tailwind', 'Webpack', 'Git', 'Figma'],
        'Backend Development': ['Python', 'Node.Js', 'Java', 'PostgreSQL', 'MongoDB',
                                'Redis', 'Docker', 'REST APIs', 'GraphQL', 'AWS'],
        'Mobile Development': ['Flutter', 'React Native', 'Swift', 'Kotlin', 'Firebase',
                               'REST APIs', 'Git', 'Android', 'Ios'],
        'DevOps': ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Jenkins', 'Linux',
                   'Python', 'Ansible', 'CI/CD', 'Prometheus'],
    }

    @staticmethod
    def extract_text_from_pdf(file_path):
        try:
            reader = PdfReader(file_path)
            text = '\n'.join(page.extract_text() or '' for page in reader.pages)
            return text, len(reader.pages)
        except Exception as e:
            print(f'PDF extraction error: {e}')
            return '', 0

    @staticmethod
    def extract_text_from_docx(file_path):
        try:
            doc = Document(file_path)
            text = '\n'.join(para.text for para in doc.paragraphs)
            page_count = max(1, len(text) // 3000)
            return text, page_count
        except Exception as e:
            print(f'DOCX extraction error: {e}')
            return '', 0

    @classmethod
    def extract_skills(cls, text):
        text_lower = text.lower()
        found = set()
        for category, skills in cls.SKILL_KEYWORDS.items():
            for skill in skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found.add(skill.title())
        return sorted(found)

    @classmethod
    def extract_education(cls, text):
        lines = text.split('\n')
        education = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in cls.EDUCATION_KEYWORDS):
                context = ' '.join(lines[i:i+3]).strip()
                if context and len(context) > 10:
                    education.append(context)
        return list(dict.fromkeys(education))[:5]

    @classmethod
    def extract_certifications(cls, text):
        certs = []
        for line in text.split('\n'):
            if any(kw in line.lower() for kw in cls.CERTIFICATION_KEYWORDS):
                if len(line.strip()) > 5:
                    certs.append(line.strip())
        return list(dict.fromkeys(certs))[:10]

    @staticmethod
    def extract_contact_info(text):
        info = {}
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info['email'] = email_match.group()
        phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', text)
        if phone_match:
            info['phone'] = phone_match.group().strip()
        return info

    @staticmethod
    def estimate_experience_years(text):
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|of)\s*(?:software|development|programming)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        job_indicators = ['present', 'current', '2024', '2023', '2022', '2021', '2020']
        job_count = sum(1 for ind in job_indicators if ind in text.lower())
        return min(job_count * 2, 15)

    @staticmethod
    def calculate_resume_score(resume_data):
        score = 0
        score += min(len(resume_data.get('skills', [])) * 3, 30)
        if resume_data.get('education'):
            score += 15
        score += min(len(resume_data.get('certifications', [])) * 5, 10)
        score += min(resume_data.get('experience_years', 0) * 2, 20)
        if resume_data.get('has_objective'):
            score += 5
        if resume_data.get('has_projects'):
            score += 7
        if resume_data.get('has_achievements'):
            score += 6
        if resume_data.get('has_hobbies'):
            score += 3
        if resume_data.get('has_declaration'):
            score += 4
        return min(score, 100)

    @staticmethod
    def calculate_ats_score(resume_data):
        score = 0
        if resume_data.get('contact_info', {}).get('email'):
            score += 20
        if resume_data.get('contact_info', {}).get('phone'):
            score += 10
        if resume_data.get('skills'):
            score += 20
        if resume_data.get('education'):
            score += 20
        if resume_data.get('has_objective'):
            score += 10
        if resume_data.get('has_projects'):
            score += 10
        if resume_data.get('page_count', 1) <= 2:
            score += 10
        return min(score, 100)

    @staticmethod
    def calculate_formatting_score(text, page_count):
        score = 60
        if page_count <= 2:
            score += 20
        sections = ['education', 'experience', 'skills', 'projects', 'summary', 'objective']
        found = sum(1 for s in sections if s in text.lower())
        score += min(found * 3, 20)
        return min(score, 100)

    @classmethod
    def determine_candidate_level(cls, page_count, experience_years):
        if experience_years >= 5 or page_count >= 3:
            return 'Experienced'
        if experience_years >= 2 or page_count == 2:
            return 'Intermediate'
        return 'Fresher'

    @classmethod
    def predict_field(cls, skills):
        skills_lower = [s.lower() for s in skills]
        field_scores = {
            'Data Science': 0, 'Web Development': 0,
            'Mobile Development': 0, 'DevOps': 0,
            'Backend Development': 0, 'Frontend Development': 0,
        }
        mapping = {
            'tensorflow': 'Data Science', 'pytorch': 'Data Science', 'keras': 'Data Science',
            'pandas': 'Data Science', 'numpy': 'Data Science', 'machine learning': 'Data Science',
            'deep learning': 'Data Science', 'data analysis': 'Data Science',
            'react': 'Frontend Development', 'angular': 'Frontend Development',
            'vue': 'Frontend Development',
            'html': 'Frontend Development', 'css': 'Frontend Development',
            'django': 'Backend Development', 'flask': 'Backend Development',
            'spring': 'Backend Development', 'node.js': 'Backend Development',
            'android': 'Mobile Development', 'ios': 'Mobile Development',
            'flutter': 'Mobile Development', 'react native': 'Mobile Development',
            'kotlin': 'Mobile Development', 'swift': 'Mobile Development',
            'docker': 'DevOps', 'kubernetes': 'DevOps', 'aws': 'DevOps',
            'terraform': 'DevOps', 'jenkins': 'DevOps',
        }
        for skill in skills_lower:
            if skill in mapping:
                field_scores[mapping[skill]] += 2
        predicted = max(field_scores, key=field_scores.get)
        if all(v == 0 for v in field_scores.values()):
            return 'Web Development'
        return predicted

    @classmethod
    def get_skill_gap(cls, predicted_field, current_skills):
        expected = cls.FIELD_SKILL_MAP.get(predicted_field, [])
        current_lower = [s.lower() for s in current_skills]
        return [s for s in expected if s.lower() not in current_lower]

    @classmethod
    def get_recommended_skills(cls, predicted_field, current_skills):
        return cls.get_skill_gap(predicted_field, current_skills)[:10]

    @classmethod
    def get_strengths(cls, resume_data):
        strengths = []
        if len(resume_data.get('skills', [])) >= 10:
            strengths.append('Strong technical skill set')
        if resume_data.get('certifications'):
            strengths.append('Professional certifications')
        if resume_data.get('experience_years', 0) >= 3:
            strengths.append('Solid industry experience')
        if resume_data.get('has_projects'):
            strengths.append('Demonstrates practical project work')
        if resume_data.get('has_achievements'):
            strengths.append('Highlighted accomplishments')
        if resume_data.get('education'):
            strengths.append('Clear educational background')
        if not strengths:
            strengths.append('Resume submitted for analysis')
        return strengths

    @classmethod
    def get_improvements(cls, resume_data):
        improvements = []
        if not resume_data.get('has_objective'):
            improvements.append('Add a professional summary or objective statement')
        if not resume_data.get('has_projects'):
            improvements.append('Include relevant projects to showcase practical skills')
        if not resume_data.get('has_achievements'):
            improvements.append('Add measurable achievements and accomplishments')
        if len(resume_data.get('skills', [])) < 8:
            improvements.append('Expand your skills section with more relevant technologies')
        if not resume_data.get('certifications'):
            improvements.append('Consider adding professional certifications')
        if not resume_data.get('contact_info', {}).get('email'):
            improvements.append('Ensure contact information is clearly visible')
        if resume_data.get('page_count', 1) > 3:
            improvements.append('Consider condensing to 1-2 pages for better readability')
        if not improvements:
            improvements.append('Great resume! Keep it updated with latest experiences.')
        return improvements

    @classmethod
    def check_resume_sections(cls, text):
        t = text.lower()
        return {
            'has_objective': any(w in t for w in ['objective', 'career objective', 'summary', 'profile']),
            'has_projects': any(w in t for w in ['project', 'projects', 'portfolio']),
            'has_achievements': any(w in t for w in ['achievement', 'achievements', 'accomplishment', 'award']),
            'has_hobbies': any(w in t for w in ['hobby', 'hobbies', 'interest', 'interests']),
            'has_declaration': any(w in t for w in ['declaration', 'declare', 'hereby']),
        }

    @classmethod
    def parse_resume(cls, file_path, filename):
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext == 'pdf':
            raw_text, page_count = cls.extract_text_from_pdf(file_path)
        elif ext == 'docx':
            raw_text, page_count = cls.extract_text_from_docx(file_path)
        else:
            return None

        if not raw_text.strip():
            return None

        skills = cls.extract_skills(raw_text)
        education = cls.extract_education(raw_text)
        certifications = cls.extract_certifications(raw_text)
        experience_years = cls.estimate_experience_years(raw_text)
        sections = cls.check_resume_sections(raw_text)
        contact_info = cls.extract_contact_info(raw_text)
        predicted_field = cls.predict_field(skills)
        recommended_skills = cls.get_recommended_skills(predicted_field, skills)
        skill_gap = cls.get_skill_gap(predicted_field, skills)
        candidate_level = cls.determine_candidate_level(page_count, experience_years)

        resume_data = {
            'filename': filename,
            'raw_text': raw_text,
            'page_count': page_count,
            'skills': skills,
            'education': education,
            'certifications': certifications,
            'experience_years': experience_years,
            'predicted_field': predicted_field,
            'recommended_skills': recommended_skills,
            'skill_gap': skill_gap,
            'candidate_level': candidate_level,
            'technical_keywords': skills,
            'contact_info': contact_info,
            **sections,
        }

        resume_data['resume_score'] = cls.calculate_resume_score(resume_data)
        resume_data['ats_score'] = cls.calculate_ats_score(resume_data)
        resume_data['formatting_score'] = cls.calculate_formatting_score(raw_text, page_count)
        resume_data['strengths'] = cls.get_strengths(resume_data)
        resume_data['improvements'] = cls.get_improvements(resume_data)
        resume_data['keyword_density'] = round(len(skills) / max(len(raw_text.split()), 1) * 100, 2)

        return resume_data
