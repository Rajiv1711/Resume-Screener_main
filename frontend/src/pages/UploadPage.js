import React, { useState } from "react";
import UploadResume from "../components/UploadResume";

const UploadPage = () => {
  const [uploaded, setUploaded] = useState(null);

  return (
    <div className="page-container">
      <div className="page-header text-center">
        <h1 className="page-title">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" className="me-3" style={{color: 'var(--accent-primary)'}}>
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
          Upload Resumes
        </h1>
        <p className="page-subtitle">
          Upload individual resumes or ZIP files containing multiple resumes for AI-powered screening
        </p>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-8 col-xl-6">
          <div className="custom-card">
            <UploadResume onUpload={setUploaded} />
          </div>

          {uploaded && (
            <div className="alert alert-success d-flex align-items-center mt-4" role="alert" style={{
              backgroundColor: 'rgba(35, 134, 54, 0.15)',
              borderColor: 'var(--accent-success)',
              color: 'var(--text-primary)'
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-3" style={{color: 'var(--accent-success)'}}>
                <path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M11,16.5L18,9.5L16.59,8.09L11,13.67L7.41,10.09L6,11.5L11,16.5Z" />
              </svg>
              <div>
                <strong>Upload Successful!</strong><br/>
                Successfully parsed {Array.isArray(uploaded.files) ? uploaded.files.length : 1} resume(s). 
                You can now go to the Dashboard to rank and analyze them.
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="row mt-5">
        <div className="col-12">
          <div className="text-center">
            <h3 className="mb-4" style={{color: 'var(--text-secondary)'}}>
              Supported File Formats
            </h3>
            <div className="row justify-content-center">
              <div className="col-md-8">
                <div className="d-flex flex-wrap justify-content-center gap-3">
                  {[
                    { name: 'PDF', icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' },
                    { name: 'DOC/DOCX', icon: 'M6,2A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2H6Z' },
                    { name: 'TXT', icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' },
                    { name: 'ZIP', icon: 'M14,12V19.88C14.04,20.18 13.94,20.5 13.71,20.71C13.32,21.1 12.69,21.1 12.3,20.71L10.59,19H10V12H14M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4A2,2 0 0,1 6,2Z' }
                  ].map((format, idx) => (
                    <div key={idx} className="px-3 py-2 rounded" style={{
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-primary)',
                      color: 'var(--text-secondary)'
                    }}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                        <path d={format.icon} />
                      </svg>
                      {format.name}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
