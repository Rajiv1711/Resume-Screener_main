"""
Test Embedder Module
Standalone embedder for testing that uses mock OpenAI service.
"""
import os
import sys
from typing import List, Dict

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "test_environment"))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

class TestEmbedder:
    """Test-friendly embedder using mock OpenAI."""
    
    def __init__(self):
        self.test_data_path = os.path.join(
            os.path.dirname(__file__), "..", "mock_data"
        )
    
    def get_text_embedding(self, text: str, model: str = "text-embedding-3-large") -> List[float]:
        """Generate embedding using mock OpenAI."""
        if not text or len(text.strip()) == 0:
            return []
        
        response = openai.Embedding.create(
            input=text,
            engine=model
        )
        
        return response["data"][0]["embedding"]
    
    def generate_resume_embedding(self, preprocessed_data: Dict) -> Dict:
        """Generate embeddings for preprocessed resume data."""
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
    
    def test_embeddings(self) -> List[Dict]:
        """Test embedding generation with sample texts."""
        test_texts = [
            "Python developer with machine learning experience",
            "React frontend developer with JavaScript skills",
            "Data scientist experienced in TensorFlow and PyTorch",
            "Full-stack developer with Azure cloud experience"
        ]
        
        results = []
        
        print("🧪 Testing Embedding Generation")
        print("=" * 50)
        
        for i, text in enumerate(test_texts, 1):
            try:
                embedding = self.get_text_embedding(text)
                result = {
                    "text": text,
                    "embedding_length": len(embedding),
                    "first_5_values": embedding[:5] if embedding else [],
                    "last_5_values": embedding[-5:] if len(embedding) >= 5 else []
                }
                results.append(result)
                print(f"✅ Text {i}: Generated {len(embedding)}-dimensional embedding")
            except Exception as e:
                error_result = {"text": text, "error": str(e)}
                results.append(error_result)
                print(f"❌ Text {i}: Error - {e}")
        
        return results
    
    def test_similarity(self) -> Dict:
        """Test similarity between similar and dissimilar texts."""
        import numpy as np
        
        # Similar texts
        text1 = "Python developer with machine learning experience"
        text2 = "Machine learning engineer with Python expertise" 
        
        # Dissimilar texts
        text3 = "Frontend React developer with JavaScript skills"
        
        try:
            emb1 = self.get_text_embedding(text1)
            emb2 = self.get_text_embedding(text2)
            emb3 = self.get_text_embedding(text3)
            
            # Calculate cosine similarities
            def cosine_similarity(v1, v2):
                v1, v2 = np.array(v1), np.array(v2)
                return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            
            sim_12 = cosine_similarity(emb1, emb2)  # Should be higher
            sim_13 = cosine_similarity(emb1, emb3)  # Should be lower
            
            return {
                "similar_texts_similarity": sim_12,
                "dissimilar_texts_similarity": sim_13,
                "similarity_difference": sim_12 - sim_13,
                "test_passed": sim_12 > sim_13
            }
            
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test the embedder with sample data."""
    print("🧪 Testing Embedder with Mock OpenAI")
    print("=" * 50)
    
    embedder = TestEmbedder()
    
    # Test basic embedding generation
    embedding_results = embedder.test_embeddings()
    
    print("\\n🔗 Testing Similarity Logic")
    print("=" * 50)
    
    # Test similarity
    similarity_results = embedder.test_similarity()
    
    if "error" in similarity_results:
        print(f"❌ Similarity test error: {similarity_results['error']}")
    else:
        print(f"✅ Similar texts similarity: {similarity_results['similar_texts_similarity']:.4f}")
        print(f"✅ Dissimilar texts similarity: {similarity_results['dissimilar_texts_similarity']:.4f}")
        print(f"✅ Difference: {similarity_results['similarity_difference']:.4f}")
        print(f"✅ Test passed: {similarity_results['test_passed']}")
    
    print("\\n📊 Embedding Results Summary:")
    print("=" * 50)
    
    for i, result in enumerate(embedding_results, 1):
        if "error" in result:
            print(f"❌ Test {i}: {result['error']}")
        else:
            print(f"✅ Test {i}: {result['embedding_length']}-D embedding for '{result['text'][:50]}...'")
    
    print("\\n🎉 Embedder testing completed!")
    return {"embeddings": embedding_results, "similarity": similarity_results}

if __name__ == "__main__":
    main()