# 🧪 Resume Screener Test Environment

A comprehensive testing environment for the Resume Screener project that allows you to test frontend and ML components (parser, embedder, ranker) **without needing Azure services, SQL databases, or external API keys**.

## 📋 Overview

This test environment provides:
- **Mock Services**: Replaces Azure OpenAI, Blob Storage, and authentication
- **Sample Data**: Pre-built resumes and job descriptions for testing
- **Standalone Components**: Test ML pipeline components independently
- **Frontend Testing**: Mock React interface for UI testing
- **Automated Test Suite**: Scripts to run comprehensive tests

## 📁 Project Structure

```
test_environment/
├── README.md                 # This file
├── backend_tests/           # Backend component tests
│   ├── test_parser.py       # Parser component tests
│   ├── test_embedder.py     # Embedder component tests
│   └── test_ranker.py       # Ranker component tests
├── frontend_tests/          # Frontend testing components
│   ├── TestApp.js           # Mock React application
│   └── TestApp.css          # Styling for test interface
├── mock_data/              # Sample test data
│   ├── sample_resume_1.txt  # Sample resume 1
│   ├── sample_resume_2.txt  # Sample resume 2
│   ├── sample_resume_3.txt  # Sample resume 3
│   └── job_descriptions.json # Job description samples
├── mock_services/          # Mock external services
│   ├── mock_openai.py      # Mock OpenAI API
│   └── mock_blob_storage.py # Mock Azure Blob Storage
├── scripts/               # Test execution scripts
│   ├── run_backend_tests.py # Python test runner
│   └── run_tests.bat       # Windows batch script
└── configs/              # Configuration files
    └── test_config.json  # Test environment settings
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Required Python packages**:
   ```bash
   pip install spacy scikit-learn numpy pandas
   python -m spacy download en_core_web_sm
   ```

### Option 1: Run All Backend Tests (Recommended)

**On Windows:**
1. Navigate to the test environment folder
2. Double-click `scripts/run_tests.bat`

**On any platform:**
```bash
cd test_environment
python scripts/run_backend_tests.py
```

### Option 2: Run Individual Component Tests

```bash
cd test_environment

# Test parser
python backend_tests/test_parser.py

# Test embedder  
python backend_tests/test_embedder.py

# Test ranker
python backend_tests/test_ranker.py
```

## 🧪 Component Testing Details

### Parser Testing
- **What it tests**: Text extraction, GPT parsing, preprocessing
- **Mock services used**: Mock OpenAI API
- **Sample data**: 3 different resume formats
- **Output**: Parsed structured data (name, email, skills, etc.)

### Embedder Testing
- **What it tests**: Text embedding generation, similarity calculations
- **Mock services used**: Mock OpenAI Embeddings API
- **Tests**: Basic embedding, similarity comparison
- **Output**: Vector embeddings and similarity scores

### Ranker Testing
- **What it tests**: Resume ranking using hybrid scoring (TF-IDF + embeddings)
- **Mock services used**: Mock OpenAI, integrated parser/embedder
- **Tests**: Individual scoring methods, integrated ranking pipeline
- **Output**: Ranked resume list with scores

## 🎯 Test Scenarios

### Backend Tests
1. **Individual Component Tests**:
   - Parser: Extract and parse resume content
   - Embedder: Generate embeddings and test similarity
   - Ranker: Score and rank resumes against job descriptions

2. **Integrated Test**:
   - Parse sample resumes → Generate embeddings → Rank against all job descriptions
   - Tests the complete ML pipeline end-to-end

### Expected Results
✅ **Parser Test**: Should extract names, emails, skills from sample resumes  
✅ **Embedder Test**: Should generate 1536-dimensional embeddings and show higher similarity for related texts  
✅ **Ranker Test**: Should rank resumes appropriately for different job descriptions  

## 📊 Understanding Test Output

### Successful Test Output
```
🧪 Testing Parser with Mock Services
==================================================
✅ Successfully parsed sample_resume_1.txt
✅ Successfully parsed sample_resume_2.txt  
✅ Successfully parsed sample_resume_3.txt

📋 Results Summary:
✅ sample_resume_1.txt:
   - Name: John Smith
   - Email: john.smith@email.com
   - Skills: 7 found
   - Preprocessed tokens: 156
   - Extracted skills: ['Python', 'React', 'Machine Learning', 'SQL']
