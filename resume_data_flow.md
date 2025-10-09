# Resume Screener Project - Data Flow

## Overview
This document outlines the complete data flow for resume processing in the Resume Screener Project, from initial upload to final ranking and reporting.

## Data Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   File System   │
│   (React)       │    │   Backend       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Upload Resume      │                       │
         │──────────────────────▶│                       │
         │                       │                       │
         │                       │ 2. Save to Disk      │
         │                       │──────────────────────▶│ data/raw_resumes/
         │                       │                       │
         │                       │ 3. Parse Resume      │
         │                       │◀──────────────────────│
         │                       │                       │
         │ 4. Return Parsed      │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │                       │                       │
         │ 5. Job Description    │                       │
         │──────────────────────▶│                       │
         │                       │                       │
         │                       │ 6. Read All Resumes  │
         │                       │◀──────────────────────│ data/raw_resumes/
         │                       │                       │
         │                       │ 7. Generate Reports  │
         │                       │──────────────────────▶│ reports/
         │                       │                       │
         │ 8. Return Ranked      │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │ 9. Download Reports   │                       │
         │──────────────────────▶│                       │
         │                       │ 10. Read Reports     │
         │                       │◀──────────────────────│ reports/
         │                       │                       │
         │ 11. Return File       │                       │
         │◀──────────────────────│                       │
```

## Detailed Data Flow Steps

### Phase 1: Resume Upload & Parsing

#### 1.1 Frontend Upload (`frontend/src/components/UploadResume.js`)
- User selects resume file(s) or ZIP file
- File is sent via HTTP POST to `/api/upload` endpoint
- Supports: PDF, DOCX, TXT, ZIP formats

#### 1.2 Backend Upload Handler (`app/routers/resumes.py`)
- Receives uploaded file via FastAPI
- Validates file format
- Saves file to `data/raw_resumes/` directory
- Calls appropriate parser based on file type

#### 1.3 Resume Parsing (`app/services/parser.py`)
- **Text Extraction**: 
  - PDF: Uses PyPDF2 to extract text
  - DOCX: Uses docx2txt library
  - TXT: Direct file reading
- **Text Preprocessing** (`ml/preprocessing.py`):
  - Clean text (lowercase, remove special chars)
  - Tokenize and lemmatize using spaCy
  - Extract skills using predefined skill list
- **GPT Parsing**:
  - Uses Azure OpenAI GPT-3.5 Turbo
  - Few-shot prompting to extract structured data
  - Returns JSON with name, email, phone, skills, experience, education
- **Save Processed Text**: Raw text saved to `data/processed/`

#### 1.4 Response to Frontend
- Returns parsed resume data
- Includes both preprocessed and GPT-parsed information

### Phase 2: Resume Ranking

#### 2.1 Ranking Request (`app/routers/ranking.py`)
- User provides job description
- System reads all resumes from `data/raw_resumes/`
- Processes each resume through the ranking pipeline

#### 2.2 Embedding Generation (`app/services/embeddings.py`)
- **Job Description Embedding**: 
  - Uses Azure OpenAI text-embedding-3-large model
  - Converts job description to vector representation
- **Resume Embeddings**:
  - Combines cleaned text + extracted skills
  - Generates embedding vector for each resume
  - Uses same embedding model for consistency

#### 2.3 Similarity Calculation (`app/services/ranker.py`)
- Computes cosine similarity between job description and each resume
- Ranks resumes by similarity score (descending order)
- Returns ranked list with scores and metadata

#### 2.4 Results Storage
- Saves ranked results to `reports/ranked_resumes.json`
- Includes file names, scores, skills, and parsed data

### Phase 3: Report Generation

#### 3.1 Report Generation (`app/services/report.py`)
- **Excel Report**: Creates `reports/ranked_resumes.xlsx`
  - Columns: Rank, Candidate Name, Email, File, Score, Top Skills
- **PDF Report**: Creates `reports/ranked_resumes.pdf`
  - Formatted table with candidate information
  - Professional styling with ReportLab

#### 3.2 Report Download (`app/routers/reporting.py`)
- Provides endpoints to download generated reports
- Supports both Excel and PDF formats

## Data Storage Locations

### Azure Blob Storage (Primary)
- `resumes/raw_resumes/` - Original uploaded files (PDF, DOCX, TXT, ZIP)
- `resumes/processed/` - Extracted raw text files (.txt)
- `resumes/reports/` - All generated reports (JSON, Excel, PDF)

### Local Storage (Backup/Cache)
- `data/raw_resumes/` - Local backup of uploaded files
- `data/processed/` - Local backup of extracted text
- `reports/` - Local backup of generated reports

## Key Technologies & Services

### Backend Services
- **FastAPI**: REST API framework
- **Azure OpenAI**: GPT-3.5 Turbo for parsing, text-embedding-3-large for embeddings
- **Azure Blob Storage**: Cloud file storage for resumes and reports
- **spaCy**: Natural language processing for text preprocessing
- **PyPDF2**: PDF text extraction
- **docx2txt**: DOCX text extraction

### Frontend
- **React**: User interface
- **Axios**: HTTP client for API calls
- **MSAL**: Microsoft Authentication Library for Azure AD

### File Processing
- **openpyxl**: Excel file generation
- **ReportLab**: PDF generation
- **zipfile**: ZIP file handling
- **azure-storage-blob**: Azure Blob Storage integration

## Data Transformations

### 1. Raw File → Extracted Text
```
PDF/DOCX/TXT → Raw Text String
```

### 2. Raw Text → Preprocessed Data
```
Raw Text → Cleaned Text + Tokens + Skills
```

### 3. Raw Text → Structured Data (GPT)
```
Raw Text → JSON {name, email, phone, skills, experience, education}
```

### 4. Preprocessed Data → Embeddings
```
Cleaned Text + Skills → Vector Embedding (1536 dimensions)
```

### 5. Embeddings → Similarity Scores
```
Job Embedding + Resume Embedding → Cosine Similarity Score
```

### 6. Scores → Ranked Results
```
Similarity Scores → Sorted List (descending by score)
```

### 7. Ranked Results → Reports
```
JSON Data → Excel/PDF Reports
```

## Error Handling

- File format validation at upload
- Graceful handling of parsing errors
- Error logging for failed resume processing
- Fallback to raw text when GPT parsing fails
- Exception handling in ranking pipeline

## Security & Authentication

- Azure AD authentication required for all endpoints
- JWT token validation via `get_current_user_azure`
- CORS configuration for frontend access
- File upload validation and sanitization

## Performance Considerations

- Batch processing of multiple resumes
- Efficient embedding generation
- Azure Blob Storage for scalable file operations
- Caching of processed text files
- Asynchronous file operations where possible
- Cloud-native architecture for better scalability
