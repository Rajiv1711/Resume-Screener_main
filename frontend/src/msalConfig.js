// frontend/src/msalConfig.js
export const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_AZURE_CLIENT_ID || "<FRONTEND_CLIENT_ID>",
    authority:
      `https://login.microsoftonline.com/${process.env.REACT_APP_AZURE_TENANT_ID || "<TENANT_ID>"}`,
    redirectUri: process.env.REACT_APP_REDIRECT_URI || (window.location.origin + "/"),
    postLogoutRedirectUri: process.env.REACT_APP_POST_LOGOUT_REDIRECT_URI || (window.location.origin + "/"),
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  }
};

// scopes used when requesting an access token for the backend API
export const loginRequest = {
  scopes: [process.env.REACT_APP_AZURE_API_SCOPE || "api://<BACKEND_CLIENT_ID>/access_as_user"]
};
