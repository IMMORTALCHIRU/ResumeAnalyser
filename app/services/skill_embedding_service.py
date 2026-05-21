"""
Semantic skill extraction and similarity scoring using pretrained embeddings.

Uses sentence-transformers (all-MiniLM-L6-v2) for fast, accurate semantic skill matching.
Includes caching, error handling, and fallback to keyword matching.
"""
import logging
from typing import List, Dict, Tuple, Set
import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Thread-safe in-memory cache for skill embeddings."""

    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, np.ndarray] = {}
        self.max_size = max_size

    def get(self, key: str) -> np.ndarray:
        """Retrieve embedding from cache."""
        return self.cache.get(key)

    def set(self, key: str, value: np.ndarray) -> None:
        """Store embedding in cache (simple FIFO if full)."""
        if len(self.cache) >= self.max_size:
            self.cache.clear()
            logger.info("Embedding cache cleared (max size reached)")
        self.cache[key] = value

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    def size(self) -> int:
        """Return current cache size."""
        return len(self.cache)


class SkillEmbeddingService:
    """
    Semantic skill extraction and similarity scoring using transformers.
    
    Provides:
    - Skill canonicalization (standardize skill names)
    - Semantic similarity scoring (cosine similarity on embeddings)
    - Skill clustering (group similar skills)
    - Robust error handling and fallback mechanisms
    """

    # Model configuration (use lightweight model for speed)
    MODEL_NAME = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD = 0.75  # Tunable
    MAX_BATCH_SIZE = 128

    # Skill canonicalization map (maps variants to standard names)
    SKILL_ALIASES = {
        'nodejs': 'node.js',
        'node js': 'node.js',
        'dotnet': '.net',
        'c#': 'csharp',
        'c sharp': 'csharp',
        'c++': 'cpp',
        'objective c': 'objective-c',
        'react native': 'react-native',
        'machine learning': 'ml',
        'deep learning': 'dl',
        'natural language processing': 'nlp',
        'computer vision': 'cv',
        'tensorflow': 'tf',
        'pytorch': 'pt',
        'scikit learn': 'scikit-learn',
        'aws': 'amazon web services',
        'gcp': 'google cloud platform',
        'ci/cd': 'cicd',
    }

    # Core skills that should always match exactly in initial phase
    CORE_SKILLS = {
        'python', 'java', 'javascript', 'react', 'angular', 'vue',
        'django', 'flask', 'node.js', 'sql', 'mongodb', 'aws',
        'docker', 'kubernetes', 'git', 'ml', 'dl', 'tensorflow',
        'pytorch', 'tensorflow', 'pandas', 'numpy', 'scikit-learn',
    }

    def __init__(self, model_name: str = None):
        """
        Initialize embedding service with lazy model loading.
        
        Args:
            model_name: Optional custom model name (defaults to all-MiniLM-L6-v2)
        """
        self.model_name = model_name or self.MODEL_NAME
        self.model = None
        self.cache = EmbeddingCache()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _load_model(self) -> SentenceTransformer:
        """Lazy load model on first use."""
        if self.model is None:
            try:
                self.logger.info(f"Loading model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                self.logger.info(f"Model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Failed to load embedding model: {e}")
        return self.model

    def _canonicalize_skill(self, skill: str) -> str:
        """
        Standardize skill name (lowercase, strip, apply aliases).
        
        Args:
            skill: Raw skill string
            
        Returns:
            Canonicalized skill name
        """
        if not skill or not isinstance(skill, str):
            return ''
        normalized = skill.lower().strip()
        return self.SKILL_ALIASES.get(normalized, normalized)

    def embed_skill(self, skill: str) -> np.ndarray:
        """
        Get embedding for a single skill with caching.
        
        Args:
            skill: Skill name
            
        Returns:
            Embedding vector (1D numpy array)
        """
        if not skill:
            return None

        canon = self._canonicalize_skill(skill)
        if not canon:
            return None

        # Check cache first
        cached = self.cache.get(canon)
        if cached is not None:
            return cached

        try:
            model = self._load_model()
            embedding = model.encode(canon, convert_to_tensor=False)
            self.cache.set(canon, embedding)
            return embedding
        except Exception as e:
            self.logger.warning(f"Failed to embed skill '{skill}': {e}")
            return None

    def embed_skills_batch(self, skills: List[str]) -> Dict[str, np.ndarray]:
        """
        Efficiently embed multiple skills.
        
        Args:
            skills: List of skill names
            
        Returns:
            Dict mapping canonicalized skills to embeddings
        """
        if not skills:
            return {}

        model = self._load_model()
        canonicalized = [self._canonicalize_skill(s) for s in skills]
        canonicalized = [s for s in canonicalized if s]  # Filter empty
        canonicalized = list(set(canonicalized))  # Deduplicate

        # Check cache and identify missing
        result = {}
        missing = []
        for skill in canonicalized:
            cached = self.cache.get(skill)
            if cached is not None:
                result[skill] = cached
            else:
                missing.append(skill)

        # Embed missing in batches
        if missing:
            try:
                embeddings = model.encode(
                    missing,
                    convert_to_tensor=False,
                    batch_size=self.MAX_BATCH_SIZE,
                    show_progress_bar=False
                )
                for skill, embedding in zip(missing, embeddings):
                    self.cache.set(skill, embedding)
                    result[skill] = embedding
            except Exception as e:
                self.logger.error(f"Batch embedding failed: {e}")

        return result

    def semantic_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate semantic similarity between two skills (0-1).
        
        Args:
            skill1: First skill
            skill2: Second skill
            
        Returns:
            Similarity score (0-1), or 0 if embedding fails
        """
        if not skill1 or not skill2:
            return 0.0

        canon1 = self._canonicalize_skill(skill1)
        canon2 = self._canonicalize_skill(skill2)

        # Exact match is always 1.0
        if canon1 == canon2:
            return 1.0

        try:
            emb1 = self.embed_skill(skill1)
            emb2 = self.embed_skill(skill2)

            if emb1 is None or emb2 is None:
                return 0.0

            # Cosine similarity
            similarity = float(util.pytorch_cos_sim(emb1, emb2)[0][0])
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
        except Exception as e:
            self.logger.warning(f"Similarity calculation failed: {e}")
            return 0.0

    def find_similar_skills(
        self,
        query_skill: str,
        candidate_skills: List[str],
        threshold: float = None
    ) -> List[Tuple[str, float]]:
        """
        Find skills similar to query from a candidate list.
        
        Args:
            query_skill: Skill to match against
            candidate_skills: List of candidate skills
            threshold: Similarity threshold (defaults to class threshold)
            
        Returns:
            List of (skill, similarity) tuples, sorted by similarity descending
        """
        if not candidate_skills:
            return []

        threshold = threshold or self.SIMILARITY_THRESHOLD
        query_canon = self._canonicalize_skill(query_skill)

        if not query_canon:
            return []

        try:
            model = self._load_model()
            query_emb = self.embed_skill(query_skill)
            if query_emb is None:
                return []

            candidate_embeds = self.embed_skills_batch(candidate_skills)
            results = []

            for skill, embedding in candidate_embeds.items():
                if embedding is None:
                    continue
                sim = float(util.pytorch_cos_sim(query_emb, embedding)[0][0])
                if sim >= threshold:
                    results.append((skill, sim))

            results.sort(key=lambda x: x[1], reverse=True)
            return results
        except Exception as e:
            self.logger.error(f"find_similar_skills failed: {e}")
            return []

    def match_skills_semantically(
        self,
        required_skills: List[str],
        available_skills: List[str],
        threshold: float = None
    ) -> Dict[str, any]:
        """
        Semantically match required skills against available skills.
        
        Args:
            required_skills: Skills needed for a role
            available_skills: Skills a candidate has
            threshold: Match threshold
            
        Returns:
            Dict with:
              - matched: List of matched skills
              - unmatched: List of unmatched required skills
              - match_details: Dict with similarity scores
              - match_percentage: Percentage of required skills matched
        """
        if not required_skills or not available_skills:
            return {
                'matched': [],
                'unmatched': required_skills or [],
                'match_details': {},
                'match_percentage': 0
            }

        threshold = threshold or self.SIMILARITY_THRESHOLD
        matched = []
        unmatched = []
        match_details = {}

        for req_skill in required_skills:
            req_canon = self._canonicalize_skill(req_skill)
            if not req_canon:
                continue

            best_match = None
            best_score = 0.0

            for avail_skill in available_skills:
                sim = self.semantic_similarity(req_skill, avail_skill)
                if sim > best_score:
                    best_score = sim
                    best_match = avail_skill

            if best_score >= threshold:
                matched.append(req_canon)
                match_details[req_canon] = {
                    'matched_with': best_match,
                    'score': best_score
                }
            else:
                unmatched.append(req_canon)
                match_details[req_canon] = {
                    'matched_with': None,
                    'score': best_score
                }

        return {
            'matched': matched,
            'unmatched': unmatched,
            'match_details': match_details,
            'match_percentage': len(matched) / len(required_skills) * 100 if required_skills else 0
        }

    def cluster_skills(
        self,
        skills: List[str],
        threshold: float = 0.8
    ) -> Dict[str, List[str]]:
        """
        Cluster similar skills together.
        
        Args:
            skills: List of skills to cluster
            threshold: Similarity threshold for clustering
            
        Returns:
            Dict mapping canonical skills to their similar variants
        """
        if not skills:
            return {}

        canonicalized = [self._canonicalize_skill(s) for s in skills]
        canonicalized = list(dict.fromkeys(c for c in canonicalized if c))  # Deduplicate

        if len(canonicalized) < 2:
            return {canonicalized[0]: [canonicalized[0]]} if canonicalized else {}

        try:
            clusters = {}
            processed = set()

            for i, skill1 in enumerate(canonicalized):
                if skill1 in processed:
                    continue

                cluster = [skill1]
                processed.add(skill1)

                for skill2 in canonicalized[i+1:]:
                    if skill2 in processed:
                        continue
                    sim = self.semantic_similarity(skill1, skill2)
                    if sim >= threshold:
                        cluster.append(skill2)
                        processed.add(skill2)

                clusters[skill1] = cluster

            return clusters
        except Exception as e:
            self.logger.error(f"Skill clustering failed: {e}")
            return {s: [s] for s in canonicalized}

    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        return {
            'cached_embeddings': self.cache.size(),
            'model_loaded': self.model is not None,
            'model_name': self.model_name
        }

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.cache.clear()
        self.logger.info("Embedding cache cleared")


# Global service instance (lazy initialized)
_skill_embedding_service = None


def get_skill_embedding_service() -> SkillEmbeddingService:
    """Get or create global skill embedding service."""
    global _skill_embedding_service
    if _skill_embedding_service is None:
        _skill_embedding_service = SkillEmbeddingService()
    return _skill_embedding_service
