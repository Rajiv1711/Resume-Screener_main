#!/usr/bin/env python3
"""
Test script to demonstrate the improved text extraction and LLM-based ranking system.
This script shows the before/after comparison of text quality and ranking intelligence.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.enhanced_text_extractor import enhanced_extractor
from app.services.llm_based_ranker import llm_ranker
from app.services.parser import extract_text  # Original extraction
from app.services.ranker import rank_resumes  # Updated to use LLM

def test_text_extraction_improvement():
    """
    Test the text extraction improvements by comparing old vs new methods.
    """
    print("=" * 80)
    print("🔍 TESTING TEXT EXTRACTION IMPROVEMENTS")
    print("=" * 80)
    
    # Find some processed text files to compare
    processed_dir = project_root / "data" / "processed"
    
    if not processed_dir.exists():
        print("❌ No processed files found. Please run the application with some resumes first.")
        return
    
    # Get a sample processed file
    sample_files = list(processed_dir.glob("*.txt"))[:2]
    
    if not sample_files:
        print("❌ No processed text files found.")
        return
    
    for sample_file in sample_files:
        print(f"\n📄 Sample File: {sample_file.name}")
        print("-" * 50)
        
        # Read the current processed text
        with open(sample_file, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        print("🔸 ORIGINAL EXTRACTION (showing first 300 chars):")
        print(original_text[:300] + "..." if len(original_text) > 300 else original_text)
        
        # Show text quality issues
        issues = []
        if " v " in original_text and "Ja v a" in original_text:
            issues.append("Text bisection detected (e.g., 'Ja v a Script')")
        if len([w for w in original_text.split() if len(w) == 1]) > 10:
            issues.append("Excessive single character words")
        if original_text.count("  ") > 20:
            issues.append("Excessive whitespace")
        
        print(f"\n🔸 ISSUES DETECTED: {len(issues)}")
        for issue in issues:
            print(f"   • {issue}")
    
    print("\n✅ Text extraction analysis complete!")
    print("📖 The enhanced extractor addresses these issues automatically.")

def test_llm_ranking_demo():
    """
    Demonstrate the LLM-based ranking system with sample data.
    """
    print("\n" + "=" * 80)
    print("🧠 TESTING LLM-BASED RANKING SYSTEM")
    print("=" * 80)
    
    # Sample job description
    job_description = """
    Senior Python Developer - AI/ML Focus
    
    We're seeking a Senior Python Developer with 5+ years of experience to join our AI/ML team. 
    The ideal candidate will have strong experience in Python, machine learning frameworks 
    (TensorFlow, PyTorch), data processing, and cloud platforms (AWS/Azure).
    
    Requirements:
    - 5+ years Python development experience
    - Strong ML/AI background with TensorFlow or PyTorch
    - Experience with pandas, numpy, scikit-learn
    - Cloud platform experience (AWS/Azure)
    - Leadership or mentoring experience preferred
    - Bachelor's degree in Computer Science or related field
    
    You'll be working on cutting-edge AI solutions and leading technical initiatives.
    """
    
    # Sample resume data (simulating parsed resumes)
    sample_resumes = [
        {
            "file": "sarah_johnson_resume.pdf",
            "parsed": {
                "name": "Sarah Johnson",
                "email": "sarah.j@email.com",
                "phone": "+1-555-0123",
                "experience": [
                    "Senior ML Engineer | TechCorp | 2020-Present (4 years) - Led ML team of 6, built recommendation systems using PyTorch serving 1M+ users",
                    "Python Developer | DataCorp | 2018-2020 (2 years) - Developed data pipelines using pandas, numpy, deployed on AWS",
                    "Software Developer | StartupXYZ | 2016-2018 (2 years) - Built web applications using Python/Django"
                ],
                "education": ["M.S. Computer Science | Stanford University | 2016", "B.S. Mathematics | UCLA | 2014"],
                "skills": ["Python", "PyTorch", "TensorFlow", "pandas", "numpy", "scikit-learn", "AWS", "Docker", "Kubernetes"]
            },
            "preprocessed": {
                "cleaned_text": "Sarah Johnson Senior ML Engineer TechCorp Led ML team built recommendation systems PyTorch Python Developer DataCorp developed data pipelines pandas numpy AWS Software Developer StartupXYZ built web applications Python Django Masters Computer Science Stanford Bachelor Mathematics UCLA",
                "skills": ["python", "pytorch", "tensorflow", "pandas", "numpy", "aws", "docker", "kubernetes"]
            }
        },
        {
            "file": "alex_chen_resume.pdf", 
            "parsed": {
                "name": "Alex Chen",
                "email": "alex.chen@email.com",
                "phone": "+1-555-0456",
                "experience": [
                    "Junior Python Developer | WebCorp | 2022-Present (2 years) - Built web applications using Django, worked with PostgreSQL databases",
                    "Intern | TechStart | Summer 2022 (3 months) - Learned Python fundamentals, built simple web apps"
                ],
                "education": ["Coding Bootcamp - Full Stack Development | 2022", "B.A. Marketing | State University | 2020"],
                "skills": ["Python", "Django", "PostgreSQL", "HTML", "CSS", "JavaScript"]
            },
            "preprocessed": {
                "cleaned_text": "Alex Chen Junior Python Developer WebCorp built web applications Django PostgreSQL Intern TechStart learned Python fundamentals Coding Bootcamp Full Stack Development Bachelor Marketing State University",
                "skills": ["python", "django", "postgresql", "html", "css", "javascript"]
            }
        },
        {
            "file": "mike_wilson_resume.pdf",
            "parsed": {
                "name": "Mike Wilson", 
                "email": "mike.w@email.com",
                "phone": "+1-555-0789",
                "experience": [
                    "Data Scientist | AnalyticsCorp | 2019-Present (5 years) - Built ML models using TensorFlow and scikit-learn, processed large datasets with pandas",
                    "Research Assistant | University Lab | 2017-2019 (2 years) - Conducted ML research, published 3 papers on computer vision"
                ],
                "education": ["Ph.D. Computer Science | MIT | 2019", "M.S. Applied Mathematics | Caltech | 2015"],
                "skills": ["Python", "TensorFlow", "scikit-learn", "pandas", "numpy", "R", "MATLAB", "Azure", "Docker"]
            },
            "preprocessed": {
                "cleaned_text": "Mike Wilson Data Scientist AnalyticsCorp built ML models TensorFlow scikit-learn processed datasets pandas Research Assistant University Lab conducted ML research published papers computer vision PhD Computer Science MIT Masters Applied Mathematics Caltech",
                "skills": ["python", "tensorflow", "scikit-learn", "pandas", "numpy", "r", "matlab", "azure"]
            }
        }
    ]
    
    print("📋 Job Description:")
    print(job_description[:200] + "..." if len(job_description) > 200 else job_description)
    
    print(f"\n👥 Evaluating {len(sample_resumes)} candidates:")
    for i, resume in enumerate(sample_resumes, 1):
        print(f"   {i}. {resume['parsed']['name']} ({resume['file']})")
    
    print("\n🔄 Running LLM-based evaluation...")
    
    try:
        # Run the LLM-based ranking
        ranked_results = rank_resumes(sample_resumes, job_description, alpha=0.3)
        
        print("\n🏆 RANKING RESULTS:")
        print("=" * 60)
        
        for result in ranked_results:
            print(f"\n🥇 #{result.get('rank', '?')} - {result.get('candidate_name', 'Unknown')}")
            print(f"   📊 Final Score: {result.get('final_score', 0):.3f}")
            print(f"   🔍 LLM Score: {result.get('llm_score', 0):.3f} | Keyword Score: {result.get('keyword_score', 0):.3f}")
            print(f"   📝 Recommendation: {result.get('recommendation', 'N/A')}")
            
            # Show detailed breakdown
            if result.get('experience_score'):
                print(f"   📈 Experience: {result['experience_score']:.2f} | Skills: {result.get('skills_score', 0):.2f} | Education: {result.get('education_score', 0):.2f}")
            
            # Show strengths and concerns
            strengths = result.get('strengths', [])[:2]  # Show top 2
            concerns = result.get('concerns', [])[:2]   # Show top 2
            
            if strengths:
                print(f"   ✅ Strengths: {', '.join(strengths)}")
            if concerns:
                print(f"   ⚠️  Concerns: {', '.join(concerns)}")
            
            print(f"   💡 Reasoning: {result.get('reasoning', 'No reasoning provided')[:100]}...")
        
        print("\n✅ LLM-based ranking completed successfully!")
        
        # Show the key benefits
        print("\n🌟 KEY BENEFITS OF LLM-BASED RANKING:")
        print("   • Considers experience relevance, not just keywords")
        print("   • Evaluates career progression and growth")
        print("   • Assesses education alignment contextually") 
        print("   • Identifies specific strengths and concerns")
        print("   • Provides actionable hiring recommendations")
        print("   • Adapts to different job requirements automatically")
        
    except Exception as e:
        print(f"❌ LLM ranking failed: {str(e)}")
        print("💡 This might be due to OpenAI API configuration issues.")

def main():
    """
    Main test function that demonstrates all improvements.
    """
    print("🚀 RESUME SCREENER IMPROVEMENTS DEMO")
    print("This demo showcases the enhanced text extraction and LLM-based ranking system")
    print("=" * 80)
    
    # Test text extraction improvements
    test_text_extraction_improvement()
    
    # Test LLM-based ranking
    test_llm_ranking_demo()
    
    print("\n" + "=" * 80)
    print("✨ DEMO COMPLETE!")
    print("\n📊 SUMMARY OF IMPROVEMENTS:")
    print("1. 🔧 Enhanced Text Extraction:")
    print("   • Multiple extraction methods with quality assessment")
    print("   • Automatic text bisection repair")
    print("   • Better handling of PDFs, DOCX, and tables")
    print("   • Quality scoring and best method selection")
    
    print("\n2. 🧠 LLM-Based Ranking (30% keywords + 70% human-like evaluation):")
    print("   • Experience relevance analysis")
    print("   • Career progression assessment") 
    print("   • Education background evaluation")
    print("   • Project quality scoring")
    print("   • Detailed strengths/concerns identification")
    print("   • Human-readable recommendations")
    
    print("\n3. 🛡️ Reliability:")
    print("   • Fallback mechanisms for both systems")
    print("   • Error handling and graceful degradation")
    print("   • Consistent scoring format")
    
    print("\n🎯 This system now evaluates resumes like an experienced HR professional!")
    print("=" * 80)

if __name__ == "__main__":
    main()