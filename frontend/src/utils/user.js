// frontend/src/utils/user.js
import { msalInstance } from '../auth/msal';

/**
 * Get the current user ID for API requests
 * This function consolidates the user identification logic used across the app
 */
export const getCurrentUserId = () => {
  // First try guest authentication
  const guestToken = localStorage.getItem('guest_token');
  const guestExpiry = localStorage.getItem('guest_token_expiry');
  
  if (guestToken && guestExpiry) {
    const now = new Date();
    const expiry = new Date(guestExpiry);
    if (now < expiry) {
      // Use guest token - create consistent user ID from token
      return `guest-${guestToken.slice(-8)}`;
    } else {
      // Guest token expired, clean up
      localStorage.removeItem('guest_token');
      localStorage.removeItem('guest_token_expiry');
    }
  }
  
  // Try Azure AD authentication
  try {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      const account = accounts[0];
      return account.username || account.homeAccountId || 'azure-user';
    }
  } catch (error) {
    console.warn('MSAL not initialized, using fallback user ID');
  }
  
  // Fallback to guest
  return 'guest';
};

/**
 * Get the API base URL
 */
export const getApiBaseUrl = () => {
  return process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api';
};

/**
 * Create headers with user authentication
 */
export const createAuthHeaders = (additionalHeaders = {}) => {
  const userId = getCurrentUserId();
  console.log('🔑 Creating auth headers for user:', userId);
  
  return {
    'X-User-Id': userId,
    ...additionalHeaders
  };
};

/**
 * Initialize or ensure user_id is set in localStorage
 * This is mainly for backward compatibility with existing code
 */
export const ensureUserIdInStorage = () => {
  const currentUserId = getCurrentUserId();
  const storedUserId = localStorage.getItem('user_id');
  
  if (!storedUserId || storedUserId !== currentUserId) {
    console.log('💾 Setting user_id in localStorage:', currentUserId);
    localStorage.setItem('user_id', currentUserId);
  }
  
  return currentUserId;
};