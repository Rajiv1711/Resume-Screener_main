#!/usr/bin/env python3
"""
CSV Export Script for Resume Screener Analysis
Exports detailed parsing, embedding, and ranking data to CSV files.
"""

import os
import sys
import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

# Import test modules
from backend_tests.test_parser import TestParser
from backend_tests.test_embedder import TestEmbedder
from backend_tests.test_ranker import TestRanker

def generate_resume_details_data(parsed_resumes, embedder):
    """Generate detailed data for each resume including parsing and embedding info."""
    detailed_data = []
    
    for i, resume in enumerate(parsed_resumes, 1):
        if "error" in resume:
            detailed_data.append({
                'resume_id': i,
                'filename': resume.get('file', 'unknown'),
                'status': 'error',
                'error_message': resume.get('error', 'Unknown error'),
                'gpt_name': None,
                'gpt_email': None,
                'gpt_phone': None,
                'gpt_skills': None,
                'gpt_experience': None,
                'gpt_education': None,
                'cleaned_text_length': 0,
                'total_tokens': 0,
                'preprocessing_skills': None,
                'preprocessing_skills_count': 0,
                'embedding_dimension': 0,
                'embedding_mean': 0,
                'embedding_std': 0,
                'embedding_min': 0,
                'embedding_max': 0,
                'embedding_norm': 0,
                'combined_text_length': 0,
                'cleaned_text_preview': None
            })
            continue
        
        # Get parsed data
        parsed_data = resume.get('parsed', {})
        preprocessed = resume.get('preprocessed', {})
        
        # Generate embedding
        embedding_data = embedder.generate_resume_embedding(preprocessed)
        embedding = np.array(embedding_data['embedding']) if embedding_data['embedding'] else np.array([])
        
        # Skills lists
        gpt_skills = parsed_data.get('skills', [])
        preprocessing_skills = preprocessed.get('skills', [])
        
        detailed_data.append({
            'resume_id': i,
            'filename': resume.get('file', 'unknown'),
            'status': 'success',
            'error_message': None,
            
            # GPT Parsing Results
            'gpt_name': parsed_data.get('name', 'N/A'),
            'gpt_email': parsed_data.get('email', 'N/A'),
            'gpt_phone': parsed_data.get('phone', 'N/A'),
            'gpt_skills': '|'.join(gpt_skills),  # Use | as separator for CSV
            'gpt_skills_count': len(gpt_skills),
            'gpt_experience': '|'.join(parsed_data.get('experience', [])),
            'gpt_education': '|'.join(parsed_data.get('education', [])),
            
            # Preprocessing Results
            'cleaned_text_length': len(preprocessed.get('cleaned_text', '')),
            'total_tokens': len(preprocessed.get('tokens', [])),
            'preprocessing_skills': '|'.join(preprocessing_skills),
            'preprocessing_skills_count': len(preprocessing_skills),
            
            # Embedding Results
            'embedding_dimension': len(embedding),
            'embedding_mean': float(embedding.mean()) if len(embedding) > 0 else 0,
            'embedding_std': float(embedding.std()) if len(embedding) > 0 else 0,
            'embedding_min': float(embedding.min()) if len(embedding) > 0 else 0,
            'embedding_max': float(embedding.max()) if len(embedding) > 0 else 0,
            'embedding_norm': float(np.linalg.norm(embedding)) if len(embedding) > 0 else 0,
            'combined_text_length': len(embedding_data.get('text', '')),
            
            # Text Preview
            'cleaned_text_preview': preprocessed.get('cleaned_text', '')[:200] + '...' if len(preprocessed.get('cleaned_text', '')) > 200 else preprocessed.get('cleaned_text', '')
        })
    
    return detailed_data

