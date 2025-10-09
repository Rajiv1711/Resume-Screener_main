import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import "./App.css";
import { useIsAuthenticated } from "@azure/msal-react";
import Navbar from "./components/Navbar";

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useIsAuthenticated();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <div className="App">
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/upload" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
