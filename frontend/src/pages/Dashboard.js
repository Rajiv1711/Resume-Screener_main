import React, { useState } from "react";
import { rankResumes, downloadReport } from "../services/api";
import ResultsTable from "../components/ResultsTable";
import InsightsChart from "../components/InsightsChart";

const Dashboard = () => {
  const [ranked, setRanked] = useState([]);
  const [jobDescription, setJobDescription] = useState("");
  const [isRanking, setIsRanking] = useState(false);
  const [showJobDescModal, setShowJobDescModal] = useState(false);

  const handleRank = async () => {
    if (!jobDescription.trim()) {
      setShowJobDescModal(true);
      return;
    }

    setIsRanking(true);
    try {
      const res = await rankResumes(jobDescription);
      setRanked(res.data.ranked_resumes);
    } catch (err) {
      alert("Error ranking resumes. Please try again.");
      console.error(err);
    } finally {
      setIsRanking(false);
    }
  };

  const handleJobDescSubmit = () => {
    if (jobDescription.trim()) {
      setShowJobDescModal(false);
      handleRank();
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" className="me-3" style={{color: 'var(--accent-primary)'}}>
            <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
          </svg>
          Resume Dashboard
        </h1>
        <p className="page-subtitle">
          Rank and analyze uploaded resumes against job requirements using AI-powered screening
        </p>
      </div>

      {/* Job Description Card */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="custom-card">
            <h4 className="mb-3" style={{color: 'var(--text-primary)'}}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
              Job Description
            </h4>
            <textarea
              className="form-control mb-3"
              rows="4"
              placeholder="Enter the job description to rank resumes against..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-tertiary)',
                borderColor: 'var(--border-primary)',
                color: 'var(--text-primary)',
                resize: 'vertical'
              }}
            />
            <div className="d-flex gap-3 flex-wrap">
              <button
                className="btn btn-custom-primary"
                onClick={handleRank}
                disabled={isRanking || !jobDescription.trim()}
              >
                {isRanking ? (
                  <>
                    <span className="loading-spinner me-2"></span>
                    Ranking Resumes...
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                      <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
                    </svg>
                    Rank Resumes
                  </>
                )}
              </button>
              
              <button
                className="btn btn-custom-secondary"
                onClick={() => downloadReport("excel")}
                disabled={ranked.length === 0}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M8,13H16V15H8V13Z" />
                </svg>
                Export Excel
              </button>
              
              <button
                className="btn btn-custom-secondary"
                onClick={() => downloadReport("pdf")}
                disabled={ranked.length === 0}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                Export PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {ranked.length > 0 && (
        <>
          {/* Statistics Cards */}
          <div className="row mb-4">
            <div className="col-md-4">
              <div className="custom-card text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-primary)'}}>
                  {ranked.length}
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  Resumes Analyzed
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="custom-card text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-success)'}}>
                  {ranked.filter(r => r.score >= 80).length}
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  High Match (80%+)
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="custom-card text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-warning)'}}>
                  {Math.round(ranked.reduce((sum, r) => sum + r.score, 0) / ranked.length)}%
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  Average Score
                </p>
              </div>
            </div>
          </div>

          {/* Ranked Results Table */}
          <div className="row mb-4">
            <div className="col-12">
              <div className="custom-card">
                <h4 className="mb-4" style={{color: 'var(--text-primary)'}}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                    <path d="M3,3H21V5H3V3M4,6H20V8H4V6M5,9H19V11H5V9M6,12H18V14H6V12M7,15H17V17H7V15M8,18H16V20H8V18Z" />
                  </svg>
                  Ranked Results
                </h4>
                <ResultsTable resumes={ranked} />
              </div>
            </div>
          </div>

          {/* Insights Chart */}
          <div className="row">
            <div className="col-12">
              <div className="custom-card">
                <h4 className="mb-4" style={{color: 'var(--text-primary)'}}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                    <path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z" />
                  </svg>
                  Insights & Analytics
                </h4>
                <InsightsChart />
              </div>
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {ranked.length === 0 && !isRanking && (
        <div className="row">
          <div className="col-12">
            <div className="text-center py-5" style={{color: 'var(--text-secondary)'}}>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{color: 'var(--text-muted)'}}>
                <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
              </svg>
              <h5>No Results Yet</h5>
              <p>Enter a job description above and click &quot;Rank Resumes&quot; to analyze uploaded resumes.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
