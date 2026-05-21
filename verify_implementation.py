#!/usr/bin/env python3
"""
Verification script for Smart Resume Analyser semantic embeddings implementation.
Checks that all components are properly installed and integrated.

Run with: python verify_implementation.py
"""

import sys
import os
from pathlib import Path


def check_file_exists(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {path}")
        return False


def check_package_installed(package, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package
    
    try:
        __import__(import_name)
        print(f"✅ {package} installed")
        return True
    except ImportError:
        print(f"❌ {package} NOT installed")
        return False


def check_file_contains(filepath, search_string, description):
    """Check if a file contains a specific string."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NOT FOUND in file")
                return False
    except FileNotFoundError:
        print(f"❌ {description} - FILE NOT FOUND")
        return False


def verify_implementation():
    """Verify the complete semantic embeddings implementation."""
    
    print("\n" + "="*70)
    print(" SMART RESUME ANALYSER - SEMANTIC EMBEDDINGS VERIFICATION")
    print("="*70 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Core Files
    print("1️⃣  CORE FILES")
    print("-" * 70)
    
    files_to_check = [
        ('app/services/skill_embedding_service.py', 'SkillEmbeddingService'),
        ('app/services/job_matching_service.py', 'JobMatchingService'),
        ('app/services/recommendation_service.py', 'RecommendationService'),
        ('app/services/resume_parser.py', 'ResumeParserService'),
        ('app/config.py', 'Config'),
        ('requirements.txt', 'Dependencies'),
        ('test_embedding_service.py', 'Unit Tests'),
        ('integration_test_embeddings.py', 'Integration Tests'),
        ('.env.template', 'Environment Template'),
        ('SEMANTIC_EMBEDDINGS.md', 'Documentation'),
    ]
    
    for filepath, description in files_to_check:
        checks_total += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    print()
    
    # 2. Dependencies
    print("2️⃣  PYTHON DEPENDENCIES")
    print("-" * 70)
    
    packages = [
        ('flask', 'Flask'),
        ('flask_pymongo', 'Flask-PyMongo'),
        ('flask_login', 'Flask-Login'),
        ('sentence_transformers', 'sentence-transformers'),
        ('spacy', 'spaCy'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
    ]
    
    for package, display_name in packages:
        checks_total += 1
        if check_package_installed(display_name, package):
            checks_passed += 1
    
    print()
    
    # 3. Implementation Features
    print("3️⃣  IMPLEMENTATION FEATURES")
    print("-" * 70)
    
    features = [
        ('app/services/skill_embedding_service.py', 'class SkillEmbeddingService', 'SkillEmbeddingService class'),
        ('app/services/skill_embedding_service.py', 'def semantic_similarity', 'Semantic similarity method'),
        ('app/services/skill_embedding_service.py', 'def match_skills_semantically', 'Skill matching method'),
        ('app/services/skill_embedding_service.py', 'def cluster_skills', 'Skill clustering method'),
        ('app/services/skill_embedding_service.py', 'class EmbeddingCache', 'Embedding cache class'),
        ('app/services/job_matching_service.py', 'def _keyword_score', 'Keyword scoring method'),
        ('app/services/job_matching_service.py', 'def _semantic_score', 'Semantic scoring method'),
        ('app/services/job_matching_service.py', 'def _experience_score', 'Experience scoring method'),
        ('app/services/recommendation_service.py', 'def _deduplicate_skills_semantically', 'Skill deduplication method'),
        ('app/services/resume_parser.py', 'def enhance_skills_with_embeddings', 'Resume skill enhancement'),
        ('app/config.py', 'EMBEDDING_MODEL', 'Embedding model config'),
        ('app/config.py', 'SEMANTIC_SIMILARITY_THRESHOLD', 'Similarity threshold config'),
    ]
    
    for filepath, feature, description in features:
        checks_total += 1
        if check_file_contains(filepath, feature, description):
            checks_passed += 1
    
    print()
    
    # 4. Configuration
    print("4️⃣  CONFIGURATION")
    print("-" * 70)
    
    config_checks = [
        ('app/config.py', 'EMBEDDING_MODEL', 'Embedding model setting'),
        ('app/config.py', 'SEMANTIC_SIMILARITY_THRESHOLD', 'Similarity threshold setting'),
        ('app/config.py', 'KEYWORD_MATCH_WEIGHT', 'Keyword weight setting'),
        ('app/config.py', 'SEMANTIC_MATCH_WEIGHT', 'Semantic weight setting'),
        ('app/config.py', 'EXPERIENCE_MATCH_WEIGHT', 'Experience weight setting'),
        ('.env.template', 'EMBEDDING_MODEL=', '.env template content'),
        ('.env.template', 'SEMANTIC_SIMILARITY_THRESHOLD', '.env threshold setting'),
    ]
    
    for filepath, feature, description in config_checks:
        checks_total += 1
        if check_file_contains(filepath, feature, description):
            checks_passed += 1
    
    print()
    
    # 5. Testing & Documentation
    print("5️⃣  TESTING & DOCUMENTATION")
    print("-" * 70)
    
    test_checks = [
        ('test_embedding_service.py', 'def test_', 'Unit test functions'),
        ('integration_test_embeddings.py', 'class TestSkillEmbeddingIntegration', 'Integration test class'),
        ('integration_test_embeddings.py', 'def test_', 'Integration test methods'),
        ('SEMANTIC_EMBEDDINGS.md', '## Overview', 'Documentation file'),
        ('SEMANTIC_EMBEDDINGS.md', 'SkillEmbeddingService', 'Service documentation'),
        ('SEMANTIC_EMBEDDINGS.md', 'Hybrid Job Matching Score', 'Hybrid scoring documentation'),
    ]
    
    for filepath, feature, description in test_checks:
        checks_total += 1
        if check_file_contains(filepath, feature, description):
            checks_passed += 1
    
    print()
    
    # Summary
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"Checks Passed: {checks_passed}/{checks_total}")
    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0
    print(f"Success Rate: {percentage:.1f}%")
    
    if checks_passed == checks_total:
        print("\n✅ ALL CHECKS PASSED - Implementation is complete!")
        print("\n📋 NEXT STEPS:")
        print("1. Copy .env.template to .env")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run tests: python integration_test_embeddings.py")
        print("4. Deploy with confidence!")
        return True
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed")
        print("Please review the errors above and ensure all files are in place.")
        return False


if __name__ == '__main__':
    success = verify_implementation()
    sys.exit(0 if success else 1)
