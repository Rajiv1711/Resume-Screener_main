import React, { useState } from "react";
import { uploadResume } from "../services/api";

const UploadResume = ({ onUpload, onUploadingChange }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files || files.length === 0) {
      alert("Please select at least one file");
      return;
    }
    
    setUploading(true);
    if (onUploadingChange) onUploadingChange(true);
    const formData = new FormData();
    // Append all files under the same field name expected by backend
    for (const f of files) {
      formData.append("resume", f);
    }

    try {
      const res = await uploadResume(formData);
      onUpload(res.data);
      setFiles([]); // Reset selection
      // Success message will be shown by parent component
    } catch (err) {
      console.error(err);
      alert("Error uploading resume. Please try again.");
    } finally {
      setUploading(false);
      if (onUploadingChange) onUploadingChange(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="form-label fw-semibold mb-3" style={{color: 'var(--text-primary)'}}>
          Select Resume File(s)
        </label>
        
        {/* Drag and Drop Zone */}
        <div 
          className={`border-2 border-dashed rounded-3 p-5 text-center position-relative ${
            dragActive ? 'border-primary' : ''
          }`}
          style={{
            borderColor: dragActive ? 'var(--accent-primary)' : 'var(--border-primary)',
            backgroundColor: dragActive ? 'rgba(88, 166, 255, 0.05)' : 'var(--bg-tertiary)',
            transition: 'all 0.3s ease',
            cursor: 'pointer'
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            id="fileInput"
            type="file"
            className="d-none"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files))}
            accept=".pdf,.doc,.docx,.txt,.zip"
            disabled={uploading}
          />
          
          <div className="mb-3">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" style={{color: 'var(--accent-primary)'}}>
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M12,12L16,16H13.5V19H10.5V16H8L12,12Z" />
            </svg>
          </div>
          
          <h5 className="mb-2" style={{color: 'var(--text-primary)'}}>
            {dragActive ? 'Drop your files here' : 'Click to upload or drag & drop'}
          </h5>
          
          <p className="mb-0" style={{color: 'var(--text-secondary)'}}>
            Supports PDF, DOC, DOCX, TXT, and ZIP files
          </p>
          
          <p className="small mt-2 mb-0" style={{color: 'var(--text-muted)'}}>
            Maximum file size: 10MB
          </p>
        </div>
      </div>

      {/* Selected Files Display */}
      {files && files.length > 0 && (
        <div className="mb-4">
          {files.map((f, idx) => (
            <div key={idx} className="d-flex align-items-center p-3 rounded mb-2" style={{
              backgroundColor: 'rgba(88, 166, 255, 0.1)',
              border: '1px solid var(--accent-primary)'
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-3" style={{color: 'var(--accent-primary)'}}>
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
              <div className="flex-grow-1">
                <div className="fw-semibold" style={{color: 'var(--text-primary)'}}>
                  {f.name}
                </div>
                <div className="small" style={{color: 'var(--text-secondary)'}}>
                  {formatFileSize(f.size)}
                </div>
              </div>
              <button
                type="button"
                className="btn btn-sm"
                onClick={(e) => {
                  e.stopPropagation();
                  setFiles(prev => prev.filter((_, i) => i !== idx));
                }}
                style={{
                  color: 'var(--text-muted)',
                  backgroundColor: 'transparent',
                  border: 'none'
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      <div className="d-grid">
        <button
          type="submit"
          className="btn btn-custom-primary btn-lg"
          disabled={files.length === 0 || uploading}
        >
          {uploading ? (
            <>
              <span className="loading-spinner me-2"></span>
              Uploading...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z" />
              </svg>
              Upload Resume
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default UploadResume;
