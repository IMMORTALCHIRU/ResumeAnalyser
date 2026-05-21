"""
AI-powered job-resume matching service.
Combines keyword-based matching with semantic skill embeddings for accurate matching.
Uses hybrid scoring: keyword overlap (40%) + semantic similarity (40%) + experience (20%).
"""
import logging
from typing import Dict, List
from app.models.resume import Resume
from app.models.job import Job
from app.services.skill_embedding_service import get_skill_embedding_service

logger = logging.getLogger(__name__)


class JobMatchingService:

    @staticmethod
    def _normalise(skills: list) -> set:
        return {s.lower().strip() for s in skills}

    @classmethod
    def _keyword_score(cls, required: set, preferred: set, resume_skills: set) -> float:
        """
        Calculate keyword-based skill match score (0-100).
        
        Args:
            required: Required skills (set)
            preferred: Preferred skills (set)
            resume_skills: Candidate's skills (set)
            
        Returns:
            Keyword match score (0-100)
        """
        matched_required = required & resume_skills
        matched_preferred = preferred & resume_skills

        if required:
            req_score = len(matched_required) / len(required) * 60
        else:
            req_score = 30  # no requirements listed → neutral

        if preferred:
            pref_score = len(matched_preferred) / len(preferred) * 20
        else:
            pref_score = 10

        return req_score + pref_score

    @classmethod
    def _semantic_score(cls, required_skills: list, resume_skills: list) -> float:
        """
        Calculate semantic skill match score using embeddings (0-100).
        
        Args:
            required_skills: List of required skills
            resume_skills: List of candidate's skills
            
        Returns:
            Semantic match score (0-100)
        """
        if not required_skills or not resume_skills:
            return 0.0

        try:
            embedding_service = get_skill_embedding_service()
            match_result = embedding_service.match_skills_semantically(
                required_skills,
                resume_skills,
                threshold=0.7  # Slightly lower for semantic matching
            )
            match_pct = match_result.get('match_percentage', 0)
            return match_pct
        except Exception as e:
            logger.warning(f"Semantic scoring failed, falling back to keyword: {e}")
            return 0.0

    @classmethod
    def _experience_score(cls, job_exp_min: int, job_exp_max: int, resume_exp: int) -> tuple:
        """
        Calculate experience match score (0-20) and bool.
        
        Args:
            job_exp_min: Min experience required for job
            job_exp_max: Max experience (optional cap)
            resume_exp: Candidate's experience years
            
        Returns:
            Tuple of (score, experience_ok_bool)
        """
        exp_min = job_exp_min or 0
        exp_max = job_exp_max or 99
        exp_years = resume_exp or 0

        if exp_min <= exp_years <= exp_max:
            return 20, True
        elif exp_years >= exp_min:
            return 15, True
        else:
            gap = exp_min - exp_years
            score = max(0, 20 - gap * 5)
            return score, False

    @staticmethod
    def _normalise(skills: list) -> set:
        return {s.lower().strip() for s in skills}

    @classmethod
    def match_score(cls, resume: Resume, job: Job) -> dict:
        """
        Calculate comprehensive match score using hybrid approach:
        - Keyword matching (40%)
        - Semantic similarity (40%)
        - Experience matching (20%)
        
        Returns a dict with:
          - match_score: Overall score (0-100)
          - keyword_score: Keyword-based score (0-100)
          - semantic_score: Semantic similarity score (0-100)
          - matched_skills: Exact keyword matches
          - missing_skills: Unmatched required skills
          - experience_ok: Bool indicating experience fit
          - recommendation: Label (Highly Recommended, Good Match, etc.)
          - semantic_details: Dict with semantic matching details (optional)
        """
        resume_skills = cls._normalise(resume.skills)
        required = cls._normalise(job.required_skills)
        preferred = cls._normalise(job.preferred_skills)

        # 1. Keyword score (40% weight)
        keyword_score = cls._keyword_score(required, preferred, resume_skills)

        # 2. Semantic score (40% weight)
        semantic_score = cls._semantic_score(
            list(required | preferred),
            list(resume_skills)
        )

        # 3. Experience score (20% weight)
        exp_score, experience_ok = cls._experience_score(
            job.experience_min or 0,
            job.experience_max,
            resume.experience_years or 0
        )

        # Hybrid weighted score
        total = (
            (keyword_score * 0.4) +
            (semantic_score * 0.4) +
            (exp_score)  # exp_score already weighted as 0-20
        )
        total = round(min(total, 100), 1)

        # Recommendation label
        if total >= 75:
            recommendation = 'Highly Recommended'
        elif total >= 60:
            recommendation = 'Good Match'
        elif total >= 40:
            recommendation = 'Partial Match'
        else:
            recommendation = 'Low Match'

        # Collect skill details
        matched_required = required & resume_skills
        matched_preferred = preferred & resume_skills
        missing = (required | preferred) - resume_skills

        # Semantic matching details (optional, for advanced UIs)
        semantic_details = None
        try:
            embedding_service = get_skill_embedding_service()
            semantic_match = embedding_service.match_skills_semantically(
                list(required | preferred),
                list(resume_skills),
                threshold=0.7
            )
            semantic_details = {
                'semantic_matched': semantic_match.get('matched', []),
                'semantic_unmatched': semantic_match.get('unmatched', []),
                'match_details': semantic_match.get('match_details', {})
            }
        except Exception as e:
            logger.debug(f"Semantic details retrieval failed (non-critical): {e}")

        return {
            'match_score': total,
            'keyword_score': round(keyword_score, 1),
            'semantic_score': round(semantic_score, 1),
            'experience_score': exp_score,
            'matched_skills': sorted(matched_required | matched_preferred),
            'missing_skills': sorted(missing)[:10],
            'experience_ok': experience_ok,
            'recommendation': recommendation,
            'semantic_details': semantic_details,
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
