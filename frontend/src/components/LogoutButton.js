// frontend/src/components/LogoutButton.js
import React from "react";
import { useMsal } from "@azure/msal-react";
import { logout } from "../services/api";

const LogoutButton = () => {
  const { instance } = useMsal();

  const handleLogout = async () => {
    try {
      // MSAL logout (redirect flow)
      await logout();
      // fallback: clear localStorage if any legacy token stored
      localStorage.removeItem("access_token");
    } catch (err) {
      console.error("Logout error", err);
      // clear local storage fallback
      localStorage.removeItem("access_token");
    }
  };

  return (
    <button 
      className="btn btn-outline-light btn-sm"
      onClick={handleLogout}
      style={{
        borderColor: 'var(--border-primary)',
        color: 'var(--text-secondary)',
        backgroundColor: 'transparent',
        transition: 'all 0.3s ease'
      }}
      onMouseEnter={(e) => {
        e.target.style.backgroundColor = 'rgba(218, 54, 51, 0.1)';
        e.target.style.borderColor = 'var(--accent-danger)';
        e.target.style.color = 'var(--accent-danger)';
      }}
      onMouseLeave={(e) => {
        e.target.style.backgroundColor = 'transparent';
        e.target.style.borderColor = 'var(--border-primary)';
        e.target.style.color = 'var(--text-secondary)';
      }}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-1">
        <path d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z" />
      </svg>
      Logout
    </button>
  );
};

export default LogoutButton;
