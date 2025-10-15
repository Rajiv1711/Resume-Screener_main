import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ParallaxHero from '../components/ParallaxHero';
import GlassCard from '../components/GlassCard';
import SessionManager from '../components/SessionManager';
import { getCurrentUserId, getApiBaseUrl, createAuthHeaders, ensureUserIdInStorage } from '../utils/user';

const SessionsPage = ({ pushToast }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessionFiles, setSessionFiles] = useState({});
  const [loading, setLoading] = useState(false);

  // Load session details when component mounts
  useEffect(() => {
    loadSessionDetails();
  }, []);

  const loadSessionDetails = async () => {
    console.log('🔄 Loading session details...');
    setLoading(true);
    try {
      // Ensure user ID is properly set
      const userId = ensureUserIdInStorage();
      console.log('👤 User ID:', userId);
      
      // Load all sessions
      const apiBaseUrl = getApiBaseUrl();
      const sessionsUrl = `${apiBaseUrl}/sessions/list`;
      console.log('📡 Fetching sessions from:', sessionsUrl);
      const response = await fetch(sessionsUrl, {
        headers: createAuthHeaders()
      });
      
      console.log('📨 Response status:', response.status);
      console.log('📨 Response headers:', response.headers);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📦 Sessions API response:', data);
      
      if (data.status === 'success') {
        console.log('✅ Sessions loaded:', data.sessions.length, 'sessions');
        setSessions(data.sessions);
        
        // Load files for each session
        console.log('📁 Loading files for', data.sessions.length, 'sessions...');
        const filesData = {};
        for (const session of data.sessions) {
          try {
            console.log(`📂 Loading files for session: ${session.session_id}`);
            const filesUrl = `${apiBaseUrl}/sessions/${session.session_id}/files`;
            console.log(`📡 Fetching files from: ${filesUrl}`);
            const filesResponse = await fetch(filesUrl, {
              headers: createAuthHeaders()
            });
            const filesResult = await filesResponse.json();
            console.log(`📋 Files response for ${session.session_id}:`, filesResult);
            if (filesResult.status === 'success') {
              filesData[session.session_id] = filesResult.files;
              console.log(`✅ Loaded ${filesResult.files.length} files for session ${session.session_id}`);
            } else {
              console.log(`❌ Files API returned non-success for session ${session.session_id}:`, filesResult.status);
            }
          } catch (error) {
            console.warn(`⚠️ Failed to load files for session ${session.session_id}:`, error);
            filesData[session.session_id] = [];
          }
        }
        console.log('📦 Final filesData:', filesData);
        setSessionFiles(filesData);
      }

      // Load current session
      const currentUrl = `${apiBaseUrl}/sessions/current`;
      console.log('🔄 Fetching current session from:', currentUrl);
      const currentResponse = await fetch(currentUrl, {
        headers: createAuthHeaders()
      });
      const currentData = await currentResponse.json();
      if (currentData.status === 'success') {
        setCurrentSession(currentData.session_id);
      }
      } else {
        console.log('❌ Sessions API returned non-success status:', data.status);
      }
    } catch (error) {
      console.error('❌ Failed to load session details:', error);
      console.error('❌ Error details:', {
        message: error.message,
        stack: error.stack
      });
      pushToast?.({ title: 'Error', message: `Failed to load session details: ${error.message}`, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSessionChange = (sessionId) => {
    setCurrentSession(sessionId);
    loadSessionDetails(); // Refresh data
  };

  const formatDate = (isoString) => {
    if (!isoString || isoString === 'Unknown') return 'Unknown';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown';
    }
  };

  const getFileTypeIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z';
      case 'doc':
      case 'docx':
        return 'M6,2A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2H6Z';
      case 'txt':
        return 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z';
      default:
        return 'M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4A2,2 0 0,1 6,2Z';
    }
  };

  return (
    <div className="page-container">
      <ParallaxHero
        title="Session Management"
        subtitle="Organize and manage your upload sessions"
      />

      <div className="row">
        {/* Session Manager */}
        <div className="col-lg-4 mb-4">
          <SessionManager 
            onSessionChange={handleSessionChange}
            pushToast={pushToast}
          />
        </div>

        {/* Session Details */}
        <div className="col-lg-8">
          <GlassCard>
            <h4 className="mb-4" style={{ color: 'var(--text-primary)' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M19,20H4C2.89,20 2,19.1 2,18V6C2,4.89 2.89,4 4,4H10L12,6H19A2,2 0 0,1 21,8H21L4,8V18L6.14,10H23.21L20.93,18.5C20.7,19.37 19.92,20 19,20Z" />
              </svg>
              Session Overview
            </h4>

            {loading ? (
              <div className="text-center py-4">
                <div className="spinner-border" role="status" style={{ color: 'var(--accent-primary)' }}>
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-3" style={{ color: 'var(--text-secondary)' }}>Loading session details...</p>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-5" style={{ color: 'var(--text-secondary)' }}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{ color: 'var(--text-muted)' }}>
                  <path d="M19,20H4C2.89,20 2,19.1 2,18V6C2,4.89 2.89,4 4,4H10L12,6H19A2,2 0 0,1 21,8H21L4,8V18L6.14,10H23.21L20.93,18.5C20.7,19.37 19.92,20 19,20Z" />
                </svg>
                <h5>No Sessions Found</h5>
                <p>Create your first session using the "New Session" button.</p>
              </div>
            ) : (
              <div className="row">
                {sessions.map((session) => (
                  <div key={session.session_id} className="col-md-6 mb-4">
                    <motion.div
                      className={`session-detail-card p-4 rounded ${session.session_id === currentSession ? 'active' : ''}`}
                      style={{
                        backgroundColor: session.session_id === currentSession 
                          ? 'rgba(79, 209, 197, 0.1)' 
                          : 'var(--bg-tertiary)',
                        border: session.session_id === currentSession 
                          ? '2px solid var(--accent-primary)' 
                          : '1px solid var(--border-primary)',
                        transition: 'all 0.3s ease'
                      }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <h5 style={{ color: 'var(--text-primary)', margin: 0 }}>
                          {session.name}
                        </h5>
                        {session.session_id === currentSession && (
                          <span 
                            className="badge"
                            style={{
                              backgroundColor: 'var(--accent-primary)',
                              color: 'white',
                              fontSize: '0.7rem'
                            }}
                          >
                            Active
                          </span>
                        )}
                      </div>

                      <div className="mb-3" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <div className="mb-1">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                            <path d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z" />
                          </svg>
                          Created: {formatDate(session.created)}
                        </div>
                        <div className="mb-1">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                            <path d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4A2,2 0 0,1 6,2M15,18V16H6V18H15M18,14V12H6V14H18Z" />
                          </svg>
                          Files: {session.blob_count || 0}
                        </div>
                        <div>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                            <path d="M12,2A2,2 0 0,1 14,4A2,2 0 0,1 12,6A2,2 0 0,1 10,4A2,2 0 0,1 12,2M21,9V7L15,1H5C3.89,1 3,1.89 3,3V7H3V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V9M19,19H5V9H19V19Z" />
                          </svg>
                          ID: {session.session_id.slice(-8)}
                        </div>
                      </div>

                      {/* File List */}
                      {sessionFiles[session.session_id] && sessionFiles[session.session_id].length > 0 && (
                        <div className="files-preview">
                          <h6 style={{ color: 'var(--text-primary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                            Files in this session:
                          </h6>
                          <div className="files-list" style={{ maxHeight: '120px', overflowY: 'auto' }}>
                            {sessionFiles[session.session_id].slice(0, 5).map((file, index) => (
                              <div key={index} className="file-item d-flex align-items-center mb-1" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                                  <path d={getFileTypeIcon(file)} />
                                </svg>
                                <span className="file-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                  {file.split('/').pop()}
                                </span>
                              </div>
                            ))}
                            {sessionFiles[session.session_id].length > 5 && (
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                                ... and {sessionFiles[session.session_id].length - 5} more files
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>

          {/* Session Statistics */}
          {sessions.length > 0 && (
            <div className="row mt-4">
              <div className="col-12">
                <GlassCard>
                  <h5 className="mb-3" style={{ color: 'var(--text-primary)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                      <path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z" />
                    </svg>
                    Session Statistics
                  </h5>
                  <div className="row">
                    <div className="col-md-3 text-center">
                      <h3 className="mb-2" style={{ color: 'var(--accent-primary)' }}>
                        {sessions.length}
                      </h3>
                      <p className="mb-0" style={{ color: 'var(--text-secondary)' }}>
                        Total Sessions
                      </p>
                    </div>
                    <div className="col-md-3 text-center">
                      <h3 className="mb-2" style={{ color: 'var(--accent-success)' }}>
                        {sessions.reduce((sum, s) => sum + (s.blob_count || 0), 0)}
                      </h3>
                      <p className="mb-0" style={{ color: 'var(--text-secondary)' }}>
                        Total Files
                      </p>
                    </div>
                    <div className="col-md-3 text-center">
                      <h3 className="mb-2" style={{ color: 'var(--accent-warning)' }}>
                        {Math.round(sessions.reduce((sum, s) => sum + (s.blob_count || 0), 0) / sessions.length) || 0}
                      </h3>
                      <p className="mb-0" style={{ color: 'var(--text-secondary)' }}>
                        Avg Files/Session
                      </p>
                    </div>
                    <div className="col-md-3 text-center">
                      <h3 className="mb-2" style={{ color: 'var(--accent-info)' }}>
                        {currentSession ? sessions.find(s => s.session_id === currentSession)?.name?.slice(0, 10) || 'None' : 'None'}
                      </h3>
                      <p className="mb-0" style={{ color: 'var(--text-secondary)' }}>
                        Active Session
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SessionsPage;