def generate_ranking_data(parsed_resumes, ranker, job_descriptions):
    """Generate ranking data for all job-resume combinations."""
    ranking_data = []
    
    for job_key, job_data in job_descriptions.items():
        # Rank all resumes for this job
        ranked_results = ranker.rank_resumes(parsed_resumes, job_data['description'])
        
        # Job description embedding stats
        job_embedding = ranker.embedder.get_text_embedding(job_data['description'])
        job_emb_stats = np.array(job_embedding)
        
        for rank, result in enumerate(ranked_results, 1):
            if "error" in result:
                ranking_data.append({
                    'job_key': job_key,
                    'job_title': job_data['title'],
                    'job_description_preview': job_data['description'][:200] + '...' if len(job_data['description']) > 200 else job_data['description'],
                    'job_required_skills': '|'.join(job_data.get('required_skills', [])),
                    'job_preferred_skills': '|'.join(job_data.get('preferred_skills', [])),
                    'job_embedding_mean': float(job_emb_stats.mean()),
                    'job_embedding_std': float(job_emb_stats.std()),
                    'resume_filename': result.get('file', 'unknown'),
                    'rank': rank,
                    'status': 'error',
                    'error_message': result.get('error', 'Unknown error'),
                    'hybrid_score': 0,
                    'tfidf_score': 0,
                    'embedding_score': 0,
                    'resume_skills': None,
                    'required_skill_matches': None,
                    'preferred_skill_matches': None,
                    'required_skills_coverage_pct': 0,
                    'preferred_skills_coverage_pct': 0,
                    'total_skill_matches': 0
                })
                continue
            
            # Calculate skill matches
            resume_skills = set(result.get('skills', []))
            required_skills = set(job_data.get('required_skills', []))
            preferred_skills = set(job_data.get('preferred_skills', []))
            
            required_matches = resume_skills.intersection(required_skills)
            preferred_matches = resume_skills.intersection(preferred_skills)
            
            # Calculate coverage percentages
            required_coverage = (len(required_matches) / len(required_skills) * 100) if len(required_skills) > 0 else 0
            preferred_coverage = (len(preferred_matches) / len(preferred_skills) * 100) if len(preferred_skills) > 0 else 0
            
            ranking_data.append({
                'job_key': job_key,
                'job_title': job_data['title'],
                'job_description_preview': job_data['description'][:200] + '...' if len(job_data['description']) > 200 else job_data['description'],
                'job_required_skills': '|'.join(job_data.get('required_skills', [])),
                'job_preferred_skills': '|'.join(job_data.get('preferred_skills', [])),
                'job_embedding_mean': float(job_emb_stats.mean()),
                'job_embedding_std': float(job_emb_stats.std()),
                'resume_filename': result.get('file', 'unknown'),
                'rank': rank,
                'status': 'success',
                'error_message': None,
                'hybrid_score': result.get('hybrid_score', 0),
                'tfidf_score': result.get('tfidf_score', 0),
                'embedding_score': result.get('embedding_score', 0),
                'resume_skills': '|'.join(result.get('skills', [])),
                'required_skill_matches': '|'.join(required_matches),
                'preferred_skill_matches': '|'.join(preferred_matches),
                'required_skills_coverage_pct': round(required_coverage, 1),
                'preferred_skills_coverage_pct': round(preferred_coverage, 1),
                'total_skill_matches': len(required_matches) + len(preferred_matches)
            })
    
    return ranking_data

def export_to_csv(data, filename, fieldnames=None):
    """Export data to CSV file."""
    if not data:
        print(f"⚠️  No data to export to {filename}")
        return False
    
    if fieldnames is None:
        fieldnames = data[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ Exported {len(data)} rows to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error exporting to {filename}: {e}")
        return False

def main():
    """Main function to run the export process."""
    print("=" * 80)
    print("📊 RESUME SCREENER - CSV EXPORT")
    print("=" * 80)
    print("Generating CSV files for detailed analysis...")
    
    # Initialize components
    parser = TestParser()
    embedder = TestEmbedder()
    ranker = TestRanker()
    
    # Load job descriptions
    job_desc_file = Path(__file__).parent / "mock_data" / "job_descriptions.json"
    with open(job_desc_file, 'r') as f:
        job_descriptions = json.load(f)
    
    # Process resumes
    print("\n🔄 Processing resumes...")
    parsed_resumes = parser.test_sample_resumes()
    print(f"✅ Processed {len(parsed_resumes)} resumes")
    
    # Generate data for export
    print("\n📋 Generating detailed resume data...")
    resume_details = generate_resume_details_data(parsed_resumes, embedder)
    
    print("🏆 Generating ranking data...")
    ranking_data = generate_ranking_data(parsed_resumes, ranker, job_descriptions)
    
    # Create export directory
    export_dir = Path(__file__).parent / "exports"
    export_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export files
    print(f"\n📁 Exporting to CSV files...")
    
    # 1. Resume Details CSV
    resume_details_file = export_dir / f"resume_details_{timestamp}.csv"
    success1 = export_to_csv(resume_details, resume_details_file)
    
    # 2. Ranking Results CSV
    ranking_file = export_dir / f"ranking_results_{timestamp}.csv"
    success2 = export_to_csv(ranking_data, ranking_file)
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 EXPORT SUMMARY")
    print("=" * 80)
    
    if success1:
        print(f"✅ Resume Details: {resume_details_file}")
        print(f"   📊 {len(resume_details)} resumes with full parsing & embedding data")
    
    if success2:
        print(f"✅ Ranking Results: {ranking_file}")
        print(f"   🏆 {len(ranking_data)} job-resume ranking combinations")
    
    print(f"\n📁 Files saved in: {export_dir}")
    print(f"🕒 Timestamp: {timestamp}")
    
    # Show data preview
    if success1 and resume_details:
        print(f"\n📋 RESUME DETAILS PREVIEW:")
        sample = resume_details[0]
        for key, value in list(sample.items())[:10]:  # Show first 10 fields
            print(f"   {key}: {value}")
        print(f"   ... and {len(sample) - 10} more fields")
    
    if success2 and ranking_data:
        print(f"\n🏆 RANKING RESULTS PREVIEW:")
        sample = ranking_data[0]
        for key, value in list(sample.items())[:10]:  # Show first 10 fields
            print(f"   {key}: {value}")
        print(f"   ... and {len(sample) - 10} more fields")
    
    print("\n🎉 CSV export completed!")
    print("You can now open these files in Excel, Google Sheets, or any CSV viewer")
    print("for detailed analysis and further processing.")
    
    return success1 and success2

if __name__ == "__main__":
    main()