```

### Test Metrics
- **Embedding Scores**: Cosine similarity (-1 to 1, higher = more similar)
- **TF-IDF Scores**: Term frequency relevance (0 to 1, higher = more relevant) 
- **Hybrid Scores**: Combined score (0 to 1, higher = better match)

## 🔧 Customization

### Adding Your Own Test Data

1. **Add Resume Files**:
   ```
   test_environment/mock_data/your_resume.txt
   ```

2. **Update Job Descriptions**:
   Edit `mock_data/job_descriptions.json`:
   ```json
   {
     "your_job": {
       "title": "Your Job Title",
       "description": "Your job description here...",
       "required_skills": ["skill1", "skill2"],
       "preferred_skills": ["skill3", "skill4"]
     }
   }
   ```

3. **Modify Test Settings**:
   Edit `configs/test_config.json` to adjust:
   - Scoring weights (alpha parameter)
   - Expected skills list
   - Test verbosity

### Mock Service Configuration

**OpenAI Mock Settings**:
- Embedding dimension: 1536 (configurable)
- Deterministic results based on text content
- No API calls or costs

**Blob Storage Mock**:
- Uses local temporary directory
- Simulates upload/download operations
- No Azure account needed

## 🚨 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'spacy'"**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**"No resumes parsed successfully"**  
- Check that sample resume files exist in `mock_data/`
- Verify file encoding is UTF-8

**"Similarity test failed"**
- This is expected behavior - mock embeddings may not show perfect similarity patterns
- Tests are designed to verify the pipeline works, not accuracy

**Import errors**
- Make sure you're running from the `test_environment` directory
- Check that the main project files exist in the parent directory

### Performance Notes
- Tests run entirely locally - no internet required
- Mock services are fast but results are simplified
- Embedding generation uses deterministic pseudo-random values

## 🔬 Advanced Usage

### Frontend Testing
The frontend test environment includes:
- Mock React interface in `frontend_tests/TestApp.js`
- Simulated file upload and processing
- Mock authentication (no real Azure AD)
- Component testing dashboard

To use:
1. Copy `TestApp.js` and `TestApp.css` to your React frontend
2. Replace your main App component temporarily
3. Test UI interactions without backend dependencies

### Integration with Real Services
When ready to test with real services:
1. Replace mock imports with real service imports
2. Add actual API keys to environment variables
3. Test with small datasets first
4. Compare results with mock test results for validation

## 📈 What's Tested vs Production

| Component | Mock Version | Production Version |
|-----------|-------------|-------------------|
| Text Parsing | ✅ Structure extraction | ✅ Real GPT parsing |
| Embeddings | ✅ Deterministic vectors | ✅ Real OpenAI embeddings |
| Similarity | ✅ Cosine similarity math | ✅ Same algorithm |
| TF-IDF | ✅ Real scikit-learn | ✅ Same implementation |
| File handling | ✅ Local file system | ❌ Azure Blob Storage |
| Authentication | ❌ Mock only | ❌ Real Azure AD |

## 📝 Test Reporting

Test results are displayed in the console and include:
- ✅/❌ Status indicators
- Execution times
- Component-specific metrics
- Overall success rate
- Detailed error messages for failures

For automated testing, check the exit codes:
- `0`: All tests passed
- `1`: Some tests failed
- `2`: Critical dependency missing

## 🎉 Next Steps

After successful testing:
1. **Validate Results**: Compare mock results with expected outcomes
2. **Add Real Services**: Gradually replace mocks with real services  
3. **Scale Testing**: Test with larger datasets
4. **Performance Testing**: Measure real-world performance
5. **Deploy**: Move to production environment

## 💡 Tips for Development

1. **Start Simple**: Use mock tests for rapid development
2. **Test Edge Cases**: Add your own test data with edge cases
3. **Compare Results**: Use mock tests to validate algorithm changes
4. **Debug Easily**: Mock services provide consistent, debuggable results
5. **Cost Control**: Develop and test without API costs

---

**Happy Testing! 🧪✨**

For issues or questions, check the error messages in the test output or review the component-specific test files for debugging information.