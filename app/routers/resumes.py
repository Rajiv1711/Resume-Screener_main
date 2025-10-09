from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from fastapi import Depends
from app.routers.azure_auth import get_current_user_azure
from app.services.blob_storage import blob_storage
from app.services.parser import parse_resume, parse_zip

router = APIRouter(prefix="/api", tags=["resumes"])

UPLOAD_DIR = "data/raw_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), _current_user= Depends(get_current_user_azure)):
    """Upload and parse a resume or a ZIP of resumes."""
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Azure Blob Storage
        blob_name = f"raw_resumes/{file.filename}"
        blob_url = blob_storage.upload_file(file_content, blob_name)
        
        # Create a temporary file for parsing (since parser expects file paths)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            if file_ext == ".zip":
                results = parse_zip(temp_path)
                return JSONResponse(content={
                    "status": "success", 
                    "files": results,
                    "blob_url": blob_url,
                    "blob_name": blob_name
                })

            elif file_ext in [".pdf", ".docx", ".txt"]:
                result = parse_resume(temp_path)
                return JSONResponse(content={
                    "status": "success", 
                    "file": file.filename, 
                    "parsed": result,
                    "blob_url": blob_url,
                    "blob_name": blob_name
                })

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
