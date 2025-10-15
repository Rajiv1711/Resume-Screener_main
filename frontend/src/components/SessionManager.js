import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from './GlassCard';

const SessionManager = ({ onSessionChange, pushToast }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [renameSessionId, setRenameSessionId] = useState(null);
  const [renameSessionName, setRenameSessionName] = useState('');
  const [loading, setLoading] = useState(false);

  // Load sessions and current session on mount
  useEffect(() => {
    loadSessions();
    loadCurrentSession();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/sessions/list', {
        headers: {
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const loadCurrentSession = async () => {
    try {
      const response = await fetch('/api/sessions/current', {
        headers: {
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setCurrentSession(data.session_id);
      }
    } catch (error) {
      console.error('Failed to load current session:', error);
    }
  };

  const createSession = async () => {
    if (!newSessionName.trim()) {
      pushToast?.({ title: 'Error', message: 'Please enter a session name', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/sessions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        },
        body: JSON.stringify({ name: newSessionName })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        pushToast?.({ title: 'Success', message: 'New session created', type: 'success' });
        setNewSessionName('');
        setShowModal(false);
        await loadSessions();
        await setActiveSession(data.session_id);
      }
    } catch (error) {
      pushToast?.({ title: 'Error', message: 'Failed to create session', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const setActiveSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/set-active`, {
        method: 'POST',
        headers: {
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        }
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        setCurrentSession(sessionId);
        onSessionChange?.(sessionId);
        pushToast?.({ title: 'Success', message: 'Active session changed', type: 'success' });
      }
    } catch (error) {
      pushToast?.({ title: 'Error', message: 'Failed to switch session', type: 'error' });
    }
  };

  const renameSession = async () => {
    if (!renameSessionName.trim()) {
      pushToast?.({ title: 'Error', message: 'Please enter a new name', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/sessions/${renameSessionId}/name`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        },
        body: JSON.stringify({ name: renameSessionName })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        pushToast?.({ title: 'Success', message: 'Session renamed', type: 'success' });
        setRenameSessionName('');
        setRenameSessionId(null);
        setShowRenameModal(false);
        await loadSessions();
      }
    } catch (error) {
      pushToast?.({ title: 'Error', message: 'Failed to rename session', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId, sessionName) => {
    if (!window.confirm(`Are you sure you want to delete "${sessionName}"? This will remove all files in this session.`)) {
      return;
    }

    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'X-User-Id': localStorage.getItem('user_id') || 'guest'
        }
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        pushToast?.({ title: 'Success', message: `Deleted ${data.deleted_blobs} files`, type: 'success' });
        await loadSessions();
        
        // If deleted session was active, reload current
        if (sessionId === currentSession) {
          await loadCurrentSession();
        }
      }
    } catch (error) {
      pushToast?.({ title: 'Error', message: 'Failed to delete session', type: 'error' });
    }
  };

  const formatDate = (isoString) => {
    if (!isoString || isoString === 'Unknown') return 'Unknown';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
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

  return (
    <div className="session-manager">
      <GlassCard>
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 style={{ color: 'var(--text-primary)', margin: 0 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
              <path d="M19,20H4C2.89,20 2,19.1 2,18V6C2,4.89 2.89,4 4,4H10L12,6H19A2,2 0 0,1 21,8H21L4,8V18L6.14,10H23.21L20.93,18.5C20.7,19.37 19.92,20 19,20Z" />
            </svg>
            Upload Sessions
          </h5>
          <button 
            className="btn btn-custom-primary btn-sm"
            onClick={() => setShowModal(true)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-1">
              <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
            </svg>
            New Session
          </button>
        </div>

        <div className="sessions-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
          {sessions.length === 0 ? (
            <div className="text-center py-3" style={{ color: 'var(--text-secondary)' }}>
              <p className="mb-0">No sessions yet. Create one to get started!</p>
            </div>
          ) : (
            <AnimatePresence>
              {sessions.map((session) => (
                <motion.div
                  key={session.session_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  className={`session-item p-3 mb-2 rounded ${session.session_id === currentSession ? 'active' : ''}`}
                  style={{
                    backgroundColor: session.session_id === currentSession 
                      ? 'rgba(79, 209, 197, 0.1)' 
                      : 'var(--bg-tertiary)',
                    border: session.session_id === currentSession 
                      ? '2px solid var(--accent-primary)' 
                      : '1px solid var(--border-primary)',
                    cursor: 'pointer'
                  }}
                  onClick={() => session.session_id !== currentSession && setActiveSession(session.session_id)}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center mb-1">
                        <strong style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                          {session.name}
                        </strong>
                        {session.session_id === currentSession && (
                          <span 
                            className="badge ms-2"
                            style={{
                              backgroundColor: 'var(--accent-primary)',
                              color: 'white',
                              fontSize: '0.7rem',
                              padding: '2px 8px'
                            }}
                          >
                            Active
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <span className="me-3">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="me-1">
                            <path d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z" />
                          </svg>
                          {formatDate(session.created)}
                        </span>
                        <span>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="me-1">
                            <path d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M15,18V16H6V18H15M18,14V12H6V14H18Z" />
                          </svg>
                          {session.blob_count} files
                        </span>
                      </div>
                    </div>
                    <div className="d-flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        className="btn btn-sm"
                        style={{
                          backgroundColor: 'transparent',
                          border: '1px solid var(--border-primary)',
                          color: 'var(--text-secondary)',
                          padding: '4px 8px'
                        }}
                        onClick={() => {
                          setRenameSessionId(session.session_id);
                          setRenameSessionName(session.name);
                          setShowRenameModal(true);
                        }}
                        title="Rename"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" />
                        </svg>
                      </button>
                      <button
                        className="btn btn-sm"
                        style={{
                          backgroundColor: 'transparent',
                          border: '1px solid var(--accent-danger)',
                          color: 'var(--accent-danger)',
                          padding: '4px 8px'
                        }}
                        onClick={() => deleteSession(session.session_id, session.name)}
                        title="Delete"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </GlassCard>

      {/* Create Session Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            className="modal-backdrop"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1050
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModal(false)}
          >
            <motion.div
              className="modal-content p-4 rounded"
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-primary)',
                maxWidth: '500px',
                width: '90%'
              }}
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h5 style={{ color: 'var(--text-primary)' }} className="mb-3">Create New Session</h5>
              <input
                type="text"
                className="form-control mb-3"
                placeholder="Enter session name (e.g., 'ML Engineer Applications')"
                value={newSessionName}
                onChange={(e) => setNewSessionName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createSession()}
                style={{
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-primary)',
                  color: 'var(--text-primary)'
                }}
                autoFocus
              />
              <div className="d-flex gap-2 justify-content-end">
                <button
                  className="btn btn-custom-secondary"
                  onClick={() => setShowModal(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  className="btn btn-custom-primary"
                  onClick={createSession}
                  disabled={loading || !newSessionName.trim()}
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rename Session Modal */}
      <AnimatePresence>
        {showRenameModal && (
          <motion.div
            className="modal-backdrop"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1050
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowRenameModal(false)}
          >
            <motion.div
              className="modal-content p-4 rounded"
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-primary)',
                maxWidth: '500px',
                width: '90%'
              }}
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h5 style={{ color: 'var(--text-primary)' }} className="mb-3">Rename Session</h5>
              <input
                type="text"
                className="form-control mb-3"
                placeholder="Enter new session name"
                value={renameSessionName}
                onChange={(e) => setRenameSessionName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && renameSession()}
                style={{
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-primary)',
                  color: 'var(--text-primary)'
                }}
                autoFocus
              />
              <div className="d-flex gap-2 justify-content-end">
                <button
                  className="btn btn-custom-secondary"
                  onClick={() => setShowRenameModal(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  className="btn btn-custom-primary"
                  onClick={renameSession}
                  disabled={loading || !renameSessionName.trim()}
                >
                  {loading ? 'Saving...' : 'Save'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SessionManager;
