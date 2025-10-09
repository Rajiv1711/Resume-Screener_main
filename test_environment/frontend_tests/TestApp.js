import React, { useState } from 'react';
import './TestApp.css';

// Mock components for testing
const MockNavbar = ({ isAuthenticated, onLogin, onLogout }) => (
  <nav className="navbar">
    <div className="navbar-brand">
      <h2>🧪 Resume Screener Test Environment</h2>
    </div>
    <div className="navbar-auth">
      {isAuthenticated ? (
        <button onClick={onLogout} className="btn btn-secondary">
          Logout (Test User)
        </button>
      ) : (
        <button onClick={onLogin} className="btn btn-primary">
          Mock Login
        </button>
      )}
    </div>
  </nav>
);

const MockUploadPage = ({ onFileUpload, results }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [jobDescription, setJobDescription] = useState('');

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFiles.length > 0 && jobDescription.trim()) {
      onFileUpload(selectedFiles, jobDescription);
    } else {
      alert('Please select files and enter job description');
    }
  };

  const predefinedJobs = [
    {
      title: "Senior Python Developer",
      description: "We are looking for an experienced Senior Python Developer to join our team. The ideal candidate will have strong experience with Python, FastAPI, and cloud technologies. Experience with machine learning and AI is a plus."
    },
    {
      title: "Data Scientist", 
      description: "Seeking a Data Scientist to work on predictive modeling and analytics projects. The role involves building machine learning models, analyzing large datasets, and creating insights for business decisions."
    },
    {
      title: "Frontend React Developer",
      description: "Looking for a Frontend Developer with expertise in React and modern JavaScript. The candidate will be responsible for building user interfaces, implementing responsive designs, and working closely with UX/UI designers."
    }
  ];

  return (
    <div className="upload-page">
      <h3>📄 Upload Resumes for Testing</h3>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="files">Select Resume Files:</label>
          <input 
            type="file" 
            id="files"
            multiple 
            accept=".txt,.pdf,.docx"
            onChange={handleFileChange}
            className="form-control"
          />
          <small>Supported formats: TXT, PDF, DOCX</small>
        </div>

        <div className="form-group">
          <label htmlFor="job-desc">Job Description:</label>
          <textarea
            id="job-desc"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={4}
            className="form-control"
            placeholder="Enter the job description here..."
          />
        </div>

        <div className="predefined-jobs">
          <h4>Quick Select Job Descriptions:</h4>
          {predefinedJobs.map((job, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setJobDescription(job.description)}
              className="btn btn-outline-secondary btn-sm"
              style={{ margin: '5px' }}
            >
              {job.title}
            </button>
          ))}
        </div>

        <button type="submit" className="btn btn-success">
          🚀 Process Resumes
        </button>
      </form>

      {results && (
        <div className="results-section">
          <h3>📊 Test Results</h3>
          <div className="results-grid">
            {results.map((result, index) => (
              <div key={index} className="result-card">
                <h4>{result.file}</h4>
                {result.error ? (
                  <div className="error">❌ Error: {result.error}</div>
                ) : (
                  <div>
                    <div className="score">
                      <strong>Hybrid Score: {result.hybrid_score}</strong>
                    </div>
                    <div className="sub-scores">
                      <span>Embedding: {result.embedding_score}</span> | 
                      <span>TF-IDF: {result.tfidf_score}</span>
                    </div>
                    <div className="skills">
                      <strong>Skills:</strong> {result.skills?.join(', ') || 'None detected'}
                    </div>
                    <div className="parsed-info">
                      <strong>Name:</strong> {result.parsed?.name || 'N/A'}
                      <br />
                      <strong>Email:</strong> {result.parsed?.email || 'N/A'}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const MockDashboard = ({ results, onRunTest }) => {
  return (
    <div className="dashboard">
      <h3>📈 Test Dashboard</h3>
      
      <div className="test-controls">
        <h4>🧪 Component Tests</h4>
        <button 
          onClick={() => onRunTest('parser')} 
          className="btn btn-primary"
        >
          Test Parser
        </button>
        <button 
          onClick={() => onRunTest('embedder')} 
          className="btn btn-primary"
        >
          Test Embedder
        </button>
        <button 
          onClick={() => onRunTest('ranker')} 
          className="btn btn-primary"
        >
          Test Ranker
        </button>
        <button 
          onClick={() => onRunTest('all')} 
          className="btn btn-success"
        >
          Run All Tests
        </button>
      </div>

      {results && (
        <div className="test-results">
          <h4>Test Results:</h4>
          <pre className="test-output">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// Mock API calls
const mockAPI = {
  processResumes: async (files, jobDescription) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock response - in real implementation, this would call your backend
    return [
      {
        file: files[0]?.name || 'sample_resume_1.txt',
        hybrid_score: 0.85,
        embedding_score: 0.82,
        tfidf_score: 0.88,
        skills: ['Python', 'React', 'Machine Learning'],
        parsed: {
          name: 'John Smith',
          email: 'john.smith@email.com'
        }
      },
      {
        file: files[1]?.name || 'sample_resume_2.txt', 
        hybrid_score: 0.72,
        embedding_score: 0.75,
        tfidf_score: 0.68,
        skills: ['Python', 'Data Science', 'SQL'],
        parsed: {
          name: 'Sarah Johnson',
          email: 'sarah.johnson@email.com'
        }
      }
    ];
  },

  runComponentTest: async (component) => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      component,
      status: 'success',
      message: `${component} test completed successfully`,
      timestamp: new Date().toISOString()
    };
  }
};

const TestApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('upload');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState(null);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('upload');
  };

  const handleFileUpload = async (files, jobDescription) => {
    setIsLoading(true);
    try {
      const result = await mockAPI.processResumes(files, jobDescription);
      setResults(result);
      setCurrentView('results');
    } catch (error) {
      alert('Error processing resumes: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunTest = async (component) => {
    setIsLoading(true);
    try {
      const result = await mockAPI.runComponentTest(component);
      setTestResults(result);
    } catch (error) {
      alert('Error running test: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="test-app">
      <MockNavbar 
        isAuthenticated={isAuthenticated}
        onLogin={handleLogin}
        onLogout={handleLogout}
      />
      
      <div className="main-content">
        <div className="navigation-tabs">
          <button 
            className={currentView === 'upload' ? 'active' : ''}
            onClick={() => setCurrentView('upload')}
          >
            📤 Upload & Test
          </button>
          <button 
            className={currentView === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
        </div>

        {isLoading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {currentView === 'upload' && (
          <MockUploadPage 
            onFileUpload={handleFileUpload}
            results={currentView === 'results' ? results : null}
          />
        )}

        {currentView === 'dashboard' && isAuthenticated && (
          <MockDashboard 
            results={testResults}
            onRunTest={handleRunTest}
          />
        )}

        {currentView === 'dashboard' && !isAuthenticated && (
          <div className="auth-required">
            <h3>🔒 Authentication Required</h3>
            <p>Please login to access the dashboard.</p>
            <button onClick={handleLogin} className="btn btn-primary">
              Mock Login
            </button>
          </div>
        )}
      </div>

      <footer className="test-footer">
        <p>🧪 Resume Screener Test Environment - No external dependencies required</p>
      </footer>
    </div>
  );
};

export default TestApp;