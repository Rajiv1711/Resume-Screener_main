import React, { useCallback, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import Dashboard from "./pages/Dashboard";
import SessionsPage from "./pages/SessionsPage";
import Login from "./pages/Login";
import Home from "./pages/Home";
import "./App.css";
import { useIsAuthenticated } from "@azure/msal-react";
import { isAuthenticated } from "./services/api";
import Navbar from "./components/Navbar";
import ToastContainer from "./components/Toast";

const ProtectedRoute = ({ children }) => {
  const azureAuthenticated = useIsAuthenticated();
  const authStatus = isAuthenticated();
  
  // Check both Azure AD and guest authentication
  if (!azureAuthenticated && !authStatus) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  const [toasts, setToasts] = useState([]);
  const pushToast = useCallback((t) => setToasts((prev) => [...prev, { id: Date.now(), ...t }]), []);
  const closeToast = useCallback((id) => setToasts((prev) => prev.filter((x) => x.id !== id)), []);

  return (
    <div className="App">
      <Navbar />
      <ToastContainer toasts={toasts} onClose={closeToast} />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home pushToast={pushToast} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/upload" element={<UploadPage pushToast={pushToast} />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard pushToast={pushToast} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sessions"
            element={
              <ProtectedRoute>
                <SessionsPage pushToast={pushToast} />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
