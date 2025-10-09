// frontend/src/services/api.js
import axios from "axios";
import { msalInstance } from "../auth/msal";
import { loginRequest } from "../msalConfig";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api",
});

// Interceptor to attach Authorization header using msal
API.interceptors.request.use(
  async (config) => {
    try {
      const accounts = msalInstance.getAllAccounts();
      if (accounts.length === 0) {
        return config; // not logged in
      }
      const silentRequest = {
        ...loginRequest,
        account: accounts[0],
      };
      const resp = await msalInstance.acquireTokenSilent(silentRequest);
      const accessToken = resp.accessToken;
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${accessToken}`;
    } catch (err) {
      // fallback: try interactive (will open popup/redirect)
      try {
        const resp = await msalInstance.acquireTokenPopup(loginRequest);
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${resp.accessToken}`;
      } catch (e) {
        console.warn("Could not acquire token silently or via popup", e);
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
  a.download = `report.${type}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

// ------------------ MSAL helper exports ------------------

export const loginRedirect = () => msalInstance.loginRedirect(loginRequest);
export const loginPopup = () => msalInstance.loginPopup(loginRequest);
export const logout = () => msalInstance.logoutRedirect();
export const getActiveAccount = () => msalInstance.getAllAccounts()[0] || null;

// default export for direct axios usage if needed
export default API;
