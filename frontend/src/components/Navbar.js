// frontend/src/components/Navbar.js
import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import { isAuthenticated } from "../services/api";
import LogoutButton from "./LogoutButton";

const Navbar = () => {
  const { accounts } = useMsal();
  const location = useLocation();
  const [guestTimeLeft, setGuestTimeLeft] = useState(null);
  const [authStatus, setAuthStatus] = useState(null);

  const isActive = (path) => location.pathname === path;

  // Update authentication status and guest timer
  useEffect(() => {
    const updateAuthStatus = () => {
      const auth = isAuthenticated();
      setAuthStatus(auth);
      
      if (auth && auth.type === 'guest') {
        const now = new Date();
        const expiry = new Date(auth.expiry);
        const secondsLeft = Math.max(0, Math.floor((expiry - now) / 1000));
        setGuestTimeLeft(secondsLeft);
        
        // If expired, clear the status
        if (secondsLeft <= 0) {
          setAuthStatus(null);
          setGuestTimeLeft(null);
        }
      } else {
        setGuestTimeLeft(null);
      }
    };
    
    // Initial update
    updateAuthStatus();
    
    // Update every second for guest timer
    const interval = setInterval(updateAuthStatus, 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Determine username based on auth type
  const getUsername = () => {
    if (accounts && accounts[0]) {
      return accounts[0].name || accounts[0].username;
    }
    if (authStatus && authStatus.type === 'guest') {
      return 'Guest User';
    }
    return null;
  };

  const username = getUsername();

  // Format time remaining for guest users
  const formatTimeLeft = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{
      backgroundColor: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-primary)',
      padding: '1rem 0',
      backdropFilter: 'blur(10px)'
    }}>
      <div className="container-fluid px-4">
        {/* Brand */}
        <Link 
          to="/" 
          className="navbar-brand d-flex align-items-center"
          style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: 'var(--accent-primary)',
            textDecoration: 'none'
          }}
        >
          <svg 
            width="32" 
            height="32" 
            viewBox="0 0 24 24" 
            fill="currentColor" 
            className="me-2"
            style={{ color: 'var(--accent-primary)' }}
          >
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
          Resume Screener
        </Link>

        {/* Navigation Links */}
        <div className="navbar-nav me-auto ms-4">
          <Link 
            to="/upload" 
            className={`nav-link px-3 py-2 rounded me-2 ${isActive('/upload') ? 'active' : ''}`}
            style={{
              color: isActive('/upload') ? 'var(--accent-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive('/upload') ? 'rgba(79, 209, 197, 0.12)' : 'transparent',
              fontWeight: '500',
              textDecoration: 'none',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/upload')) {
                e.target.style.color = 'var(--text-primary)';
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/upload')) {
                e.target.style.color = 'var(--text-secondary)';
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-1">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
            </svg>
            Upload
          </Link>
          
          <Link 
            to="/dashboard" 
            className={`nav-link px-3 py-2 rounded ${isActive('/dashboard') ? 'active' : ''}`}
            style={{
              color: isActive('/dashboard') ? 'var(--accent-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive('/dashboard') ? 'rgba(79, 209, 197, 0.12)' : 'transparent',
              fontWeight: '500',
              textDecoration: 'none',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/dashboard')) {
                e.target.style.color = 'var(--text-primary)';
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/dashboard')) {
                e.target.style.color = 'var(--text-secondary)';
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-1">
              <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
            </svg>
            Dashboard
          </Link>
        </div>

        {/* User Info and Logout */}
        <div className="d-flex align-items-center">
          {username && (
            <div className="d-flex align-items-center me-3">
              <span 
                className="px-3 py-1 rounded d-flex align-items-center"
                style={{
                  color: 'var(--text-primary)',
                  backgroundColor: authStatus && authStatus.type === 'guest' 
                    ? 'rgba(255, 193, 7, 0.1)' 
                    : 'var(--bg-tertiary)',
                  border: authStatus && authStatus.type === 'guest' 
                    ? '1px solid rgba(255, 193, 7, 0.3)' 
                    : 'none',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                  <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
                </svg>
                {username}
                {authStatus && authStatus.type === 'guest' && (
                  <span 
                    className="badge ms-2"
                    style={{
                      backgroundColor: guestTimeLeft > 60 ? 'var(--accent-success)' 
                        : guestTimeLeft > 30 ? 'var(--accent-warning)' 
                        : 'var(--accent-danger)',
                      color: 'white',
                      fontSize: '0.75rem'
                    }}
                  >
                    {guestTimeLeft !== null ? formatTimeLeft(guestTimeLeft) : '0:00'}
                  </span>
                )}
              </span>
            </div>
          )}
          <LogoutButton />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
