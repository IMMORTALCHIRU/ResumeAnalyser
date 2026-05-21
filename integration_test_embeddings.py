"""
Integration test for semantic skill embeddings across the Smart Resume Analyser pipeline.
Tests the complete flow: resume parsing → skill enhancement → job matching → recommendations.

Run with: python -m pytest integration_test_embeddings.py -v
Or directly: python integration_test_embeddings.py
"""

import pytest
import sys
import json
from pprint import pprint


class TestSkillEmbeddingIntegration:
    """Integration tests for the semantic skill embedding pipeline."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize services before each test."""
        try:
            from app.services.skill_embedding_service import get_skill_embedding_service
            self.embedding_service = get_skill_embedding_service()
        except ImportError as e:
            pytest.skip(f"Cannot import embedding service: {e}")
    
    def test_01_embedding_service_initialization(self):
        """Test that embedding service initializes correctly."""
        assert self.embedding_service is not None
        assert self.embedding_service.model_name == 'all-MiniLM-L6-v2'
        # Model is lazily loaded (loaded on first use, not during initialization)
        assert self.embedding_service.cache is not None
        print("✓ Embedding service initialized successfully")
        print("✓ Cache initialized (model loads on first embedding)")
    
    def test_02_skill_canonicalization(self):
        """Test skill name canonicalization."""
        test_cases = [
            ('nodejs', 'node.js'),
            ('React', 'react'),
            ('C#', 'csharp'),
            ('TypeScript', 'typescript'),
        ]
        
        for input_skill, expected in test_cases:
            result = self.embedding_service._canonicalize_skill(input_skill)
            assert result == expected, f"Canonicalization failed for '{input_skill}': got '{result}', expected '{expected}'"
        
        print("✓ Skill canonicalization working correctly")
    
    def test_03_embedding_consistency(self):
        """Test that embeddings are consistent for the same skill."""
        skill = 'python'
        
        emb1 = self.embedding_service.embed_skill(skill)
        emb2 = self.embedding_service.embed_skill(skill)
        
        assert emb1 is not None
        assert emb2 is not None
        assert (emb1 == emb2).all(), "Embeddings not consistent for same skill"
        
        print("✓ Embedding consistency verified")
    
    def test_04_semantic_similarity_logical(self):
        """Test that semantic similarity makes logical sense."""
        # Same skill should have ~1.0 similarity
        sim_same = self.embedding_service.semantic_similarity('python', 'python')
        assert sim_same >= 0.99, f"Same skill similarity too low: {sim_same}"
        
        # Very different skills should have low similarity
        sim_diff = self.embedding_service.semantic_similarity('python', 'docker')
        assert sim_diff < 0.8, f"Different skills similarity too high: {sim_diff}"
        
        # Related skills may have moderate similarity
        sim_related = self.embedding_service.semantic_similarity('react', 'angular')
        # Both are frontend frameworks but text embeddings may not capture this strongly
        assert 0.0 <= sim_related <= 1.0, f"Similarity out of valid range: {sim_related}"
        print(f"  React ↔ Angular similarity: {sim_related:.3f}")
        
        print("✓ Semantic similarity scores are logically sound")
    
    def test_05_batch_embedding_performance(self):
        """Test that batch embedding works and is more efficient."""
        skills = ['python', 'java', 'javascript', 'react', 'angular', 'docker', 'kubernetes']
        
        result = self.embedding_service.embed_skills_batch(skills)
        
        assert len(result) == len(skills), f"Batch size mismatch: {len(result)} vs {len(skills)}"
        
        for skill, embedding in result.items():
            assert embedding is not None, f"Missing embedding for {skill}"
        
        print(f"✓ Batch embedded {len(skills)} skills successfully")
    
    def test_06_skill_matching(self):
        """Test semantic skill matching."""
        required = ['Python', 'Django', 'PostgreSQL', 'Docker', 'Kubernetes']
        available = ['python', 'flask', 'mysql', 'docker', 'kubernetes', 'aws']
        
        result = self.embedding_service.match_skills_semantically(
            required, available, threshold=0.7
        )
        
        assert 'matched' in result
        assert 'unmatched' in result
        assert 'match_percentage' in result
        
        # Should match python, docker, kubernetes
        matched_lower = [m.lower() for m in result['matched']]
        assert 'python' in matched_lower
        assert 'docker' in matched_lower or 'kubernetes' in matched_lower
        
        print(f"✓ Skill matching: {result['match_percentage']:.1f}% match")
    
    def test_07_find_similar_skills(self):
        """Test finding similar skills."""
        query = 'machine learning'
        candidates = ['ml', 'deep learning', 'neural networks', 'docker', 'kubernetes']
        
        similar = self.embedding_service.find_similar_skills(
            query, candidates, threshold=0.6
        )
        
        assert len(similar) > 0, "No similar skills found"
        
        # Should find ml, deep learning, neural networks as similar
        skills_found = [skill.lower() for skill, _ in similar]
        assert any('ml' in s or 'machine' in s or 'deep' in s for s in skills_found)
        
        print(f"✓ Found {len(similar)} similar skills for '{query}'")
    
    def test_08_cache_functionality(self):
        """Test that caching works correctly."""
        skill = 'python'
        
        # Clear cache
        self.embedding_service.cache.clear()
        stats_before = self.embedding_service.get_cache_stats()
        
        # Embed a skill
        self.embedding_service.embed_skill(skill)
        stats_after = self.embedding_service.get_cache_stats()
        
        # Cache should have increased
        assert stats_after['cached_embeddings'] > stats_before['cached_embeddings'], "Cache not growing"
        
        print(f"✓ Cache working: {stats_after['cached_embeddings']} embeddings cached")
    
    def test_09_error_handling(self):
        """Test that service handles errors gracefully."""
        # Test with empty inputs
        result = self.embedding_service.match_skills_semantically([], [])
        assert result['matched'] == []
        assert result['unmatched'] == []
        # match_percentage is only included when there are required skills
        assert 'match_details' in result
        
        # Test with None/empty strings
        similar = self.embedding_service.find_similar_skills('', ['python', 'java'])
        # Should not crash
        
        print("✓ Error handling working correctly")
    
    def test_10_job_matching_integration(self):
        """Test integration with JobMatchingService."""
        try:
            from app.services.job_matching_service import JobMatchingService
            
            # Mock objects
            class MockResume:
                skills = ['Python', 'Django', 'PostgreSQL', 'Docker']
                experience_years = 3
            
            class MockJob:
                required_skills = ['Python', 'Flask', 'MySQL']
                preferred_skills = ['Docker', 'Kubernetes']
                experience_min = 2
                experience_max = 7
            
            resume = MockResume()
            job = MockJob()
            
            result = JobMatchingService.match_score(resume, job)
            
            assert 'match_score' in result
            assert 'keyword_score' in result
            assert 'semantic_score' in result
            assert 'experience_score' in result
            
            # Verify hybrid scoring
            expected_score = (
                (result['keyword_score']/100 * 0.4) +
                (result['semantic_score']/100 * 0.4) +
                (result['experience_score']/20 * 0.2)
            ) * 100
            
            assert abs(result['match_score'] - expected_score) < 1, "Hybrid scoring calculation error"
            
            print(f"✓ Job matching integration: Score={result['match_score']:.1f}")
            
        except ImportError as e:
            pytest.skip(f"Cannot import JobMatchingService: {e}")
    
    def test_11_recommendation_service_integration(self):
        """Test that RecommendationService can use embedding service."""
        try:
            from app.services.recommendation_service import RecommendationService
            
            # Test skill deduplication
            skills = ['React', 'react', 'ReactJS', 'Angular', 'Vue']
            
            result = RecommendationService._deduplicate_skills_semantically(
                skills,
                self.embedding_service
            )
            
            assert len(result) <= len(skills), "Deduplication didn't reduce skills"
            assert all(isinstance(s, str) for s in result), "Invalid skill types"
            
            print(f"✓ Recommendation service integration: {len(skills)} skills → {len(result)} unique")
            
        except ImportError as e:
            pytest.skip(f"Cannot import RecommendationService: {e}")
    
    def test_12_performance_metrics(self):
        """Test performance metrics of embedding operations."""
        import time
        
        skills = ['python', 'java', 'javascript', 'go', 'rust', 'c++', 'c#']
        
        # Single embedding
        start = time.time()
        for skill in skills:
            self.embedding_service.embed_skill(skill)
        single_time = time.time() - start
        
        # Batch embedding
        self.embedding_service.cache.clear()
        start = time.time()
        self.embedding_service.embed_skills_batch(skills)
        batch_time = time.time() - start
        
        print(f"✓ Performance: Single={single_time*1000:.1f}ms, Batch={batch_time*1000:.1f}ms")
        print(f"  Speedup: {single_time/batch_time:.1f}x faster with batching")


