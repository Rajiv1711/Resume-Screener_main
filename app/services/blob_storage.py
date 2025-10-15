import os
import io
from datetime import datetime
from typing import Optional, List, Dict
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from app.config import BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME


class BlobStorageService:
    """Service for managing resume files in Azure Blob Storage with session-based organization."""
    
    def __init__(self):
        self.connection_string = BLOB_CONNECTION_STRING
        self.container_name = BLOB_CONTAINER_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._ensure_container_exists()
        # Store current session per user
        self._user_sessions: Dict[str, str] = {}
        # Store session metadata (name, description, etc.)
        self._session_metadata: Dict[str, Dict] = {}
    
    def _ensure_container_exists(self):
        """Create the container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
        except Exception:
            # Container already exists or other error
            pass

    def _sanitize_user_id(self, user_id: str) -> str:
        """Sanitize user id for use in blob paths (preserve @ and .)."""
        if not user_id:
            return "guest"
        # Keep alphanumeric, @, ., -, _
        sanitized = "".join(ch if ch.isalnum() or ch in '@.-_' else '_' for ch in user_id)
        return sanitized or "guest"
    
    def _sanitize_container_suffix(self, user_id: str) -> str:
        """Sanitize user id to be used as a container suffix (lowercase, alnum and dash)."""
        if not user_id:
            return "public"
        sanitized = "".join(ch if ch.isalnum() or ch == '-' else '-' for ch in user_id.lower())
        return sanitized.strip('-') or "public"
    
    def create_session(self, user_id: str, session_name: Optional[str] = None) -> str:
        """Create a new session for a user with timestamp.
        
        Args:
            user_id: User identifier (email or username)
            session_name: Optional custom name for the session
            
        Returns:
            Session ID (timestamp-based)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        self._user_sessions[user_id] = session_id
        
        # Store session metadata
        metadata_key = f"{user_id}:{session_id}"
        self._session_metadata[metadata_key] = {
            'name': session_name or f"Session {timestamp}",
            'created': datetime.now().isoformat(),
            'user_id': user_id,
            'session_id': session_id
        }
        
        # Save metadata to blob storage
        self._save_session_metadata(user_id, session_id)
        
        return session_id
    
    def get_current_session(self, user_id: str) -> str:
        """Get the current session ID for a user, creating one if needed.
        
        Args:
            user_id: User identifier
            
        Returns:
            Current session ID
        """
        if user_id not in self._user_sessions:
            return self.create_session(user_id)
        return self._user_sessions[user_id]
    
    def get_session_path(self, user_id: str, session_id: Optional[str] = None) -> str:
        """Get the blob path prefix for a user's session.
        
        Args:
            user_id: User identifier
            session_id: Optional specific session ID, uses current if None
            
        Returns:
            Blob path prefix (e.g., 'user@email.com/session_20250115_103045/')
        """
        sanitized_user = self._sanitize_user_id(user_id)
        if session_id is None:
            session_id = self.get_current_session(user_id)
        return f"{sanitized_user}/{session_id}/"

    def _get_or_create_user_container(self, user_id: str):
        """Return a container client for the user's container, creating if needed."""
        suffix = self._sanitize_container_suffix(user_id)
        user_container = f"{self.container_name}-{suffix}"
        container_client = self.blob_service_client.get_container_client(user_container)
        try:
            container_client.create_container()
        except Exception:
            pass
        return user_container
    
    def upload_file(self, file_content: bytes, blob_name: str) -> str:
        """
        Upload a file to blob storage.
        
        Args:
            file_content: The file content as bytes
            blob_name: The name/path for the blob
            
        Returns:
            The URL of the uploaded blob
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        
        blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url

    def upload_file_user(self, file_content: bytes, blob_name: str, user_id: str) -> str:
        user_container = self._get_or_create_user_container(user_id)
        blob_client = self.blob_service_client.get_blob_client(
            container=user_container,
            blob=blob_name
        )
        blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Download a file from blob storage.
        
        Args:
            blob_name: The name/path of the blob to download
            
        Returns:
            The file content as bytes
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        
        download_stream = blob_client.download_blob()
        return download_stream.readall()

    def download_file_user(self, blob_name: str, user_id: str) -> bytes:
        user_container = self._get_or_create_user_container(user_id)
        blob_client = self.blob_service_client.get_blob_client(
            container=user_container,
            blob=blob_name
        )
        download_stream = blob_client.download_blob()
        return download_stream.readall()
    
    def download_file_to_stream(self, blob_name: str) -> io.BytesIO:
        """
        Download a file from blob storage to a stream.
        
        Args:
            blob_name: The name/path of the blob to download
            
        Returns:
            A BytesIO stream containing the file content
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        
        download_stream = blob_client.download_blob()
        return io.BytesIO(download_stream.readall())
    
    def list_blobs(self, prefix: str = "") -> List[str]:
        """
        List all blobs in the container with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter blob names
            
        Returns:
            List of blob names
        """
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]

    def list_blobs_user(self, prefix: str, user_id: str) -> List[str]:
        user_container = self._get_or_create_user_container(user_id)
        container_client = self.blob_service_client.get_container_client(user_container)
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from storage.
        
        Args:
            blob_name: The name/path of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception:
            return False
    
    def blob_exists(self, blob_name: str) -> bool:
        """
        Check if a blob exists in storage.
        
        Args:
            blob_name: The name/path of the blob to check
            
        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False
    
    def get_blob_url(self, blob_name: str) -> str:
        """
        Get the URL for a blob.
        
        Args:
            blob_name: The name/path of the blob
            
        Returns:
            The URL of the blob
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        return blob_client.url

    def get_blob_url_user(self, blob_name: str, user_id: str) -> str:
        user_container = self._get_or_create_user_container(user_id)
        blob_client = self.blob_service_client.get_blob_client(
            container=user_container,
            blob=blob_name
        )
        return blob_client.url
    
    # ========== Session-Based Methods ==========
    
    def upload_file_session(self, file_content: bytes, blob_name: str, user_id: str, session_id: Optional[str] = None) -> str:
        """Upload a file to a user's session folder.
        
        Args:
            file_content: File content as bytes
            blob_name: Name of the blob (e.g., 'raw_resumes/resume.pdf')
            user_id: User identifier
            session_id: Optional session ID, uses current if None
            
        Returns:
            URL of the uploaded blob
        """
        session_path = self.get_session_path(user_id, session_id)
        full_blob_name = f"{session_path}{blob_name}"
        
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=full_blob_name
        )
        blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url
    
    def download_file_session(self, blob_name: str, user_id: str, session_id: Optional[str] = None) -> bytes:
        """Download a file from a user's session folder.
        
        Args:
            blob_name: Name of the blob relative to session (e.g., 'raw_resumes/resume.pdf')
            user_id: User identifier
            session_id: Optional session ID, uses current if None
            
        Returns:
            File content as bytes
        """
        session_path = self.get_session_path(user_id, session_id)
        full_blob_name = f"{session_path}{blob_name}"
        
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=full_blob_name
        )
        download_stream = blob_client.download_blob()
        return download_stream.readall()
    
    def list_blobs_session(self, user_id: str, session_id: Optional[str] = None, prefix: str = "") -> List[str]:
        """List all blobs in a user's session folder.
        
        Args:
            user_id: User identifier
            session_id: Optional session ID, uses current if None
            prefix: Additional prefix filter within the session (e.g., 'raw_resumes/')
            
        Returns:
            List of blob names (relative to session path)
        """
        session_path = self.get_session_path(user_id, session_id)
        full_prefix = f"{session_path}{prefix}"
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=full_prefix)
        
        # Return names relative to session path
        session_prefix_len = len(session_path)
        return [blob.name[session_prefix_len:] for blob in blobs]
    
    def list_user_sessions(self, user_id: str) -> List[Dict[str, str]]:
        """List all sessions for a user with metadata.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session info dicts with 'session_id', 'name', 'created', 'blob_count'
        """
        sanitized_user = self._sanitize_user_id(user_id)
        user_prefix = f"{sanitized_user}/"
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=user_prefix)
        
        # Extract unique session IDs
        sessions = {}
        for blob in blobs:
            # blob.name format: user@email.com/session_20250115_103045/raw_resumes/file.pdf
            # or: user@email.com/session_20250115_103045/.metadata.json
            parts = blob.name[len(user_prefix):].split('/', 1)
            if parts and parts[0].startswith('session_'):
                session_id = parts[0]
                if session_id not in sessions:
                    # Load metadata
                    metadata = self._load_session_metadata(user_id, session_id)
                    
                    sessions[session_id] = {
                        'session_id': session_id,
                        'name': metadata.get('name', f"Session {session_id.replace('session_', '')}"),
                        'created': metadata.get('created', 'Unknown'),
                        'blob_count': 0
                    }
                
                # Count non-metadata files only
                if not '.metadata.json' in blob.name:
                    sessions[session_id]['blob_count'] += 1
        
        # Sort by creation time (newest first)
        return sorted(sessions.values(), key=lambda x: x['created'], reverse=True)
    
    def _save_session_metadata(self, user_id: str, session_id: str):
        """Save session metadata to blob storage."""
        try:
            metadata_key = f"{user_id}:{session_id}"
            if metadata_key in self._session_metadata:
                import json
                metadata_json = json.dumps(self._session_metadata[metadata_key])
                session_path = self.get_session_path(user_id, session_id)
                
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=f"{session_path}.metadata.json"
                )
                blob_client.upload_blob(metadata_json.encode('utf-8'), overwrite=True)
        except Exception as e:
            print(f"Failed to save session metadata: {e}")
    
    def _load_session_metadata(self, user_id: str, session_id: str) -> Dict:
        """Load session metadata from blob storage."""
        try:
            import json
            session_path = self.get_session_path(user_id, session_id)
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=f"{session_path}.metadata.json"
            )
            download_stream = blob_client.download_blob()
            metadata_json = download_stream.readall().decode('utf-8')
            return json.loads(metadata_json)
        except Exception:
            # Return default metadata if not found
            timestamp_str = session_id.replace('session_', '')
            return {
                'name': f"Session {timestamp_str}",
                'created': 'Unknown',
                'user_id': user_id,
                'session_id': session_id
            }
    
    def update_session_name(self, user_id: str, session_id: str, new_name: str) -> bool:
        """Update the name of a session.
        
        Args:
            user_id: User identifier
            session_id: Session ID to update
            new_name: New name for the session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata_key = f"{user_id}:{session_id}"
            
            # Load existing metadata if not in cache
            if metadata_key not in self._session_metadata:
                self._session_metadata[metadata_key] = self._load_session_metadata(user_id, session_id)
            
            # Update name
            self._session_metadata[metadata_key]['name'] = new_name
            
            # Save to blob storage
            self._save_session_metadata(user_id, session_id)
            return True
        except Exception as e:
            print(f"Failed to update session name: {e}")
            return False
    
    def delete_session(self, user_id: str, session_id: str) -> int:
        """Delete all blobs in a user's session.
        
        Args:
            user_id: User identifier
            session_id: Session ID to delete
            
        Returns:
            Number of blobs deleted
        """
        session_path = self.get_session_path(user_id, session_id)
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=session_path)
        
        count = 0
        for blob in blobs:
            try:
                container_client.delete_blob(blob.name)
                count += 1
            except:
                pass
        
        # Clean up from session cache
        if user_id in self._user_sessions and self._user_sessions[user_id] == session_id:
            del self._user_sessions[user_id]
        
        return count


# Global instance
blob_storage = BlobStorageService()
