"""
Silent Parser Module for Web Interface
Parser that works without console output for clean web interface experience.
"""
import os
import sys
import json
from typing import Dict, List
from pathlib import Path
import PyPDF2
from docx import Document

# Add project paths
current_dir = Path(__file__).parent
test_env_dir = current_dir.parent
project_root = test_env_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(test_env_dir))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

# Import ML modules
from ml.preprocessing import preprocess_resume_text

class SilentParser:
    """Silent parser that produces no console output."""
    
    def __init__(self):
        self.test_data_path = test_env_dir / "mock_data"
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from different file formats."""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension == '.docx':
                return self._extract_docx_text(file_path)
            elif file_extension == '.txt':
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            raise ValueError(f"Error reading file {file_path}: {e}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_resume_with_gpt(self, text: str) -> dict:
        """Parse resume using mock GPT (silent)."""
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
        """Test parsing with sample resume data (silent)."""
        results = []
        
        for filename in ["sample_resume_1.txt", "sample_resume_2.txt", "sample_resume_3.txt"]:
            file_path = self.test_data_path / filename
            
            if file_path.exists():
                try:
                    result = self.parse_resume(str(file_path))
                    results.append(result)
                except Exception as e:
                    error_result = {"file": filename, "error": str(e)}
                    results.append(error_result)
            else:
                error_result = {"file": filename, "error": "File not found"}
                results.append(error_result)
        
        return results