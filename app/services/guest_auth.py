# app/services/guest_auth.py
import time
import secrets
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class GuestSessionManager:
    """
    Manages guest sessions with IP-based tracking and 3-minute expiration.
    """
    
    def __init__(self):
        # Store format: {ip_hash: {"token": str, "expires_at": float, "created_at": float}}
        self._sessions: Dict[str, Dict] = {}
        self.session_duration = 3 * 60  # 3 minutes in seconds
    
    def _hash_ip(self, ip_address: str) -> str:
        """Hash IP address for privacy and storage."""
        return hashlib.sha256(ip_address.encode()).hexdigest()
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions from memory."""
        current_time = time.time()
        expired_ips = [
            ip_hash for ip_hash, session in self._sessions.items()
            if session["expires_at"] < current_time
        ]
        for ip_hash in expired_ips:
            del self._sessions[ip_hash]
    
    def create_guest_session(self, ip_address: str) -> Tuple[str, datetime]:
        """
        Create a new guest session for the given IP address.
        Returns (token, expires_at_datetime).
        """
        self._cleanup_expired_sessions()
        
        ip_hash = self._hash_ip(ip_address)
        current_time = time.time()
        expires_at = current_time + self.session_duration
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Store session
        self._sessions[ip_hash] = {
            "token": token,
            "expires_at": expires_at,
            "created_at": current_time,
            "ip_address": ip_address  # Store for logging purposes
        }
        
        expires_at_dt = datetime.fromtimestamp(expires_at)
        return token, expires_at_dt
    
    def validate_guest_token(self, token: str, ip_address: str) -> Optional[Dict]:
        """
        Validate a guest token for the given IP address.
        Returns session info if valid, None if invalid/expired.
        """
        self._cleanup_expired_sessions()
        
        ip_hash = self._hash_ip(ip_address)
        session = self._sessions.get(ip_hash)
        
        if not session:
            return None
        
        if session["token"] != token:
            return None
        
        current_time = time.time()
        if session["expires_at"] < current_time:
            # Session expired, remove it
            del self._sessions[ip_hash]
            return None
        
        return {
            "ip_address": ip_address,
            "created_at": datetime.fromtimestamp(session["created_at"]),
            "expires_at": datetime.fromtimestamp(session["expires_at"]),
            "remaining_seconds": int(session["expires_at"] - current_time)
        }
    
    def revoke_guest_session(self, ip_address: str):
        """Revoke/delete a guest session for the given IP address."""
        ip_hash = self._hash_ip(ip_address)
        if ip_hash in self._sessions:
            del self._sessions[ip_hash]
    
    def get_session_stats(self) -> Dict:
        """Get statistics about current guest sessions."""
        self._cleanup_expired_sessions()
        current_time = time.time()
        
        active_sessions = len(self._sessions)
        total_remaining_time = sum(
            max(0, session["expires_at"] - current_time)
            for session in self._sessions.values()
        )
        
        return {
            "active_sessions": active_sessions,
            "total_remaining_minutes": total_remaining_time / 60,
            "session_duration_minutes": self.session_duration / 60
        }

# Global instance
guest_session_manager = GuestSessionManager()