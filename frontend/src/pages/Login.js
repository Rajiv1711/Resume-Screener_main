// frontend/src/pages/Login.js
import React, { useState } from "react";
import { useMsal } from "@azure/msal-react";
import { loginPopup, guestLogin, setGuestToken } from "../services/api";
import { useNavigate } from "react-router-dom";
import { ensureUserIdInStorage } from "../utils/user";

const Login = () => {
  const { instance, accounts } = useMsal();
  const navigate = useNavigate();
  const [isGuestLoading, setIsGuestLoading] = useState(false);

  const handleLogin = async () => {
    try {
      await loginPopup(); // shows popup and signs in
      
      // Ensure user_id is properly set
      const userId = ensureUserIdInStorage();
      console.log('🔐 Azure login successful, user ID:', userId);
      
      navigate("/dashboard");
    } catch (err) {
      console.error("Login error", err);
      alert("Login failed");
    }
  };

  const handleGuestLogin = async () => {
    setIsGuestLoading(true);
    try {
      const response = await guestLogin();
      const { access_token, expires_at } = response.data;
      
      // Store guest token
      setGuestToken(access_token, expires_at);
      
      // Ensure user_id is properly set
      const userId = ensureUserIdInStorage();
      console.log('🔐 Guest login successful, user ID:', userId);
      
      // Navigate to dashboard
      navigate("/dashboard");
    } catch (err) {
      console.error("Guest login error", err);
      alert("Guest login failed. Please try again.");
    } finally {
      setIsGuestLoading(false);
    }
  };

  const username = accounts && accounts[0] ? accounts[0].username : null;

  return (
    <div className="page-container">
      <div className="row justify-content-center">
        <div className="col-lg-6 col-xl-5">
          <div className="text-center mb-5">
            <div className="mb-4">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="currentColor" style={{color: 'var(--accent-primary)'}}>
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
            </div>
            <h1 className="page-title mb-2">Welcome to Resume Screener</h1>
            <p className="page-subtitle">
              AI-powered resume screening and ranking platform
            </p>
          </div>

          <div className="custom-card text-center">
            {username ? (
              <>
                <div className="mb-4">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{color: 'var(--accent-success)'}}>
                    <path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M11,16.5L18,9.5L16.59,8.09L11,13.67L7.41,10.09L6,11.5L11,16.5Z" />
                  </svg>
                  <h4 className="mb-3" style={{color: 'var(--text-primary)'}}>
                    Successfully Signed In!
                  </h4>
                  <div className="p-3 rounded mb-4" style={{
                    backgroundColor: 'rgba(35, 134, 54, 0.1)',
                    border: '1px solid var(--accent-success)',
                    color: 'var(--text-primary)'
                  }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-success)'}}>
                      <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
                    </svg>
                    <strong>Signed in as:</strong> {username}
                  </div>
                </div>
                <button 
                  className="btn btn-custom-primary btn-lg w-100"
                  onClick={() => navigate("/dashboard")}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                    <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
                  </svg>
                  Go to Dashboard
                </button>
              </>
            ) : (
              <>
                <div className="mb-4">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{color: 'var(--accent-primary)'}}>
                    <path d="M12,15C12.81,15 13.5,14.7 14.11,14.11C14.7,13.5 15,12.81 15,12C15,11.19 14.7,10.5 14.11,9.89C13.5,9.3 12.81,9 12,9C11.19,9 10.5,9.3 9.89,9.89C9.3,10.5 9,11.19 9,12C9,12.81 9.3,13.5 9.89,14.11C10.5,14.7 11.19,15 12,15M12,2C14.75,2 17.1,3 18.8,4.6C20.6,6.2 21.5,8.75 21.5,12V13.5C21.5,14.25 21.25,14.9 20.75,15.4C20.25,15.9 19.6,16.15 18.85,16.15C18.5,16.15 18.2,16.05 17.85,15.85C17.5,15.65 17.25,15.4 17.1,15.1C16.45,15.9 15.55,16.3 14.4,16.3C13.4,16.3 12.5,15.95 11.75,15.25C11,14.55 10.65,13.65 10.65,12.55C10.65,11.4 11,10.5 11.75,9.75C12.5,9 13.4,8.65 14.4,8.65C15.55,8.65 16.45,9.05 17.1,9.85V9.85C17.3,8.95 17.75,8.2 18.4,7.65C19.05,7.1 19.85,6.8 20.75,6.8C21.45,6.8 22.05,7.05 22.55,7.55C23.05,8.05 23.3,8.65 23.3,9.35V12C23.3,17.05 21.9,21.05 19.1,23.85C16.3,26.65 12.3,28.05 7.25,28.05H5.75V26.55H7.25C11.7,26.55 15.2,25.35 17.7,22.95C20.2,20.55 21.45,17.05 21.45,12.55V9.35C21.45,9.05 21.35,8.8 21.15,8.6C20.95,8.4 20.7,8.3 20.4,8.3C19.9,8.3 19.45,8.5 19.05,8.9C18.65,9.3 18.45,9.75 18.45,10.25V13.5C18.45,13.85 18.35,14.15 18.15,14.35C17.95,14.55 17.65,14.65 17.3,14.65C16.95,14.65 16.65,14.55 16.45,14.35C16.25,14.15 16.15,13.85 16.15,13.5V12C16.15,11.2 15.85,10.5 15.25,9.9C14.65,9.3 13.95,9 13.15,9C12.35,9 11.65,9.3 11.05,9.9C10.45,10.5 10.15,11.2 10.15,12C10.15,12.8 10.45,13.5 11.05,14.1C11.65,14.7 12.35,15 13.15,15C13.95,15 14.65,14.7 15.25,14.1V12H13.15V10.5H16.65V12C16.65,13.25 16.15,14.35 15.15,15.35C14.15,16.35 13.05,16.85 11.85,16.85C10.4,16.85 9.2,16.25 8.25,15.05C7.3,13.85 6.8,12.45 6.8,10.85V9.35C6.8,8.65 7.05,8.05 7.55,7.55C8.05,7.05 8.65,6.8 9.35,6.8C10.25,6.8 11.05,7.1 11.7,7.65C12.35,8.2 12.8,8.95 13,9.85V9.85C13.65,9.05 14.55,8.65 15.7,8.65C16.7,8.65 17.6,9 18.35,9.7C19.1,10.4 19.45,11.3 19.45,12.4C19.45,13.55 19.1,14.45 18.35,15.15C17.6,15.85 16.7,16.2 15.7,16.2C14.55,16.2 13.65,15.8 13,15V15C12.8,15.95 12.35,16.7 11.7,17.25C11.05,17.8 10.25,18.1 9.35,18.1C8.65,18.1 8.05,17.85 7.55,17.35C7.05,16.85 6.8,16.25 6.8,15.55V12C6.8,8.75 7.7,6.2 9.5,4.6C11.3,3 13.65,2 16.4,2H12Z" />
                  </svg>
                  <h4 className="mb-3" style={{color: 'var(--text-primary)'}}>
                    Sign in with Microsoft
                  </h4>
                  <p className="mb-4" style={{color: 'var(--text-secondary)'}}>
                    Use your Microsoft account to access the Resume Screener platform
                  </p>
                </div>
                
                <button 
                  className="btn btn-custom-primary btn-lg w-100 mb-3"
                  onClick={handleLogin}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                    <path d="M2,3H8V9H2V3M9,3H15V9H9V3M16,3H22V9H16V3M2,10H8V16H2V10M9,10H15V16H9V10M16,10H22V16H16V10M2,17H8V23H2V17M9,17H15V23H9V17M16,17H22V23H16V17Z" />
                  </svg>
                  Sign in with Microsoft
                </button>
                
                <div className="text-center my-3">
                  <span className="px-3" style={{color: 'var(--text-secondary)', backgroundColor: 'var(--bg-primary)'}}>
                    OR
                  </span>
                  <hr style={{marginTop: '-12px', borderColor: 'var(--border-primary)'}} />
                </div>
                
                <button 
                  className="btn btn-outline-secondary btn-lg w-100 mb-3"
                  onClick={handleGuestLogin}
                  disabled={isGuestLoading}
                  style={{
                    borderColor: 'var(--border-primary)',
                    color: 'var(--text-primary)',
                    backgroundColor: 'transparent'
                  }}
                >
                  {isGuestLoading ? (
                    <>
                      <span className="loading-spinner me-2"></span>
                      Creating Guest Session...
                    </>
                  ) : (
                    <>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                        <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
                      </svg>
                      Continue as Guest (3 min)
                    </>
                  )}
                </button>
                
                <div className="alert alert-info" style={{
                  backgroundColor: 'rgba(88, 166, 255, 0.1)',
                  borderColor: 'var(--accent-primary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--accent-primary)'
                }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                    <path d="M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z" />
                  </svg>
                  <small>
                    <strong>Microsoft Account:</strong> Full access with secure authentication via Azure AD.<br/>
                    <strong>Guest Access:</strong> 3-minute trial access without registration. Limited to your IP address.
                  </small>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      
      <div className="row mt-5">
        <div className="col-12">
          <div className="text-center">
            <h3 className="mb-4" style={{color: 'var(--text-secondary)'}}>
              Platform Features
            </h3>
            <div className="row justify-content-center">
              {[
                {
                  icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z',
                  title: 'Upload Resumes',
                  desc: 'Support for PDF, DOC, and ZIP files'
                },
                {
                  icon: 'M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z',
                  title: 'AI Screening',
                  desc: 'Advanced AI-powered resume analysis'
                },
                {
                  icon: 'M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z',
                  title: 'Analytics',
                  desc: 'Detailed insights and reporting'
                }
              ].map((feature, idx) => (
                <div key={idx} className="col-md-4 mb-4">
                  <div className="p-3 rounded" style={{
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-primary)'
                  }}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{color: 'var(--accent-primary)'}}>
                      <path d={feature.icon} />
                    </svg>
                    <h6 style={{color: 'var(--text-primary)'}}>{feature.title}</h6>
                    <p className="small mb-0" style={{color: 'var(--text-secondary)'}}>
                      {feature.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
