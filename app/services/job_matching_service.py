"""
AI-powered job-resume matching service.
Uses TF-IDF style skill overlap and weighted scoring for match percentage.
"""
from app.models.resume import Resume
from app.models.job import Job


class JobMatchingService:

    @staticmethod
    def _normalise(skills: list) -> set:
        return {s.lower().strip() for s in skills}

    @classmethod
    def match_score(cls, resume: Resume, job: Job) -> dict:
        """
        Returns a dict with:
          - match_score  (0-100)
          - matched_skills
          - missing_skills
          - experience_ok  (bool)
          - recommendation  (str label)
        """
        resume_skills = cls._normalise(resume.skills)
        required = cls._normalise(job.required_skills)
        preferred = cls._normalise(job.preferred_skills)

        # Skill matching
        matched_required = required & resume_skills
        matched_preferred = preferred & resume_skills
        missing = (required | preferred) - resume_skills

        if required:
            req_score = len(matched_required) / len(required) * 60
        else:
            req_score = 30  # no requirements listed → neutral

        if preferred:
            pref_score = len(matched_preferred) / len(preferred) * 20
        else:
            pref_score = 10

        # Experience matching (max 20 points)
        exp_min = job.experience_min or 0
        exp_max = job.experience_max or 99
        exp_years = resume.experience_years or 0
        if exp_min <= exp_years <= exp_max:
            exp_score = 20
            experience_ok = True
        elif exp_years >= exp_min:
            exp_score = 15
            experience_ok = True
        else:
            gap = exp_min - exp_years
            exp_score = max(0, 20 - gap * 5)
            experience_ok = False

        total = round(req_score + pref_score + exp_score, 1)
        total = min(total, 100)

        if total >= 75:
            recommendation = 'Highly Recommended'
        elif total >= 50:
            recommendation = 'Good Match'
        elif total >= 30:
            recommendation = 'Partial Match'
        else:
            recommendation = 'Low Match'

        return {
            'match_score': total,
            'matched_skills': sorted(matched_required | matched_preferred),
            'missing_skills': sorted(missing)[:10],
            'experience_ok': experience_ok,
            'recommendation': recommendation,
        }

    @classmethod
    def get_candidates_for_job(cls, job: Job, top_n: int = 20) -> list:
        """Return sorted list of (resume, match_dict) for a specific job."""
        all_resumes = Resume.get_all()
        results = []
        for resume in all_resumes:
            match = cls.match_score(resume, job)
            results.append({'resume': resume, 'match': match})
        results.sort(key=lambda x: x['match']['match_score'], reverse=True)
        return results[:top_n]

    @classmethod
    def get_jobs_for_resume(cls, resume: Resume, top_n: int = 10) -> list:
        """Return sorted list of (job, match_dict) for a specific resume."""
        all_jobs = Job.get_all(active_only=True)
        results = []
        for job in all_jobs:
            match = cls.match_score(resume, job)
            results.append({'job': job, 'match': match})
        results.sort(key=lambda x: x['match']['match_score'], reverse=True)
        return results[:top_n]
