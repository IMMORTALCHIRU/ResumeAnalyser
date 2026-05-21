from app.models.recommendation import Recommendation
from app.models.resume import Resume
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class RecommendationService:

    COURSES = {
        'Data Science': [
            {'name': 'Machine Learning by Andrew Ng', 'url': 'https://www.coursera.org/learn/machine-learning', 'platform': 'Coursera'},
            {'name': 'Deep Learning Specialization', 'url': 'https://www.coursera.org/specializations/deep-learning', 'platform': 'Coursera'},
            {'name': 'IBM Data Science Certificate', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science', 'platform': 'Coursera'},
            {'name': 'Python for Data Science', 'url': 'https://www.datacamp.com/tracks/data-scientist-with-python', 'platform': 'DataCamp'},
        ],
        'Web Development': [
            {'name': 'The Complete Web Developer Course', 'url': 'https://www.udemy.com/course/the-complete-web-developer-course-2/', 'platform': 'Udemy'},
            {'name': 'Full Stack Web Developer Nanodegree', 'url': 'https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044', 'platform': 'Udacity'},
            {'name': 'React - The Complete Guide', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'platform': 'Udemy'},
            {'name': 'Node.js Developer Course', 'url': 'https://www.udemy.com/course/the-complete-nodejs-developer-course-2/', 'platform': 'Udemy'},
        ],
        'Mobile Development': [
            {'name': 'Flutter & Dart Development Course', 'url': 'https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/', 'platform': 'Udemy'},
            {'name': 'iOS App Development with Swift', 'url': 'https://www.coursera.org/specializations/app-development', 'platform': 'Coursera'},
            {'name': 'Android Development for Beginners', 'url': 'https://developer.android.com/courses', 'platform': 'Google'},
        ],
        'DevOps': [
            {'name': 'Docker and Kubernetes Complete Guide', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/', 'platform': 'Udemy'},
            {'name': 'AWS Certified Solutions Architect', 'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate/', 'platform': 'Udemy'},
            {'name': 'DevOps Engineering Course', 'url': 'https://www.coursera.org/professional-certificates/devops-engineer', 'platform': 'Coursera'},
        ],
        'Backend Development': [
            {'name': 'Python Backend Development', 'url': 'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/', 'platform': 'Udemy'},
            {'name': 'Node.js Backend Mastery', 'url': 'https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/', 'platform': 'Udemy'},
            {'name': 'REST API Design', 'url': 'https://www.udacity.com/course/designing-restful-apis--ud388', 'platform': 'Udacity'},
        ],
        'Frontend Development': [
            {'name': 'Advanced CSS and Sass', 'url': 'https://www.udemy.com/course/advanced-css-and-sass/', 'platform': 'Udemy'},
            {'name': 'JavaScript - The Complete Guide', 'url': 'https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/', 'platform': 'Udemy'},
            {'name': 'React Developer Nanodegree', 'url': 'https://www.udacity.com/course/react-nanodegree--nd019', 'platform': 'Udacity'},
        ],
    }

    @classmethod
    def generate_job_recommendations(cls, user_id):
        """
        Generate job role recommendations based on resume skills.
        Uses semantic matching for better accuracy.
        """
        resume = Resume.get_latest_by_user(user_id)
        if not resume:
            return None

        skills = [s.lower() for s in resume.skills]
        experience_years = resume.experience_years

        # Try semantic matching for enhanced accuracy
        use_semantic = False
        embedding_service = None
        
        try:
            from app.services.skill_embedding_service import get_skill_embedding_service
            embedding_service = get_skill_embedding_service()
            use_semantic = True
        except Exception as e:
            logger.info(f"Semantic matching unavailable: {e}. Using keyword matching.")

        role_scores = {}
        for role, required_skills in Config.JOB_ROLE_MAPPINGS.items():
            if use_semantic and embedding_service:
                # Use semantic matching for better skill alignment detection
                try:
                    match_result = embedding_service.match_skills_semantically(
                        required_skills,
                        skills,
                        threshold=Config.SEMANTIC_SIMILARITY_THRESHOLD
                    )
                    skill_match = match_result['match_percentage'] / 100.0
                except Exception as e:
                    logger.warning(f"Semantic matching failed for role {role}: {e}")
                    # Fallback to keyword matching
                    matched = sum(1 for skill in required_skills if skill.lower() in skills)
                    skill_match = matched / len(required_skills) if required_skills else 0
            else:
                # Keyword-based matching
                matched = sum(1 for skill in required_skills if skill.lower() in skills)
                skill_match = matched / len(required_skills) if required_skills else 0
            
            exp_factor = min(experience_years / 5, 1)
            score = (skill_match * 0.75) + (exp_factor * 0.25)
            role_scores[role] = round(score * 100, 2)

        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        top_roles = [{'role': role, 'match_score': score} for role, score in sorted_roles[:5]]

        predicted_field = resume.predicted_field
        courses = cls.COURSES.get(predicted_field, cls.COURSES['Web Development'])[:3]
        
        # Get recommended skills with semantic deduplication
        recommended_skills = cls._deduplicate_skills_semantically(
            resume.recommended_skills[:12],
            embedding_service if use_semantic else None
        )[:8]

        rec_data = {
            'recommended_roles': top_roles,
            'recommended_courses': courses,
            'recommended_skills': recommended_skills,
            'based_on_resume': resume.id,
            'confidence_scores': role_scores,
            'semantic_matching': use_semantic,
        }
        return Recommendation.update_or_create(user_id, rec_data)

    @classmethod
    def _deduplicate_skills_semantically(cls, skills, embedding_service=None):
        """
        Deduplicate and organize skills using semantic clustering.
        
        Groups similar skills together and returns the most representative ones.
        Falls back to simple deduplication if embedding service unavailable.
        
        Args:
            skills: List of skill strings to deduplicate
            embedding_service: SkillEmbeddingService instance (optional)
            
        Returns:
            Deduplicated and clustered skill list
        """
        if not skills:
            return []
        
        if embedding_service is None:
            # Simple deduplication: case-insensitive unique
            seen = set()
            result = []
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower not in seen:
                    seen.add(skill_lower)
                    result.append(skill)
            return result
        
        try:
            # Use semantic clustering for intelligent deduplication
            clusters = embedding_service.cluster_skills(skills, threshold=0.8)
            result = []
            for cluster in clusters:
                # Use the first (most representative) skill from each cluster
                if cluster:
                    result.append(cluster[0])
            return result
        except Exception as e:
            logger.warning(f"Semantic deduplication failed: {e}. Using simple deduplication.")
            # Fallback to simple deduplication
            seen = set()
            result = []
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower not in seen:
                    seen.add(skill_lower)
                    result.append(skill)
            return result
