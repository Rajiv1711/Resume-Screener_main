// src/index.js
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { MsalProvider } from "@azure/msal-react";
// Import Bootstrap CSS first
import "bootstrap/dist/css/bootstrap.min.css";
// Then import our custom CSS
import "./index.css";
import App from "./App";
import CustomCursor from "./components/CustomCursor";
import AnimatedBackground from "./components/AnimatedBackground";
import ScrollToTop from "./components/ScrollToTop";
import { msalInstance } from "./auth/msal";

// Initialize MSAL and then render the app
const initializeApp = async () => {
  try {
    // Ensure MSAL is initialized before rendering
    await msalInstance.initialize();
    console.log("MSAL initialized successfully");
  } catch (error) {
    console.error("MSAL initialization failed:", error);
  }
  
  // Render the app regardless of MSAL initialization status
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(
    <React.StrictMode>
      <AnimatedBackground />
      <CustomCursor />
      <MsalProvider instance={msalInstance}>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <App />
          <ScrollToTop />
        </BrowserRouter>
      </MsalProvider>
    </React.StrictMode>
  );
};

// Start the app initialization
initializeApp();
