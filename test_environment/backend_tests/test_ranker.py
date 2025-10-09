"""
Test Ranker Module
Standalone ranker for testing that uses mock services and sample data.
"""
import os
import sys
import json
import numpy as np
from typing import List, Dict

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "test_environment"))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

# Import test modules
from backend_tests.test_parser import TestParser
from backend_tests.test_embedder import TestEmbedder

# Import ML modules
from ml.hybrid_ranker import TfidfHybridScorer, combine_hybrid_scores

class TestRanker:
    """Test-friendly ranker using mock services."""
    
    def __init__(self):
        self.test_data_path = os.path.join(
            os.path.dirname(__file__), "..", "mock_data"
        )
        self.parser = TestParser()
        self.embedder = TestEmbedder()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        v1, v2 = np.array(vec1), np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def load_job_descriptions(self) -> Dict:
        """Load job descriptions from test data."""
        job_desc_file = os.path.join(self.test_data_path, "job_descriptions.json")
        try:
            with open(job_desc_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading job descriptions: {e}")
            return {}
    
    def rank_resumes(self, resume_list: List[Dict], job_description: str, alpha: float = 0.7) -> List[Dict]:
        """Rank resumes using hybrid scoring."""
        
        # Generate embedding for job description
        job_embedding = self.embedder.get_text_embedding(job_description)
        
        ranked_results = []
        
        # Prepare TF-IDF scorer
        tfidf = TfidfHybridScorer()
        resumes_clean_text = []
        preprocessed_cache = []
        
        for resume in resume_list:
            try:
                # Generate embedding for resume
                preprocessed = resume.get("preprocessed", {})
                embedding_data = self.embedder.generate_resume_embedding(preprocessed)
                resume_embedding = embedding_data["embedding"]
                
                # Compute similarity score
                score = self.cosine_similarity(job_embedding, resume_embedding)
                
                # Collect TF-IDF inputs
                resumes_clean_text.append(preprocessed.get("cleaned_text", ""))
                preprocessed_cache.append(preprocessed)
                
                ranked_results.append({
                    "file": resume.get("file"),
                    "embedding_score": round(score, 4),
                    "skills": preprocessed.get("skills", []),
                    "parsed": resume.get("parsed", {}),
                })
                
            except Exception as e:
                ranked_results.append({
                    "file": resume.get("file"),
                    "error": str(e)
                })
        
        # Compute TF-IDF scores
        try:
            tfidf_scores = tfidf.score(resumes_clean_text, job_description)
        except Exception as e:
            print(f"TF-IDF scoring error: {e}")
            tfidf_scores = [0.0 for _ in ranked_results]
        
        # Normalize embedding scores and combine
        embed_scores = [max(0.0, min(1.0, (r.get("embedding_score", 0.0) + 1.0) / 2.0)) for r in ranked_results]
        hybrid_scores = combine_hybrid_scores(embed_scores, tfidf_scores, alpha=alpha)
        
        # Add scores to results
        for r, h, t in zip(ranked_results, hybrid_scores, tfidf_scores):
            if "error" not in r:
                r["tfidf_score"] = round(float(t), 4)
                r["hybrid_score"] = round(float(h), 4)
        
        # Sort by hybrid score
        ranked_results.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
        return ranked_results
    
    def test_ranking_pipeline(self) -> Dict:
        """Test the complete ranking pipeline."""
        print("🧪 Testing Complete Ranking Pipeline")
        print("=" * 50)
        
        # Parse sample resumes
        print("📄 Parsing sample resumes...")
        parsed_resumes = self.parser.test_sample_resumes()
        
        if not parsed_resumes:
            return {"error": "No resumes parsed successfully"}
        
        # Load job descriptions
        job_descriptions = self.load_job_descriptions()
        
        if not job_descriptions:
            return {"error": "No job descriptions loaded"}
        
        results = {}
        
        # Test ranking for each job description
        for job_key, job_data in job_descriptions.items():
            print(f"\\n🎯 Testing ranking for: {job_data['title']}")
            print("-" * 40)
            
            try:
                ranked_results = self.rank_resumes(
                    parsed_resumes,
                    job_data['description']
                )
                
                results[job_key] = {
                    "job_title": job_data['title'],
                    "ranked_resumes": ranked_results,
                    "total_resumes": len([r for r in ranked_results if "error" not in r])
                }
                
                # Print ranking results
                print(f"✅ Successfully ranked {results[job_key]['total_resumes']} resumes")
                for i, resume in enumerate(ranked_results[:3], 1):  # Show top 3
                    if "error" not in resume:
                        print(f"   {i}. {resume['file']} - Hybrid: {resume['hybrid_score']:.3f}")
                
            except Exception as e:
                results[job_key] = {"error": str(e)}
                print(f"❌ Error ranking for {job_data['title']}: {e}")
        
        return results
    
    def test_scoring_methods(self) -> Dict:
        """Test different scoring methods."""
        print("\\n🔬 Testing Scoring Methods")
        print("=" * 50)
        
        # Sample texts for testing
        resume_texts = [
            "Python developer with machine learning experience using TensorFlow and scikit-learn",
            "React frontend developer with JavaScript and TypeScript skills",
            "Full-stack developer with Python, React, and cloud deployment experience"
        ]
        
        job_desc = "Looking for a Python developer with machine learning expertise"
        
        results = {}
        
        try:
            # Test TF-IDF scoring
            tfidf = TfidfHybridScorer()
            tfidf_scores = tfidf.score(resume_texts, job_desc)
            
            # Test embedding scoring
            job_embedding = self.embedder.get_text_embedding(job_desc)
            embedding_scores = []
            
            for text in resume_texts:
                resume_embedding = self.embedder.get_text_embedding(text)
                score = self.cosine_similarity(job_embedding, resume_embedding)
                # Normalize to [0,1]
                normalized_score = max(0.0, min(1.0, (score + 1.0) / 2.0))
                embedding_scores.append(normalized_score)
            
            # Test hybrid scoring
            hybrid_scores = combine_hybrid_scores(embedding_scores, tfidf_scores, alpha=0.7)
            
            results = {
                "tfidf_scores": [round(s, 4) for s in tfidf_scores],
                "embedding_scores": [round(s, 4) for s in embedding_scores],
                "hybrid_scores": [round(s, 4) for s in hybrid_scores],
                "resume_texts": resume_texts,
                "job_description": job_desc
            }
            
            # Print comparison
            print("Resume Rankings Comparison:")
            for i, text in enumerate(resume_texts):
                print(f"\\nResume {i+1}: '{text[:50]}...'")
                print(f"  TF-IDF: {results['tfidf_scores'][i]:.3f}")
                print(f"  Embedding: {results['embedding_scores'][i]:.3f}")
                print(f"  Hybrid: {results['hybrid_scores'][i]:.3f}")
            
        except Exception as e:
            results = {"error": str(e)}
            print(f"❌ Error in scoring methods test: {e}")
        
        return results

def main():
    """Test the complete ranking system."""
    print("🧪 Testing Ranker with Mock Services")
    print("=" * 50)
    
    ranker = TestRanker()
    
    # Test complete pipeline
    pipeline_results = ranker.test_ranking_pipeline()
    
    # Test scoring methods
    scoring_results = ranker.test_scoring_methods()
    
    print("\\n📊 Final Results Summary:")
    print("=" * 50)
    
    # Pipeline results
    if "error" in pipeline_results:
        print(f"❌ Pipeline test failed: {pipeline_results['error']}")
    else:
        print(f"✅ Pipeline test completed for {len(pipeline_results)} job descriptions")
        for job_key, result in pipeline_results.items():
            if "error" not in result:
                print(f"   - {result['job_title']}: {result['total_resumes']} resumes ranked")
    
    # Scoring results
    if "error" in scoring_results:
        print(f"❌ Scoring methods test failed: {scoring_results['error']}")
    else:
        print(f"✅ Scoring methods test completed")
        print(f"   - TF-IDF, Embedding, and Hybrid scores generated successfully")
    
    print("\\n🎉 Ranker testing completed!")
    
    return {
        "pipeline": pipeline_results,
        "scoring": scoring_results
    }

if __name__ == "__main__":
    main()