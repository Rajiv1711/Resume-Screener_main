"""
Test Parser Module
Standalone parser for testing that uses mock services instead of real Azure services.
"""
import os
import sys
import json
from typing import Dict, List

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "test_environment"))

# Mock OpenAI before importing the real modules
import mock_services.mock_openai as openai

# Replace the real openai with mock
sys.modules['openai'] = openai

# Now import the ML modules
from ml.preprocessing import preprocess_resume_text

class TestParser:
    """Test-friendly parser that uses mock services."""
    
    def __init__(self):
        self.test_data_path = os.path.join(
            os.path.dirname(__file__), "..", "mock_data"
        )
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from test files (simplified for testing)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")
    
    def parse_resume_with_gpt(self, text: str) -> dict:
        """Parse resume using mock GPT."""
        few_shot_examples = [
            {
                "role": "system",
                "content": "You are a resume parser that extracts structured information from resumes in JSON format."
            },
            {
                "role": "user", 
                "content": "Extract key details from this resume:\\n\\nJohn Doe\\nEmail: john.doe@example.com\\nPhone: 123-456-7890\\nSkills: Python, Machine Learning, SQL\\nExperience: 2 years at ABC Corp as Data Analyst\\nEducation: B.Tech in Computer Science"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "name": "John Doe",
                    "email": "john.doe@example.com", 
                    "phone": "123-456-7890",
                    "skills": ["Python", "Machine Learning", "SQL"],
                    "experience": ["Data Analyst at ABC Corp (2 years)"],
                    "education": ["B.Tech in Computer Science"]
                }, indent=4)
            }
        ]
        
        few_shot_examples.append({
            "role": "user",
            "content": f"Extract key details from this resume:\\n\\n{text}"
        })
        
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=few_shot_examples,
            temperature=0.0
        )
        
        parsed_output = response["choices"][0]["message"]["content"]
        
        try:
            return json.loads(parsed_output)
        except Exception:
            return {"raw_response": parsed_output}
    
    def parse_resume(self, file_path: str) -> dict:
        """Full pipeline: extract text, preprocess, then parse."""
        raw_text = self.extract_text(file_path)
        
        # Preprocess
        preprocessed = preprocess_resume_text(raw_text)
        
        # GPT parsing
        parsed_resume = self.parse_resume_with_gpt(raw_text)
        
        return {
            "file": os.path.basename(file_path),
            "preprocessed": preprocessed,
            "parsed": parsed_resume
        }
    
    def test_sample_resumes(self) -> List[Dict]:
        """Test parsing with sample resume data."""
        results = []
        
        for filename in ["sample_resume_1.txt", "sample_resume_2.txt", "sample_resume_3.txt"]:
            file_path = os.path.join(self.test_data_path, filename)
            
            if os.path.exists(file_path):
                try:
                    result = self.parse_resume(file_path)
                    results.append(result)
                    print(f"✅ Successfully parsed {filename}")
                except Exception as e:
                    error_result = {"file": filename, "error": str(e)}
                    results.append(error_result)
                    print(f"❌ Error parsing {filename}: {e}")
            else:
                print(f"⚠️  File not found: {filename}")
        
        return results

def main():
    """Test the parser with sample data."""
    print("🧪 Testing Parser with Mock Services")
    print("=" * 50)
    
    parser = TestParser()
    results = parser.test_sample_resumes()
    
    print("\\n📋 Results Summary:")
    print("=" * 50)
    
    for result in results:
        if "error" in result:
            print(f"❌ {result['file']}: {result['error']}")
        else:
            print(f"✅ {result['file']}:")
            print(f"   - Name: {result['parsed'].get('name', 'N/A')}")
            print(f"   - Email: {result['parsed'].get('email', 'N/A')}")
            print(f"   - Skills: {len(result['parsed'].get('skills', []))} found")
            print(f"   - Preprocessed tokens: {len(result['preprocessed'].get('tokens', []))}")
            print(f"   - Extracted skills: {result['preprocessed'].get('skills', [])}")
    
    print("\\n🎉 Parser testing completed!")
    return results

if __name__ == "__main__":
    main()