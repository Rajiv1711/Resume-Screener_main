import React, { useState } from "react";
import { rankResumes, rankResumesFromFile, downloadReport } from "../services/api";
import ResultsTable from "../components/ResultsTable";
import InsightsChart from "../components/InsightsChart";
import GlassCard from "../components/GlassCard";
import Loader from "../components/Loader";
import ParallaxHero from "../components/ParallaxHero";
import SessionManager from "../components/SessionManager";

const Dashboard = ({ pushToast }) => {
  const [ranked, setRanked] = useState([]);
  const [jobDescription, setJobDescription] = useState("");
  const [jdFile, setJdFile] = useState(null);
  const [isRanking, setIsRanking] = useState(false);
  const [showJobDescModal, setShowJobDescModal] = useState(false);

  const handleRank = async () => {
    if (!jdFile && !jobDescription.trim()) {
      setShowJobDescModal(true);
      return;
    }

    setIsRanking(true);
    try {
      let res;
      if (jdFile && !jobDescription.trim()) {
        const fd = new FormData();
        fd.append("jd_file", jdFile);
        res = await rankResumesFromFile(fd);
      } else {
        res = await rankResumes(jobDescription);
      }
      const ranked = Array.isArray(res.data?.ranked_resumes) ? res.data.ranked_resumes : [];
      const mapped = ranked.map((r, i) => {
        // Extract score - handle both final_score (0-1 from LLM) and hybrid_score
        let score = 0;
        if (r?.final_score !== undefined) {
          score = Math.round(r.final_score * 100);
        } else if (r?.hybrid_score !== undefined) {
          score = Math.round(r.hybrid_score * 100);
        } else if (r?.score !== undefined) {
          score = Math.round(r.score);
        }

        // Extract name - try candidate_name first, then parsed.name, then file
        let name = r?.candidate_name || (r?.parsed && r.parsed.name) || r?.file || `Candidate ${i + 1}`;
        
        // Extract skills - check multiple locations
        let skills = [];
        if (Array.isArray(r?.skills)) {
          skills = r.skills;
        } else if (r?.parsed && Array.isArray(r.parsed.skills)) {
          skills = r.parsed.skills;
        }

        return {
          ...r,
          score,
          name,
          skills
        };
      });
      setRanked(mapped);
    } catch (err) {
      alert("Error ranking resumes. Please try again.");
      console.error(err);
    } finally {
      setIsRanking(false);
      if (pushToast && ranked.length > 0) {
        pushToast({ title: 'Ranking Complete', message: 'Results are ready on the dashboard.', type: 'success' });
      }
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
      <ParallaxHero
        title="Resume Dashboard"
        subtitle="Rank and analyze uploaded resumes against job requirements"
      />

      <div className="row mb-4">
        {/* Session Manager Sidebar */}
        <div className="col-lg-4 mb-4">
          <SessionManager 
            onSessionChange={(sessionId) => {
              console.log('Active session changed to:', sessionId);
              // Clear current rankings when session changes
              setRanked([]);
            }}
            pushToast={pushToast}
          />
        </div>

        {/* Job Description Card */}
        <div className="col-lg-8 mb-4">
          <GlassCard>
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
            {/* JD File Upload */}
            <div className="mb-3">
              <label className="form-label" style={{color: 'var(--text-secondary)'}}>Or upload a job description document (PDF, DOCX, TXT)</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                className="form-control"
                onChange={(e) => setJdFile(e.target.files && e.target.files[0] ? e.target.files[0] : null)}
              />
              {jdFile && (
                <div className="small mt-2" style={{color: 'var(--text-muted)'}}>
                  Selected: {jdFile.name} (<button className="btn btn-link p-0" onClick={() => setJdFile(null)}>clear</button>)
                </div>
              )}
            </div>

            <div className="d-flex gap-3 flex-wrap align-items-center">
              <button
                className="btn btn-custom-primary align-items-center d-flex"
                onClick={handleRank}
                disabled={isRanking || (!jobDescription.trim() && !jdFile)}
              >
                {isRanking ? (
                  <>
                    <Loader size={24} />
                    <span className="ms-2">Ranking Resumes...</span>
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
                Export Excel
              </button>
              <button
                className="btn btn-custom-secondary"
                onClick={() => downloadReport("csv")}
                disabled={ranked.length === 0}
              >
                Export CSV
              </button>
              <button
                className="btn btn-custom-secondary"
                onClick={() => downloadReport("pdf")}
                disabled={ranked.length === 0}
              >
                Export PDF
              </button>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Results Section */}
      {ranked.length > 0 && (
        <>
          {/* Statistics Cards */}
          <div className="row mb-4">
            <div className="col-md-4">
              <GlassCard className="text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-primary)'}}>
                  {ranked.length}
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  Resumes Analyzed
                </p>
              </GlassCard>
            </div>
            <div className="col-md-4">
              <GlassCard className="text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-success)'}}>
                  {ranked.filter(r => r.score >= 80).length}
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  High Match (80%+)
                </p>
              </GlassCard>
            </div>
            <div className="col-md-4">
              <GlassCard className="text-center">
                <h3 className="mb-2" style={{color: 'var(--accent-warning)'}}>
                  {Math.round(ranked.reduce((sum, r) => sum + r.score, 0) / ranked.length)}%
                </h3>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
                  Average Score
                </p>
              </GlassCard>
            </div>
          </div>

          {/* Ranked Results Table */}
          <div className="row mb-4">
            <div className="col-12">
              <GlassCard>
                <h4 className="mb-4" style={{color: 'var(--text-primary)'}}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                    <path d="M3,3H21V5H3V3M4,6H20V8H4V6M5,9H19V11H5V9M6,12H18V14H6V12M7,15H17V17H7V15M8,18H16V20H8V18Z" />
                  </svg>
                  Ranked Results
                </h4>
                <ResultsTable resumes={ranked} />
              </GlassCard>
            </div>
          </div>

          {/* Insights Chart */}
          <div className="row">
            <div className="col-12">
              <GlassCard>
                <h4 className="mb-4" style={{color: 'var(--text-primary)'}}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                    <path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z" />
                  </svg>
                  Insights & Analytics
                </h4>
                <InsightsChart />
              </GlassCard>
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
