"""
Silent Embedder Module for Web Interface
Embedder that works without console output for clean web interface experience.
"""
import os
import sys
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

class SilentEmbedder:
    """Silent embedder using mock OpenAI (no console output)."""
    
    def __init__(self):
        self.test_data_path = test_env_dir / "mock_data"
    
    def get_text_embedding(self, text: str, model: str = "text-embedding-3-large") -> List[float]:
        """Generate embedding using mock OpenAI (silent)."""
        if not text or len(text.strip()) == 0:
            return []
        
        response = openai.Embedding.create(
            input=text,
            engine=model
        )
        
        return response["data"][0]["embedding"]
    
    def generate_resume_embedding(self, preprocessed_data: Dict) -> Dict:
        """Generate embeddings for preprocessed resume data (silent)."""
        cleaned_text = preprocessed_data.get("cleaned_text", "")
        skills = " ".join(preprocessed_data.get("skills", []))
        
        # Combine text and skills
        combined_text = f"{cleaned_text}\\nSkills: {skills}"
        
        embedding = self.get_text_embedding(combined_text)
        
        return {
            "text": combined_text,
            "embedding": embedding,
            "vector_length": len(embedding)
        }