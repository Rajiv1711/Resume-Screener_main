import os
import zipfile
import tempfile
import docx2txt
import PyPDF2
import openai
import json
import io

from ml.preprocessing import preprocess_resume_text
from app.services.blob_storage import blob_storage

# Configure OpenAI / Azure OpenAI
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="C6GA6hGNxN48a6A2jR6JyhDYTzbnwfvHJuYTM2FUz4olCPa2mBq0JQQJ99BIAC77bzfXJ3w3AAABACOGAz1x",
    api_version="2024-12-01-preview",
    azure_endpoint="https://parseroa.openai.azure.com/"
)

UPLOAD_DIR = "data/processed"


def extract_text(file_path: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT."""
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == ".docx":
        text = docx2txt.process(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return text


def extract_text_from_blob(blob_name: str, user_id: str = None) -> str:
    """Extract raw text from a blob in Azure Blob Storage."""
    text = ""
    ext = os.path.splitext(blob_name)[1].lower()
    
    # Download blob content to memory
    if user_id:
        file_content = blob_storage.download_file_user(blob_name, user_id)
    else:
        file_content = blob_storage.download_file(blob_name)
    file_stream = io.BytesIO(file_content)

    if ext == ".pdf":
        reader = PyPDF2.PdfReader(file_stream)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == ".docx":
        # For docx, we need to save to a temporary file since docx2txt.process expects a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            text = docx2txt.process(temp_path)
        finally:
            os.unlink(temp_path)
    elif ext == ".txt":
        text = file_content.decode('utf-8')
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return text


def parse_resume_with_gpt(text: str) -> dict:
    """Parse resume text using GPT-3.5 Turbo with few-shot prompting."""
    few_shot_examples = [
        {
            "role": "system",
            "content": "You are a resume parser that extracts structured information from resumes in JSON format."
        },
        {
            "role": "user",
            "content": "Extract key details from this resume:\n\nJohn Doe\nEmail: john.doe@example.com\nPhone: 123-456-7890\nSkills: Python, Machine Learning, SQL\nExperience: 2 years at ABC Corp as Data Analyst\nEducation: B.Tech in Computer Science"
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

    # Add the actual resume
    few_shot_examples.append({
        "role": "user",
        "content": f"Extract key details from this resume:\n\n{text}"
    })

    response = client.chat.completions.create(
        model="gpt-35-turbo",  # Azure deployment name
        messages=few_shot_examples,
        temperature=0.0
    )

    parsed_output = response.choices[0].message.content

    try:
        return json.loads(parsed_output)
    except Exception:
        return {"raw_response": parsed_output}


def parse_resume(file_path: str) -> dict:
    """Full pipeline: extract raw text, preprocess, then parse with GPT."""
    raw_text = extract_text(file_path)

    # Save extracted raw text
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    processed_file = os.path.join(UPLOAD_DIR, os.path.basename(file_path) + ".txt")
    with open(processed_file, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # Step 1: Preprocess
    preprocessed = preprocess_resume_text(raw_text)

    # Step 2: GPT Parsing
    parsed_resume = parse_resume_with_gpt(raw_text)

    # Merge results
    return {
        "file": os.path.basename(file_path),
        "preprocessed": preprocessed,
        "parsed": parsed_resume
    }


def parse_resume_from_blob(blob_name: str, user_id: str = None) -> dict:
    """Full pipeline: extract raw text from blob, preprocess, then parse with GPT."""
    raw_text = extract_text_from_blob(blob_name, user_id=user_id)

    # Save extracted raw text to blob storage
    processed_blob_name = f"processed/{os.path.basename(blob_name)}.txt"
    if user_id:
        blob_storage.upload_file_user(raw_text.encode('utf-8'), processed_blob_name, user_id)
    else:
        blob_storage.upload_file(raw_text.encode('utf-8'), processed_blob_name)

    # Step 1: Preprocess
    preprocessed = preprocess_resume_text(raw_text)

    # Step 2: GPT Parsing
    parsed_resume = parse_resume_with_gpt(raw_text)

    # Merge results
    return {
        "file": os.path.basename(blob_name),
        "blob_name": blob_name,
        "processed_blob_name": processed_blob_name,
        "preprocessed": preprocessed,
        "parsed": parsed_resume
    }


def parse_zip(file_path: str) -> list:
    """Handle ZIP file containing multiple resumes."""
    parsed_results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        for root, _, files in os.walk(tmpdir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    try:
                        resume_path = os.path.join(root, file)
                        parsed = parse_resume(resume_path)
                        parsed_results.append(parsed)
                    except Exception as e:
                        parsed_results.append({"file": file, "error": str(e)})

    return parsed_results


def parse_zip_from_blob(blob_name: str, user_id: str = None) -> list:
    """Handle ZIP file containing multiple resumes from blob storage."""
    parsed_results = []

    # Download ZIP file from blob storage
    if user_id:
        zip_content = blob_storage.download_file_user(blob_name, user_id)
    else:
        zip_content = blob_storage.download_file(blob_name)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save ZIP content to temporary file
        zip_path = os.path.join(tmpdir, "temp.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_content)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file == "temp.zip":  # Skip the temp zip file itself
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    try:
                        resume_path = os.path.join(root, file)
                        parsed = parse_resume(resume_path)
                        parsed_results.append(parsed)
                    except Exception as e:
                        parsed_results.append({"file": file, "error": str(e)})

    return parsed_results
