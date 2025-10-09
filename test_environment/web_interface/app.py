#!/usr/bin/env python3
"""
Resume Screener Test Web Interface
Flask backend that provides a web UI for testing the ML components with mock services.
"""

import os
import sys
import json
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, session
from werkzeug.utils import secure_filename
import csv
import io
import pickle
import time

# Add project paths
current_dir = Path(__file__).parent
test_env_dir = current_dir.parent
project_root = test_env_dir.parent

sys.path.insert(0, str(test_env_dir))
sys.path.insert(0, str(project_root))

# Mock OpenAI before importing
import mock_services.mock_openai as openai
sys.modules['openai'] = openai

# Import silent modules (no console output)
from silent_parser import SilentParser
from silent_embedder import SilentEmbedder
from silent_ranker import SilentRanker

app = Flask(__name__)
app.secret_key = 'test-secret-key-for-resume-screener'
app.config['UPLOAD_FOLDER'] = current_dir / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class TempDataStorage:
    """Manages temporary file storage for processed resume data."""
    
    def __init__(self, temp_dir=None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / 'resume_screener'
        self.temp_dir.mkdir(exist_ok=True)
        # Clean up files older than 2 hours on initialization
        self.cleanup_old_files(max_age_hours=2)
    
    def store_data(self, session_id, data):
        """Store processed resume data for a session."""
        file_path = self.temp_dir / f"resumes_{session_id}.pkl"
        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'data': data,
                    'timestamp': time.time(),
                    'session_id': session_id
                }, f)
            print(f"DEBUG: Stored data for session {session_id} in {file_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to store data for session {session_id}: {e}")
            return False
    
    def retrieve_data(self, session_id):
        """Retrieve processed resume data for a session."""
        file_path = self.temp_dir / f"resumes_{session_id}.pkl"
        try:
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    stored_data = pickle.load(f)
                print(f"DEBUG: Retrieved data for session {session_id} from {file_path}")
                return stored_data['data']
            else:
                print(f"DEBUG: No data file found for session {session_id}")
                return None
        except Exception as e:
            print(f"ERROR: Failed to retrieve data for session {session_id}: {e}")
            return None
    
    def delete_data(self, session_id):
        """Delete stored data for a session."""
        file_path = self.temp_dir / f"resumes_{session_id}.pkl"
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"DEBUG: Deleted data file for session {session_id}")
                return True
            return False
        except Exception as e:
            print(f"ERROR: Failed to delete data for session {session_id}: {e}")
            return False
    
    def cleanup_old_files(self, max_age_hours=2):
        """Clean up temporary files older than specified hours."""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_dir.glob("resumes_*.pkl"):
                try:
                    if file_path.stat().st_mtime < (current_time - max_age_seconds):
                        file_path.unlink()
                        print(f"DEBUG: Cleaned up old file {file_path}")
                except Exception as e:
                    print(f"WARNING: Failed to clean up file {file_path}: {e}")
        except Exception as e:
            print(f"ERROR: Failed to cleanup old files: {e}")
    
    def get_or_create_session_id(self, session):
        """Get existing session ID or create a new one."""
        if 'data_session_id' not in session:
            session['data_session_id'] = str(uuid.uuid4())
            print(f"DEBUG: Created new data session ID: {session['data_session_id']}")
        return session['data_session_id']

