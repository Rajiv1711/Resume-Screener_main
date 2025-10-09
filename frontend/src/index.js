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
import { msalInstance } from "./auth/msal";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <MsalProvider instance={msalInstance}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </MsalProvider>
);
