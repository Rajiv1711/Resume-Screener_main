"""
Mock Blob Storage Service for Testing
This replaces the Azure Blob Storage dependency for testing purposes.
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

class MockBlobStorage:
    """Mock implementation of blob storage that uses local filesystem."""
    
    def __init__(self, base_path: str = None):
        """Initialize mock blob storage with a base directory."""
        if base_path is None:
            base_path = os.path.join(tempfile.gettempdir(), "mock_blob_storage")
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        print(f"Mock Blob Storage initialized at: {self.base_path}")
    
    def upload_file(self, content: bytes, blob_name: str) -> Dict[str, Any]:
        """Mock upload file - saves to local filesystem."""
        try:
            file_path = self.base_path / blob_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            file_path.write_bytes(content)
            
            return {
                "status": "success",
                "blob_name": blob_name,
                "size": len(content),
                "path": str(file_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def download_file(self, blob_name: str) -> bytes:
        """Mock download file - reads from local filesystem."""
        file_path = self.base_path / blob_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"Blob not found: {blob_name}")
        
        return file_path.read_bytes()
    
    def delete_file(self, blob_name: str) -> Dict[str, Any]:
        """Mock delete file."""
        file_path = self.base_path / blob_name
        
        try:
            if file_path.exists():
                file_path.unlink()
                return {"status": "success", "blob_name": blob_name}
            else:
                return {"status": "error", "error": "File not found"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def list_files(self, prefix: str = "") -> list:
        """Mock list files."""
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path
            
            if search_path.exists():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.base_path)
                        files.append(str(relative_path).replace("\\", "/"))
            
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def exists(self, blob_name: str) -> bool:
        """Check if blob exists."""
        file_path = self.base_path / blob_name
        return file_path.exists()

# Global instance for testing
blob_storage = MockBlobStorage()