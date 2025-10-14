// frontend/src/services/api.js
import axios from "axios";
import { msalInstance } from "../auth/msal";
import { loginRequest } from "../msalConfig";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api",
});

// Interceptor to attach Authorization header using msal or guest token
API.interceptors.request.use(
  async (config) => {
    // Identify user for per-user blob containers (hoisted for catch access)
    let userIdHeader = null;
    try {

      // First try guest authentication
      const guestToken = localStorage.getItem('guest_token');
      const guestExpiry = localStorage.getItem('guest_token_expiry');
      
      if (guestToken && guestExpiry) {
        const now = new Date();
        const expiry = new Date(guestExpiry);
        if (now < expiry) {
          // Use guest token
          config.headers = config.headers || {};
          config.headers["Authorization"] = `Bearer ${guestToken}`;
          userIdHeader = `guest-${guestToken.slice(-8)}`;
          config.headers['X-User-Id'] = userIdHeader;
          return config;
        } else {
          // Guest token expired, clean up
          localStorage.removeItem('guest_token');
          localStorage.removeItem('guest_token_expiry');
        }
      }
      
      // Try Azure AD authentication
      let accounts = [];
      try {
        accounts = msalInstance.getAllAccounts();
        if (accounts.length === 0) {
          // not logged in with either method
          if (userIdHeader) {
            config.headers = config.headers || {};
            config.headers['X-User-Id'] = userIdHeader;
          }
          return config;
        }
      } catch (error) {
        // MSAL not initialized yet, skip Azure AD auth
        if (userIdHeader) {
          config.headers = config.headers || {};
          config.headers['X-User-Id'] = userIdHeader;
        }
        return config;
      }
      
      const silentRequest = {
        ...loginRequest,
        account: accounts[0],
      };
      const resp = await msalInstance.acquireTokenSilent(silentRequest);
      const accessToken = resp.accessToken;
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${accessToken}`;
      // Prefer username; fallback to homeAccountId
      const acct = accounts[0];
      const azureUserId = acct?.username || acct?.homeAccountId || null;
      if (azureUserId) {
        config.headers['X-User-Id'] = azureUserId;
      } else if (userIdHeader) {
        config.headers['X-User-Id'] = userIdHeader;
      }
    } catch (err) {
      // fallback: try interactive (will open popup/redirect) only for Azure
      try {
        const resp = await msalInstance.acquireTokenPopup(loginRequest);
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${resp.accessToken}`;
        const accounts = msalInstance.getAllAccounts();
        const acct = accounts && accounts[0];
        const azureUserId = acct?.username || acct?.homeAccountId || null;
        if (azureUserId) {
          config.headers['X-User-Id'] = azureUserId;
        }
      } catch (e) {
        console.warn("Could not acquire token silently or via popup", e);
        // still send any derived guest header
        if (userIdHeader) {
          config.headers = config.headers || {};
          config.headers['X-User-Id'] = userIdHeader;
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ------------------ Named API helper exports ------------------

// Upload resume (single file or zip). Expects FormData with "resume" field.
export const uploadResume = (formData) =>
  API.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// Get insights (skill frequencies, etc.)
export const getInsights = () => API.get("/insights");

// Rank resumes (job_description string)
export const rankResumes = (jobDescription) =>
  API.post("/rank", { job_description: jobDescription });

// Download report securely with auth header
export const downloadReport = async (type) => {
  const res = await API.get(`/download/${type}`, { responseType: "blob" });
  const blob = new Blob([res.data], {
    type: res.headers["content-type"] || "application/octet-stream",
  });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  // Map logical type to proper file extension
  const ext = type === 'excel' ? 'xlsx' : (type === 'csv' ? 'csv' : (type === 'pdf' ? 'pdf' : type));
  a.download = `ranked_resumes.${ext}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

// ------------------ Guest Authentication ------------------

// Guest login - creates a 3-minute session based on IP
export const guestLogin = () => API.post("/auth/guest-login");

// Get guest session status
export const getGuestStatus = () => API.get("/auth/guest-status");

// Guest logout
export const guestLogout = () => API.post("/auth/guest-logout");

// Check if user is authenticated (either Azure or Guest)
export const isAuthenticated = () => {
  // Check for guest token
  const guestToken = localStorage.getItem('guest_token');
  const guestExpiry = localStorage.getItem('guest_token_expiry');
  
  if (guestToken && guestExpiry) {
    const now = new Date();
    const expiry = new Date(guestExpiry);
    if (now < expiry) {
      return { type: 'guest', token: guestToken, expiry };
    } else {
      // Guest token expired, clean up
      localStorage.removeItem('guest_token');
      localStorage.removeItem('guest_token_expiry');
    }
  }
  
  // Check for Azure AD authentication
  try {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      return { type: 'azure', account: accounts[0] };
    }
  } catch (error) {
    // MSAL not initialized yet, ignore Azure AD auth
  }
  
  return null;
};

// Store guest token
export const setGuestToken = (token, expiresAt) => {
  localStorage.setItem('guest_token', token);
  localStorage.setItem('guest_token_expiry', expiresAt);
};

// Clear guest token
export const clearGuestToken = () => {
  localStorage.removeItem('guest_token');
  localStorage.removeItem('guest_token_expiry');
};

// ------------------ MSAL helper exports ------------------

export const loginRedirect = () => msalInstance.loginRedirect(loginRequest);
export const loginPopup = () => msalInstance.loginPopup(loginRequest);
export const logout = () => {
  // Clear both Azure and guest tokens
  clearGuestToken();
  msalInstance.logoutRedirect();
};
export const getActiveAccount = () => {
  try {
    return msalInstance.getAllAccounts()[0] || null;
  } catch (error) {
    // MSAL not initialized yet
    return null;
  }
};

// default export for direct axios usage if needed
export default API;
