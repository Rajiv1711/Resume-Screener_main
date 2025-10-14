import os
import io
from typing import Optional, List
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from app.config import BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME


class BlobStorageService:
    """Service for managing resume files in Azure Blob Storage."""
    
    def __init__(self):
        self.connection_string = BLOB_CONNECTION_STRING
        self.container_name = BLOB_CONTAINER_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create the container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
        except Exception:
            # Container already exists or other error
            pass

    def _sanitize_container_suffix(self, user_id: str) -> str:
        """Sanitize user id to be used as a container suffix (lowercase, alnum and dash)."""
        if not user_id:
            return "public"
        sanitized = "".join(ch if ch.isalnum() or ch == '-' else '-' for ch in user_id.lower())
        return sanitized.strip('-') or "public"

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


# Global instance
blob_storage = BlobStorageService()
