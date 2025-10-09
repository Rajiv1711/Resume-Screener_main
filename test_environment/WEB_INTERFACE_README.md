# 🌐 Resume Screener Web Interface

A complete web-based testing interface for your Resume Screener that **mimics your original UI** but runs entirely with mock services—no Azure services, databases, or API keys required!

## ✨ Features

### 🎯 **Complete User Experience**
- **Professional UI** that looks and feels like your production interface
- **Real-time processing** with progress indicators
- **Interactive job selection** from predefined job descriptions
- **Drag & drop file upload** with support for PDF, DOCX, TXT
- **Live ranking results** with beautiful visualizations
- **Detailed analytics** and insights dashboard

### 🧪 **Full ML Pipeline Testing**
- **Resume Parsing**: Extract structured data using mock GPT
- **Embedding Generation**: Create semantic vectors with mock OpenAI
- **Hybrid Ranking**: TF-IDF + embedding similarity scoring
- **Skill Matching**: Visual skill coverage analysis
- **Export Options**: Download results as CSV or JSON

### 🚀 **Zero Dependencies**
- **No Azure services** - everything runs locally
- **No API keys** - uses mock services
- **No database** - session-based storage
- **No authentication** - focuses on ML testing

## 🚀 Quick Start

### Option 1: Double-Click Launch (Windows)
```bash
# Simply double-click:
start_web_interface.bat
```

### Option 2: Python Launch
```bash
# From test_environment directory:
python start_web_interface.py
```

### Option 3: Direct Flask
```bash
# From web_interface directory:
cd web_interface
python app.py
```

## 🎮 How to Use

### 1. **Select Job Description**
- Choose from 3 predefined job descriptions:
  - Senior Python Developer
  - Data Scientist  
  - Frontend React Developer
- View required and preferred skills
- See job description details

### 2. **Upload Resumes**
- Click "Upload Resumes" and select files
- Supported formats: PDF, DOCX, TXT
- Upload multiple files at once
- Real-time processing with progress bar

### 3. **View Processing Results**
- See parsing success/failure for each resume
- View extracted skills and tokens count
- Check for any processing errors

### 4. **Rank Candidates**
- Click "Rank Candidates" to start ranking
- Watch real-time progress indicators
- See hybrid scores (TF-IDF + embeddings)

### 5. **Analyze Results**
- **Ranking Cards**: Top candidates with scores
- **Skill Matching**: Visual coverage percentages
- **Detailed Analysis**: Statistics and breakdowns
- **Export Options**: Download data for further analysis

## 📊 Interface Sections

### 🎛️ **Control Sidebar**
- **Job Selection**: Dropdown with available positions
- **File Upload**: Multi-file selector with format validation
- **Action Buttons**: Process, Rank, Clear operations
- **Export Options**: CSV and JSON download buttons
- **Status Display**: Real-time operation feedback

### 📋 **Main Dashboard**
- **Job Description Card**: Shows selected job details
- **Processing Results**: Upload and parsing summary
- **Ranking Results**: Ordered candidate list with scores
- **Detailed Analysis**: In-depth metrics and charts
- **Progress Indicators**: Real-time processing feedback

### 🏆 **Ranking Display**
- **Visual Ranking**: Gold, silver, bronze indicators
- **Score Breakdown**: Hybrid, TF-IDF, embedding scores
- **Skill Analysis**: Required/preferred skill matches
- **Coverage Bars**: Visual skill matching percentages
- **Matched Skills**: Highlighted skill badges

## 🔧 Technical Details

### **Backend (Flask)**
- **REST API**: Clean endpoints for upload, ranking, export
- **File Handling**: Secure upload with validation
- **Session Management**: Temporary data storage
- **Mock Integration**: Uses test parser, embedder, ranker
- **Error Handling**: Comprehensive error responses

### **Frontend (HTML/CSS/JS)**
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Bootstrap 5 + custom styling
- **Interactive Elements**: Real-time updates and feedback
- **Progress Tracking**: Visual processing indicators
- **Export Functionality**: Client-side file downloads

### **Mock Services Integration**
- **Parser**: Uses TestParser with mock GPT responses
- **Embedder**: Generates deterministic embeddings
- **Ranker**: Hybrid scoring with TF-IDF + embeddings
- **Data**: Sample resumes and job descriptions included

## 📁 File Structure

```
web_interface/
├── app.py                 # Flask backend application
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── style.css         # UI styling
│   └── script.js         # Frontend JavaScript
└── uploads/              # Temporary file storage
```

## 🎯 API Endpoints

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/` | GET | Main interface |
| `/api/job-descriptions` | GET | Get available jobs |
| `/api/upload` | POST | Upload and process resumes |
| `/api/rank` | POST | Rank resumes against job |
| `/api/export/<format>` | GET | Export results (csv/json) |
| `/api/clear-session` | POST | Clear session data |

## 🧪 Testing Scenarios

### **Basic Workflow**
1. Start interface → Select job → Upload resumes → Rank → Analyze

### **Edge Cases**
- Upload invalid file formats
- Upload without selecting job
- Rank without uploading files
- Multiple job selections
- Large file uploads

### **Performance Testing**
- Multiple simultaneous uploads
- Large resume files
- Many skill matches
- Export large datasets

## 💡 Use Cases

### **Development Testing**
- Validate ML pipeline logic
- Test UI/UX improvements
- Debug ranking algorithms
- Verify skill extraction

### **Demo & Presentation**
- Show complete user journey
- Demonstrate ranking intelligence
- Highlight key features
- No setup complexity

### **Algorithm Comparison**
- Test scoring parameter changes
- Compare different job descriptions
- Analyze skill matching accuracy
- Export data for further analysis

## 🔍 Troubleshooting

### **Common Issues**

**Interface won't start:**
```bash
# Check Flask installation
pip install flask

# Verify you're in the right directory
ls web_interface/app.py
```

**Processing errors:**
```bash
# Check dependencies
pip install spacy scikit-learn numpy
python -m spacy download en_core_web_sm
```

**Port already in use:**
```bash
# Kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

### **Browser Issues**
- Clear browser cache
- Try incognito/private mode
- Check JavaScript console for errors
- Ensure port 5000 is accessible

## 🎉 What You Get

### **Immediate Benefits**
✅ **Test your ML pipeline** without external services  
✅ **Demo your solution** with professional interface  
✅ **Debug ranking logic** with detailed analysis  
✅ **Export test data** for comparison with production  
✅ **Validate UI/UX** before full integration  

### **Development Advantages**
✅ **Rapid iteration** - no API rate limits or costs  
✅ **Consistent results** - deterministic mock responses  
✅ **Easy debugging** - all processing happens locally  
✅ **Complete control** - modify behavior as needed  
✅ **No infrastructure** - just run and test  

---

## 🚀 **Ready to Test?**

Just run `start_web_interface.bat` and your browser will open automatically!

**Your Resume Screener is now fully testable with a professional web interface! 🎉**