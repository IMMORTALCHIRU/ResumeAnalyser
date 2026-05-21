"""
Test script for semantic skill embedding integration.
Verifies the SkillEmbeddingService and JobMatchingService work correctly.
"""
import sys
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_service():
    """Test SkillEmbeddingService initialization and basic operations."""
    print("\n" + "="*60)
    print("TEST 1: SkillEmbeddingService Initialization")
    print("="*60)
    
    try:
        from app.services.skill_embedding_service import get_skill_embedding_service
        
        service = get_skill_embedding_service()
        print(f"✓ Service initialized: {service}")
        print(f"✓ Model name: {service.model_name}")
        
        return service
    except Exception as e:
        print(f"✗ Failed to initialize service: {e}")
        sys.exit(1)


def test_skill_canonicalization(service):
    """Test skill name canonicalization."""
    print("\n" + "="*60)
    print("TEST 2: Skill Canonicalization")
    print("="*60)
    
    test_cases = [
        ('nodejs', 'node.js'),
        ('React', 'react'),
        ('C#', 'csharp'),
        ('python', 'python'),
    ]
    
    for input_skill, expected in test_cases:
        canonical = service._canonicalize_skill(input_skill)
        status = "✓" if canonical == expected else "✗"
        print(f"{status} '{input_skill}' → '{canonical}' (expected: '{expected}')")


def test_skill_embedding(service):
    """Test individual skill embedding."""
    print("\n" + "="*60)
    print("TEST 3: Skill Embedding")
    print("="*60)
    
    skills = ['python', 'javascript', 'react', 'docker', 'kubernetes']
    
    try:
        for skill in skills:
            embedding = service.embed_skill(skill)
            if embedding is not None:
                print(f"✓ Embedded '{skill}': shape={embedding.shape}")
            else:
                print(f"✗ Failed to embed '{skill}'")
    except Exception as e:
        print(f"✗ Embedding test failed: {e}")


def test_semantic_similarity(service):
    """Test semantic similarity between skills."""
    print("\n" + "="*60)
    print("TEST 4: Semantic Similarity Scoring")
    print("="*60)
    
    test_pairs = [
        ('python', 'python', 1.0),  # Exact match should be 1.0
        ('node.js', 'nodejs', 0.9),  # Should be very similar
        ('react', 'angular', 0.6),  # Both frontend frameworks, moderately similar
        ('python', 'java', 0.3),  # Different languages, low similarity
        ('docker', 'kubernetes', 0.7),  # Both DevOps tools, moderately similar
    ]
    
    for skill1, skill2, expected_range in test_pairs:
        similarity = service.semantic_similarity(skill1, skill2)
        if isinstance(expected_range, tuple):
            status = "✓" if expected_range[0] <= similarity <= expected_range[1] else "✗"
        else:
            tolerance = 0.1
            status = "✓" if abs(similarity - expected_range) <= tolerance else "~"
        print(f"{status} '{skill1}' ↔ '{skill2}': {similarity:.4f}")


def test_find_similar_skills(service):
    """Test finding similar skills."""
    print("\n" + "="*60)
    print("TEST 5: Find Similar Skills")
    print("="*60)
    
    query = 'machine learning'
    candidates = ['ml', 'deep learning', 'neural networks', 'docker', 'kubernetes', 'tensorflow']
    
    try:
        results = service.find_similar_skills(query, candidates, threshold=0.7)
        print(f"Query: '{query}'")
        print(f"Candidates: {candidates}")
        print(f"Similar skills (threshold=0.7):")
        for skill, similarity in results:
            print(f"  - {skill}: {similarity:.4f}")
    except Exception as e:
        print(f"✗ Find similar skills test failed: {e}")


def test_match_skills_semantically(service):
    """Test semantic skill matching."""
    print("\n" + "="*60)
    print("TEST 6: Semantic Skill Matching")
    print("="*60)
    
    required = ['Python', 'Django', 'PostgreSQL', 'Docker']
    available = ['python', 'flask', 'mysql', 'docker', 'kubernetes']
    
    try:
        result = service.match_skills_semantically(required, available, threshold=0.7)
        print(f"Required: {required}")
        print(f"Available: {available}")
        print(f"\nMatching result:")
        print(f"  Matched: {result['matched']}")
        print(f"  Unmatched: {result['unmatched']}")
        print(f"  Match %: {result['match_percentage']:.1f}%")
    except Exception as e:
        print(f"✗ Skill matching test failed: {e}")


def test_batch_embedding(service):
    """Test batch skill embedding."""
    print("\n" + "="*60)
    print("TEST 7: Batch Skill Embedding")
    print("="*60)
    
    skills = ['python', 'java', 'javascript', 'react', 'angular', 'docker', 'kubernetes']
    
    try:
        result = service.embed_skills_batch(skills)
        print(f"Batch embedded {len(result)} skills:")
        for skill, embedding in result.items():
            if embedding is not None:
                print(f"  ✓ {skill}: {embedding.shape}")
    except Exception as e:
        print(f"✗ Batch embedding test failed: {e}")


def test_job_matching_integration():
    """Test JobMatchingService integration with semantic scoring."""
    print("\n" + "="*60)
    print("TEST 8: JobMatchingService Integration")
    print("="*60)
    
    try:
        # Create mock objects
        class MockResume:
            def __init__(self):
                self.skills = ['Python', 'Django', 'PostgreSQL', 'Docker', 'React']
                self.experience_years = 3
        
        class MockJob:
            def __init__(self):
                self.required_skills = ['Python', 'Flask', 'MySQL']
                self.preferred_skills = ['Docker', 'Kubernetes']
                self.experience_min = 2
                self.experience_max = 7
        
        from app.services.job_matching_service import JobMatchingService
        
        resume = MockResume()
        job = MockJob()
        
        match_result = JobMatchingService.match_score(resume, job)
        
        print(f"Resume Skills: {resume.skills}")
        print(f"Job Requirements:")
        print(f"  Required: {job.required_skills}")
        print(f"  Preferred: {job.preferred_skills}")
        print(f"\nMatch Result:")
        print(f"  Overall Score: {match_result['match_score']}/100")
        print(f"  Keyword Score: {match_result['keyword_score']}/100")
        print(f"  Semantic Score: {match_result['semantic_score']}/100")
        print(f"  Experience Score: {match_result['experience_score']}/20")
        print(f"  Recommendation: {match_result['recommendation']}")
        print(f"  Matched Skills: {match_result['matched_skills']}")
        print(f"  Missing Skills: {match_result['missing_skills']}")
        
    except Exception as e:
        print(f"✗ Job matching integration test failed: {e}")


def test_cache_stats(service):
    """Test cache statistics."""
    print("\n" + "="*60)
    print("TEST 9: Cache Statistics")
    print("="*60)
    
    stats = service.get_cache_stats()
    print(f"Cache Stats:")
    pprint(stats)


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" SEMANTIC SKILL EMBEDDING SERVICE TEST SUITE")
    print("="*70)
    
    # Initialize service
    service = test_embedding_service()
    
    # Run tests
    test_skill_canonicalization(service)
    test_skill_embedding(service)
    test_semantic_similarity(service)
    test_find_similar_skills(service)
    test_match_skills_semantically(service)
    test_batch_embedding(service)
    test_cache_stats(service)
    
    # Integration test
    test_job_matching_integration()
    
    print("\n" + "="*70)
    print(" ALL TESTS COMPLETED")
    print("="*70)
    print("\nFor full usage examples, see app/services/skill_embedding_service.py")


if __name__ == '__main__':
    main()