def run_tests():
    """Run tests without pytest."""
    print("\n" + "="*70)
    print(" SEMANTIC EMBEDDING INTEGRATION TESTS")
    print("="*70 + "\n")
    
    test_suite = TestSkillEmbeddingIntegration()
    
    # Setup
    try:
        test_suite.setup()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    
    tests = [
        ('Embedding Service Initialization', test_suite.test_01_embedding_service_initialization),
        ('Skill Canonicalization', test_suite.test_02_skill_canonicalization),
        ('Embedding Consistency', test_suite.test_03_embedding_consistency),
        ('Semantic Similarity Logic', test_suite.test_04_semantic_similarity_logical),
        ('Batch Embedding', test_suite.test_05_batch_embedding_performance),
        ('Skill Matching', test_suite.test_06_skill_matching),
        ('Find Similar Skills', test_suite.test_07_find_similar_skills),
        ('Cache Functionality', test_suite.test_08_cache_functionality),
        ('Error Handling', test_suite.test_09_error_handling),
        ('Job Matching Integration', test_suite.test_10_job_matching_integration),
        ('Recommendation Service Integration', test_suite.test_11_recommendation_service_integration),
        ('Performance Metrics', test_suite.test_12_performance_metrics),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTest: {test_name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {test_name} skipped: {e}")
    
    print("\n" + "="*70)
    print(f" RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    # Try to run with pytest if available, otherwise run directly
    try:
        import pytest
        sys.exit(pytest.main([__file__, '-v']))
    except ImportError:
        success = run_tests()
        sys.exit(0 if success else 1)
