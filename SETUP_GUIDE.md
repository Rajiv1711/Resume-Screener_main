# Resume Screener Setup Guide

## 🎯 Quick Setup (Windows)

This guide ensures smooth virtual environment creation and dependency installation for the Resume Screener project.

### Prerequisites
- Python 3.13+ installed
- Node.js and npm installed (for frontend)
- PowerShell or Command Prompt access

### 🚀 Setup Steps

#### 1. Clone and Navigate
```powershell
git clone <repository-url>
cd Resume-Screener_main
```

#### 2. Create Virtual Environment
```powershell
python -m venv venv
```

#### 3. Activate Virtual Environment
```powershell
# PowerShell
venv\Scripts\Activate.ps1

# Command Prompt  
venv\Scripts\activate.bat
```

#### 4. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

#### 5. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

#### 6. Start the Application

**Backend (Terminal 1):**
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend (Terminal 2):**
```powershell
cd frontend
npm start
```

## 📋 Dependencies Overview

### Core Dependencies Analysis

**✅ Successfully Resolved Issues:**

1. **Spacy Compilation Problem**: 
   - **Issue**: `spacy==3.7.4` failed to compile on Windows due to C++ build dependencies
   - **Solution**: Replaced with NLTK for text processing in `ml/preprocessing.py`
   - **Impact**: Maintained NLP functionality without compilation issues

2. **Missing FastAPI File Upload Support**:
   - **Issue**: `python-multipart` was missing, causing file upload failures
   - **Solution**: Added `python-multipart==0.0.20` to requirements.txt

3. **Version Mismatches**:
   - **Issue**: Some package versions in original requirements.txt were outdated
   - **Solution**: Updated to tested, working versions

### Key Package Categories

#### 🌐 Web Framework
- `fastapi==0.115.0` - Main web framework
- `uvicorn==0.30.1` - ASGI server
- `starlette==0.38.6` - Web framework foundation
- `python-multipart==0.0.20` - File upload support

#### 🤖 NLP & Text Processing  
- `nltk==3.9.1` - Natural language processing (replaces spacy)
- `PyPDF2==3.0.1` - PDF text extraction
- `python-docx==1.1.2` - Word document processing
- `docx2txt==0.8` - Alternative docx processing
- `regex==2025.9.18` - Advanced regex support

#### 🧠 Machine Learning
- `numpy==2.3.3` - Numerical computing
- `scikit-learn==1.7.2` - ML algorithms  
- `transformers==4.57.0` - Hugging Face transformers

#### ☁️ Azure & AI Services
- `openai==2.3.0` - OpenAI API client
- `azure-identity==1.25.1` - Azure authentication
- `azure-storage-blob==12.26.0` - Azure blob storage

#### 📊 Reporting & Export
- `openpyxl==3.1.5` - Excel file generation
- `reportlab==4.4.4` - PDF report generation
- `pandas==2.3.3` - Data manipulation

#### 🔐 Authentication & Security
- `PyJWT==2.10.1` - JWT token handling
- `python-jose[cryptography]==3.5.0` - JSON Web Signature
- `requests==2.32.5` - HTTP client

#### 🧪 Testing & Development
- `pytest==8.4.2` - Testing framework
- `black==25.9.0` - Code formatting
- `flake8==7.3.0` - Code linting
- `isort==7.0.0` - Import sorting

#### 🌐 Optional Web Interface
- `flask==3.1.0` - For test web interface
- `werkzeug==3.1.0` - Flask dependency

## 🛠️ Code Modifications Made

### 1. Updated `ml/preprocessing.py`
**Before:** Used spacy for NLP processing
```python
import spacy
nlp = spacy.load("en_core_web_sm")
```

**After:** Uses NLTK with automatic data download
```python
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Auto-download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
```

### 2. Updated `requirements.txt`
- Removed problematic Windows packages
- Added missing dependencies
- Updated versions to tested, working ones
- Added clear categorization and comments

## 🚨 Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Ensure virtual environment is activated before running commands

### Issue: Port already in use
**Solution:** 
```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <pid_number> /F
```

### Issue: Frontend build failures
**Solution:**
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: NLTK data download errors
**Solution:** Run this once after installation:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

## 📁 Project Structure
```
Resume-Screener_main/
├── app/                    # FastAPI backend
│   ├── main.py            # Main application
│   ├── routers/           # API routes
│   ├── services/          # Business logic
│   └── models/            # Data models
├── frontend/              # React frontend
│   ├── src/              # React source code
│   └── package.json      # Node dependencies
├── ml/                   # Machine learning components
│   ├── preprocessing.py  # Text processing (uses NLTK)
│   └── hybrid_ranker.py  # Ranking algorithms
├── test_environment/     # Test utilities
├── venv/                 # Virtual environment (created)
├── requirements.txt      # Python dependencies (updated)
└── SETUP_GUIDE.md       # This guide
```

## 🌐 Application URLs

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000  
- **API Documentation**: http://127.0.0.1:8000/docs
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## 📝 Development Notes

- **Virtual Environment**: Always use `venv` for dependency isolation
- **NLTK Data**: Downloads automatically on first import
- **File Uploads**: Supports PDF, DOCX, TXT, and ZIP files
- **Authentication**: Supports both regular and guest authentication
- **Storage**: Configured for Azure Blob Storage integration
- **Reports**: Generates Excel, PDF, and CSV reports

## 🏗️ Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ Azure Services
     ↓                     ↓                    ↓
  Port 3000           Port 8000         OpenAI + Blob Storage
```

---

**✅ This setup has been tested and verified to work smoothly on Windows with Python 3.13+**

For issues or questions, refer to the application logs or check the FastAPI interactive docs at `/docs`.