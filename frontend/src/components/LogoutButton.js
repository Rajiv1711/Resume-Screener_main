import React, { useEffect, useState } from "react";
import { useMsal } from "@azure/msal-react";
import { useNavigate } from "react-router-dom";
import {
  logout,
  guestLogout,
  clearGuestToken,
  isAuthenticated,
  loginPopup,
  guestLogin,
  setGuestToken,
} from "../services/api";
import { ensureUserIdInStorage } from "../utils/user";

const LoginLogoutButton = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // Check authentication state
  useEffect(() => {
    const checkAuth = () => {
      const status = isAuthenticated();
      setAuthStatus(status);
    };

    checkAuth();
    const interval = setInterval(checkAuth, 2000);
    return () => clearInterval(interval);
  }, []);

  // ------------------ LOGOUT HANDLER ------------------
  const handleLogout = async () => {
    try {
      const auth = isAuthenticated();
      if (auth && auth.type === "guest") {
        try {
          await guestLogout();
        } catch (err) {
          console.warn("Guest logout API call failed:", err);
        }
        clearGuestToken();
      } else {
        await logout();
      }
      localStorage.removeItem("access_token");
      navigate("/login");
    } catch (err) {
      console.error("Logout error", err);
      localStorage.removeItem("access_token");
      clearGuestToken();
    } finally {
      setAuthStatus(null);
    }
  };

  // ------------------ LOGIN HANDLER ------------------
  const handleLogin = async (type = "azure") => {
    setLoading(true);
    try {
      if (type === "guest") {
        const response = await guestLogin();
        const { access_token, expires_at } = response.data;
        setGuestToken(access_token, expires_at);
      } else {
        await loginPopup();
      }

      // Ensure user_id is set for both guest and Azure logins
      ensureUserIdInStorage();
      navigate("/dashboard");
    } catch (err) {
      console.error("Login error:", err);
      alert("Login failed. Please try again.");
    } finally {
      setLoading(false);
      setAuthStatus(isAuthenticated());
    }
  };

  // ------------------ UI RENDER ------------------
  const isLoggedIn = !!authStatus;

  return (
    <div className="d-flex gap-2 align-items-center">
      {isLoggedIn ? (
        <button
          className="btn btn-outline-light btn-sm"
          onClick={handleLogout}
          style={{
            borderColor: "var(--border-primary)",
            color: "var(--text-secondary)",
            backgroundColor: "transparent",
            transition: "all 0.3s ease",
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "rgba(218, 54, 51, 0.1)";
            e.target.style.borderColor = "var(--accent-danger)";
            e.target.style.color = "var(--accent-danger)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "transparent";
            e.target.style.borderColor = "var(--border-primary)";
            e.target.style.color = "var(--text-secondary)";
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="me-1"
          >
            <path d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z" />
          </svg>
          Logout
        </button>
      ) : (
        <>
          <button
            className="btn btn-custom-primary btn-sm"
            onClick={() => handleLogin("azure")}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner me-2"></span> Signing in...
              </>
            ) : (
              <>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="me-1"
                >
                  <path d="M2,3H8V9H2V3M9,3H15V9H9V3M16,3H22V9H16V3M2,10H8V16H2V10M9,10H15V16H9V10M16,10H22V16H16V10M2,17H8V23H2V17M9,17H15V23H9V17M16,17H22V23H16V17Z" />
                </svg>
                Login
              </>
            )}
          </button>

          <button
            className="btn btn-outline-light btn-sm"
            onClick={() => handleLogin("guest")}
            disabled={loading}
            style={{
              borderColor: "var(--border-primary)",
              color: "var(--text-secondary)",
              backgroundColor: "transparent",
            }}
          >
            {loading ? (
              <>
                <span className="loading-spinner me-2"></span> Loading...
              </>
            ) : (
              <>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="me-1"
                >
                  <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
                </svg>
                Guest Login
              </>
            )}
          </button>
        </>
      )}
    </div>
  );
};

export default LoginLogoutButton;
