// frontend/src/components/Navbar.js
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import LogoutButton from "./LogoutButton";

const Navbar = () => {
  const { accounts } = useMsal();
  const location = useLocation();
  const username =
    accounts && accounts[0] ? accounts[0].name || accounts[0].username : null;

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{
      backgroundColor: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-primary)',
      padding: '1rem 0'
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
              backgroundColor: isActive('/upload') ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
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
              backgroundColor: isActive('/dashboard') ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
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
            <span 
              className="me-3 px-3 py-1 rounded"
              style={{
                color: 'var(--text-primary)',
                backgroundColor: 'var(--bg-tertiary)',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
              </svg>
              {username}
            </span>
          )}
          <LogoutButton />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
