"""
Mock OpenAI Service for Testing
This replaces the OpenAI API calls for testing purposes.
"""
import json
import random
import re
from typing import List, Dict, Any

class MockOpenAI:
    """Mock OpenAI service that simulates API responses without making actual API calls."""
    
    def __init__(self):
        """Initialize mock OpenAI with predefined responses."""
        self.embedding_dim = 1536  # Standard dimension for text-embedding-3-large
        
    def create_chat_completion(self, **kwargs) -> Dict[str, Any]:
        """Mock chat completion for resume parsing."""
        messages = kwargs.get('messages', [])
        
        # Find the user message with resume text
        resume_text = ""
        for message in messages:
            if message.get('role') == 'user' and 'Extract key details' in message.get('content', ''):
                resume_text = message.get('content', '')
                break
        
        # Simple parsing logic based on resume text
        parsed_resume = self._mock_parse_resume(resume_text)
        
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(parsed_resume, indent=2)
                    }
                }
            ]
        }
    
    def create_embedding(self, **kwargs) -> Dict[str, Any]:
        """Mock embedding creation."""
        text = kwargs.get('input', '')
        
        # Create a deterministic but pseudo-random embedding based on text content
        embedding = self._generate_mock_embedding(text)
        
        return {
            "data": [
                {
                    "embedding": embedding
                }
            ]
        }
    
    def _mock_parse_resume(self, text: str) -> Dict[str, Any]:
        """Extract basic information from resume text using regex."""
        
        # Extract name (assume first line or first capitalized words)
        name_match = re.search(r'^([A-Z][A-Z\s]+)$', text.split('\n')[0])
        name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else ""
        
        # Extract phone
        phone_match = re.search(r'[\(\)\d\s\-\+]+\d{4,}', text)
        phone = phone_match.group(0).strip() if phone_match else ""
        
        # Extract skills (look for common tech skills)
        skills_pattern = r'\b(?:python|javascript|java|react|sql|html|css|node\.?js|azure|aws|git|docker|kubernetes|tensorflow|scikit-learn|machine learning|fastapi|flask|django|mongodb|mysql|postgresql|tableau|pandas|numpy)\b'
        skills = list(set(re.findall(skills_pattern, text.lower())))
        skills = [skill.title() if skill != 'sql' else skill.upper() for skill in skills]
        
        # Extract experience (very basic)
        experience = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['developer', 'engineer', 'analyst', 'scientist']):
                if '|' in line or 'at ' in line.lower():
                    experience.append(line.strip())
        
        # Extract education
        education = []
        for line in lines:
            if any(word in line.lower() for word in ['bachelor', 'master', 'degree', 'university', 'college']):
                education.append(line.strip())
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "experience": experience[:3],  # Limit to 3 entries
            "education": education[:2]      # Limit to 2 entries
        }
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding based on text content."""
        # Use text hash as seed for reproducible results
        seed = hash(text) % (2**32)
        random.seed(seed)
        
        # Generate embedding with some logic based on content
        embedding = []
        
        # Base random values
        for i in range(self.embedding_dim):
            base_value = random.gauss(0, 0.1)
            
            # Add some content-specific patterns
            if 'python' in text.lower():
                base_value += 0.1 * (1 if i % 10 == 0 else 0)
            if 'react' in text.lower():
                base_value += 0.1 * (1 if i % 13 == 0 else 0)  
            if 'machine learning' in text.lower():
                base_value += 0.1 * (1 if i % 17 == 0 else 0)
            if 'javascript' in text.lower():
                base_value += 0.1 * (1 if i % 19 == 0 else 0)
            
            embedding.append(base_value)
        
        # Normalize to unit length (as real embeddings often are)
        length = sum(x*x for x in embedding) ** 0.5
        if length > 0:
            embedding = [x/length for x in embedding]
        
        return embedding

# Mock the openai module structure
class MockChatCompletion:
    @staticmethod
    def create(**kwargs):
        return MockOpenAI().create_chat_completion(**kwargs)

class MockEmbedding:
    @staticmethod
    def create(**kwargs):
        return MockOpenAI().create_embedding(**kwargs)

# Global instances for testing
ChatCompletion = MockChatCompletion()
Embedding = MockEmbedding()

# Configuration (mock)
api_type = "mock"
api_key = "mock-key"
api_base = "https://mock.openai.com/"
api_version = "mock-version"