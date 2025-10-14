import React from "react";
import { motion } from "framer-motion";

const ResultsTable = ({ resumes }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-success)';
    if (score >= 60) return 'var(--accent-warning)';
    return 'var(--accent-danger)';
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  if (!resumes || resumes.length === 0) {
    return (
      <div className="text-center py-4" style={{color: 'var(--text-secondary)'}}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" className="mb-3">
          <path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M11,16.5L6.5,12L7.91,10.59L11,13.67L16.59,8.09L18,9.5L11,16.5Z" />
        </svg>
        <p>No resumes to display</p>
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <table className="table table-dark table-hover">
        <thead>
          <tr style={{borderColor: 'var(--border-primary)'}}>
            <th scope="col" className="fw-semibold" style={{color: 'var(--text-primary)', backgroundColor: 'var(--bg-tertiary)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
              </svg>
              Candidate
            </th>
            <th scope="col" className="fw-semibold text-center" style={{color: 'var(--text-primary)', backgroundColor: 'var(--bg-tertiary)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.46,13.97L5.82,21L12,17.27Z" />
              </svg>
              Match Score
            </th>
            <th scope="col" className="fw-semibold" style={{color: 'var(--text-primary)', backgroundColor: 'var(--bg-tertiary)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M12,2A2,2 0 0,1 14,4A2,2 0 0,1 12,6A2,2 0 0,1 10,4A2,2 0 0,1 12,2M21,9V7L15,1L13.5,2.5L16.17,5.17L10.5,10.84C10.19,11.15 10,11.55 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12C14,11.55 13.81,11.15 13.5,10.84L19.17,5.17L21.83,7.83L23,6.5L21,9M4.93,5.82C3.08,5.82 1.6,7.3 1.6,9.15C1.6,11 3.08,12.47 4.93,12.47C6.78,12.47 8.25,11 8.25,9.15C8.25,7.3 6.78,5.82 4.93,5.82M11.5,22H13V20H11.5V22M8.5,20V22H10V20H8.5M5.5,20V22H7V20H5.5M2.5,20V22H4V20H2.5Z" />
              </svg>
              Top Skills
            </th>
          </tr>
        </thead>
        <tbody>
          {resumes.map((resume, idx) => (
            <motion.tr
              key={idx}
              className="align-middle"
              style={{
                borderColor: 'var(--border-primary)',
                backgroundColor: idx % 2 === 0 ? 'var(--bg-secondary)' : 'rgba(255, 255, 255, 0.02)'
              }}
              whileHover={{ scale: 1.01, backgroundColor: 'rgba(79, 209, 197, 0.06)' }}
              transition={{ scale: { type: 'spring', stiffness: 300, damping: 24 } }}
            >
              <td style={{color: 'var(--text-primary)'}}>
                <div className="d-flex align-items-center">
                  <div className="me-3">
                    <div 
                      className="rounded-circle d-flex align-items-center justify-content-center fw-bold"
                      style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: 'var(--accent-primary)',
                        color: 'white',
                        fontSize: '1.1rem'
                      }}
                    >
                      {idx + 1}
                    </div>
                  </div>
                  <div>
                    <div className="fw-semibold">
                      {resume.name || `Candidate ${idx + 1}`}
                    </div>
                    <div className="small" style={{color: 'var(--text-secondary)'}}>
                      Resume #{idx + 1}
                    </div>
                  </div>
                </div>
              </td>
              <td className="text-center">
                <div className="d-flex flex-column align-items-center">
                  <span 
                    className="badge rounded-pill px-3 py-2 mb-1"
                    style={{
                      backgroundColor: `${getScoreColor(resume.score)}20`,
                      color: getScoreColor(resume.score),
                      border: `1px solid ${getScoreColor(resume.score)}`,
                      fontSize: '0.9rem',
                      fontWeight: '600'
                    }}
                  >
                    {resume.score}%
                  </span>
                  <div className="progress" style={{width: '60px', height: '4px'}}>
                    <div 
                      className="progress-bar"
                      role="progressbar"
                      style={{
                        width: `${resume.score}%`,
                        backgroundColor: getScoreColor(resume.score)
                      }}
                      aria-valuenow={resume.score}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    ></div>
                  </div>
                </div>
              </td>
              <td style={{color: 'var(--text-primary)'}}>
                <div className="d-flex flex-wrap gap-1">
                  {resume.skills && resume.skills.length > 0 ? (
                    resume.skills.slice(0, 5).map((skill, skillIdx) => (
                      <motion.span
                        key={skillIdx}
                        className="badge rounded-pill px-2 py-1"
                        style={{
                          backgroundColor: 'var(--bg-tertiary)',
                          color: 'var(--text-secondary)',
                          border: '1px solid var(--border-primary)',
                          fontSize: '0.75rem'
                        }}
                        whileHover={{ scale: 1.06, color: '#ffffff' }}
                        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                      >
                        {skill}
                      </motion.span>
                    ))
                  ) : (
                    <span style={{color: 'var(--text-muted)', fontStyle: 'italic'}}>
                      No skills data
                    </span>
                  )}
                  {resume.skills && resume.skills.length > 5 && (
                    <motion.span 
                      className="badge rounded-pill px-2 py-1"
                      style={{
                        backgroundColor: 'var(--accent-primary)',
                        color: 'white',
                        fontSize: '0.75rem'
                      }}
                      whileHover={{ scale: 1.06 }}
                    >
                      +{resume.skills.length - 5} more
                    </motion.span>
                  )}
                </div>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