class ResumeProcessor:
    """Handles resume processing using mock services."""
    
    def __init__(self):
        self.parser = SilentParser()
        self.embedder = SilentEmbedder()
        self.ranker = SilentRanker()
        self.job_descriptions = self.load_job_descriptions()
    
    def load_job_descriptions(self):
        """Load job descriptions from test data."""
        job_file = test_env_dir / "mock_data" / "job_descriptions.json"
        with open(job_file, 'r') as f:
            return json.load(f)
    
    def process_file(self, file_path, filename):
        """Process a single resume file."""
        try:
            result = self.parser.parse_resume(file_path)
            result['original_filename'] = filename
            result['file_id'] = str(uuid.uuid4())
            result['processed_at'] = datetime.now().isoformat()
            return result
        except Exception as e:
            return {
                'file': filename,
                'original_filename': filename,
                'file_id': str(uuid.uuid4()),
                'processed_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def rank_resumes(self, processed_resumes, job_description_key):
        """Rank resumes against a specific job description."""
        if job_description_key not in self.job_descriptions:
            return {'error': 'Invalid job description key'}
        
        job_data = self.job_descriptions[job_description_key]
        
        try:
            ranked_results = self.ranker.rank_resumes(processed_resumes, job_data['description'])
            
            # Add additional metadata
            for i, result in enumerate(ranked_results):
                if 'error' not in result:
                    # Add skill match analysis
                    resume_skills = set(result.get('skills', []))
                    required_skills = set(job_data.get('required_skills', []))
                    preferred_skills = set(job_data.get('preferred_skills', []))
                    
                    required_matches = resume_skills.intersection(required_skills)
                    preferred_matches = resume_skills.intersection(preferred_skills)
                    
                    result.update({
                        'rank': i + 1,
                        'job_title': job_data['title'],
                        'required_skill_matches': list(required_matches),
                        'preferred_skill_matches': list(preferred_matches),
                        'required_skills_coverage': round(len(required_matches) / len(required_skills) * 100, 1) if required_skills else 0,
                        'preferred_skills_coverage': round(len(preferred_matches) / len(preferred_skills) * 100, 1) if preferred_skills else 0,
                        'total_skill_matches': len(required_matches) + len(preferred_matches)
                    })
            
            return {
                'job_info': job_data,
                'ranked_results': ranked_results,
                'total_resumes': len([r for r in ranked_results if 'error' not in r])
            }
            
        except Exception as e:
            return {'error': str(e)}

# Initialize processor and storage
processor = ResumeProcessor()
storage = TempDataStorage()

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/job-descriptions')
def get_job_descriptions():
    """Get available job descriptions."""
    jobs = []
    for key, job_data in processor.job_descriptions.items():
        jobs.append({
            'key': key,
            'title': job_data['title'],
            'description': job_data['description'],
            'required_skills': job_data.get('required_skills', []),
            'preferred_skills': job_data.get('preferred_skills', [])
        })
    return jsonify(jobs)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    processed_results = []
    upload_id = str(uuid.uuid4())
    
    for file in files:
        if file and allowed_file(file.filename):
            # Secure the filename and save
            filename = secure_filename(file.filename)
            file_path = app.config['UPLOAD_FOLDER'] / f"{upload_id}_{filename}"
            file.save(file_path)
            
            # Process the file
            result = processor.process_file(str(file_path), filename)
            processed_results.append(result)
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
        else:
            processed_results.append({
                'file': file.filename,
                'original_filename': file.filename,
                'file_id': str(uuid.uuid4()),
                'processed_at': datetime.now().isoformat(),
                'error': 'File type not allowed'
            })
    
    # Store results in temporary file instead of session
    session_id = storage.get_or_create_session_id(session)
    success = storage.store_data(session_id, processed_results)
    
    if not success:
        return jsonify({'error': 'Failed to store processed data'}), 500
    
    return jsonify({
        'upload_id': upload_id,
        'processed_count': len([r for r in processed_results if 'error' not in r]),
        'error_count': len([r for r in processed_results if 'error' in r]),
        'results': processed_results
    })

@app.route('/api/rank', methods=['POST'])
def rank_resumes():
    """Rank uploaded resumes against a job description."""
    # Add debugging
    print(f"DEBUG: Received request to /api/rank")
    print(f"DEBUG: Content-Type: {request.content_type}")
    print(f"DEBUG: Request data: {request.data}")
    
    try:
        data = request.json
        print(f"DEBUG: Parsed JSON data: {data}")
    except Exception as e:
        print(f"DEBUG: JSON parsing error: {e}")
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data:
        print("DEBUG: No data received")
        return jsonify({'error': 'No data received'}), 400
    
    job_key = data.get('job_key')
    print(f"DEBUG: Job key: {job_key}")
    
    if not job_key:
        print("DEBUG: No job key provided")
        return jsonify({'error': 'Job description key is required'}), 400
    
    # Get session ID and retrieve data from file storage
    session_id = session.get('data_session_id')
    if not session_id:
        print("DEBUG: No data session ID found")
        return jsonify({'error': 'No session data found. Please upload resumes first.'}), 400
    
    processed_resumes = storage.retrieve_data(session_id)
    if processed_resumes is None:
        processed_resumes = []
    
    print(f"DEBUG: Found {len(processed_resumes)} processed resumes in storage")
    if not processed_resumes:
        print("DEBUG: No resumes in storage")
        return jsonify({'error': 'No resumes uploaded yet'}), 400
    
    # Filter out errored resumes for ranking
    valid_resumes = [r for r in processed_resumes if 'error' not in r]
    if not valid_resumes:
        return jsonify({'error': 'No valid resumes to rank'}), 400
    
    ranking_results = processor.rank_resumes(valid_resumes, job_key)
    
    if 'error' in ranking_results:
        return jsonify(ranking_results), 500
    
    return jsonify(ranking_results)

@app.route('/api/export/<format>')
def export_results(format):
    """Export results in various formats."""
    if format not in ['csv', 'json']:
        return jsonify({'error': 'Unsupported format'}), 400
    
    # Get data from file storage
    session_id = session.get('data_session_id')
    if not session_id:
        return jsonify({'error': 'No session data found'}), 400
    
    processed_resumes = storage.retrieve_data(session_id)
    if not processed_resumes:
        return jsonify({'error': 'No data to export'}), 400
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'csv':
        output = io.StringIO()
        
        # Determine fields
        if processed_resumes:
            sample = processed_resumes[0]
            fieldnames = []
            
            # Basic fields
            basic_fields = ['file', 'original_filename', 'file_id', 'processed_at', 'status']
            fieldnames.extend([f for f in basic_fields if f in sample or f == 'status'])
            
            # Add status field
            for resume in processed_resumes:
                resume['status'] = 'error' if 'error' in resume else 'success'
            
            # Parsed data fields
            if 'parsed' in sample:
                parsed_fields = ['gpt_name', 'gpt_email', 'gpt_phone', 'gpt_skills', 'gpt_experience']
                fieldnames.extend(parsed_fields)
                
                # Flatten parsed data
                for resume in processed_resumes:
                    if 'parsed' in resume:
                        parsed = resume['parsed']
                        resume['gpt_name'] = parsed.get('name', 'N/A')
                        resume['gpt_email'] = parsed.get('email', 'N/A')
                        resume['gpt_phone'] = parsed.get('phone', 'N/A')
                        resume['gpt_skills'] = '|'.join(parsed.get('skills', []))
                        resume['gpt_experience'] = '|'.join(parsed.get('experience', []))
            
            # Preprocessing fields
            if 'preprocessed' in sample:
                prep_fields = ['skills_count', 'tokens_count', 'preprocessing_skills']
                fieldnames.extend(prep_fields)
                
                for resume in processed_resumes:
                    if 'preprocessed' in resume:
                        prep = resume['preprocessed']
                        resume['skills_count'] = len(prep.get('skills', []))
                        resume['tokens_count'] = len(prep.get('tokens', []))
                        resume['preprocessing_skills'] = '|'.join(prep.get('skills', []))
            
            # Error field
            fieldnames.append('error_message')
            for resume in processed_resumes:
                resume['error_message'] = resume.get('error', '')
        
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_resumes)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'resume_analysis_{timestamp}.csv'
        )
    
    else:  # JSON format
        return send_file(
            io.BytesIO(json.dumps(processed_resumes, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'resume_analysis_{timestamp}.json'
        )

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear current session data and temporary files."""
    # Clean up temporary data file if it exists
    session_id = session.get('data_session_id')
    if session_id:
        storage.delete_data(session_id)
        print(f"DEBUG: Cleaned up temporary data for session {session_id}")
    
    # Clear session
    session.clear()
    
    # Also run cleanup of old files
    storage.cleanup_old_files(max_age_hours=2)
    
    return jsonify({'message': 'Session and temporary data cleared'})

if __name__ == '__main__':
    # Ensure upload directory exists
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    
    print("🚀 Starting Resume Screener Test Web Interface...")
    print("=" * 60)
    print(f"📂 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🌐 Web interface will be available at: http://localhost:5000")
    print("=" * 60)
    print("\n✨ All ranking results will be displayed in the web interface only!")
    print("📊 Check your browser at http://localhost:5000 for the complete experience.")
    print("\n" + "=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
