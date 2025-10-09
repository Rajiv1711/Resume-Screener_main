"""
Silent Ranker Module for Web Interface
Ranker that works without console output for clean web interface experience.
"""
import os
import sys
import json
import numpy as np
from typing import List, Dict
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
test_env_dir = current_dir.parent
project_root = test_env_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(test_env_dir))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

# Import silent modules
from silent_parser import SilentParser
from silent_embedder import SilentEmbedder

# Import ML modules
from ml.hybrid_ranker import TfidfHybridScorer, combine_hybrid_scores

class SilentRanker:
    """Silent ranker using mock services (no console output)."""
    
    def __init__(self):
        self.test_data_path = test_env_dir / "mock_data"
        self.parser = SilentParser()
        self.embedder = SilentEmbedder()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        v1, v2 = np.array(vec1), np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def load_job_descriptions(self) -> Dict:
        """Load job descriptions from test data."""
        job_desc_file = self.test_data_path / "job_descriptions.json"
        with open(job_desc_file, 'r') as f:
            return json.load(f)
    
    def rank_resumes(self, resume_list: List[Dict], job_description: str, alpha: float = 0.7) -> List[Dict]:
        """Rank resumes using hybrid scoring (silent)."""
        
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
        except Exception:
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