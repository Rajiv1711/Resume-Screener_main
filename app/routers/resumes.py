from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from fastapi.responses import JSONResponse
import os
import shutil
# from fastapi import Depends
# from app.routers.azure_auth import get_current_user_azure
from app.services.blob_storage import blob_storage
from fastapi import Request
from app.services.parser import parse_resume, parse_zip

router = APIRouter(prefix="/api", tags=["resumes"])

UPLOAD_DIR = "data/raw_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_resume(resume: List[UploadFile] = File(...), request: Request = None):
    """Upload and parse one or more resumes or ZIPs of resumes.

    The frontend should send multiple files under the same field name "resume".
    """
    try:
        import tempfile

        results = []

        user_id = "guest"
        if request is not None:
            # Try to extract user identity hints
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header

        for uploaded_file in resume:
            file_ext = os.path.splitext(uploaded_file.filename)[1].lower()

            # Read file content
            file_content = await uploaded_file.read()

            # Upload to Azure Blob Storage
            blob_name = f"raw_resumes/{uploaded_file.filename}"
            blob_url = blob_storage.upload_file_user(file_content, blob_name, user_id)

            # Create a temporary file for parsing (since parser expects file paths)
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name

            try:
                if file_ext == ".zip":
                    parsed_list = parse_zip(temp_path)
                    results.append({
                        "status": "success",
                        "file": uploaded_file.filename,
                        "parsed": parsed_list,
                        "blob_url": blob_url,
                        "blob_name": blob_name,
                        "type": "zip"
                    })
                elif file_ext in [".pdf", ".docx", ".txt"]:
                    parsed = parse_resume(temp_path)
                    results.append({
                        "status": "success",
                        "file": uploaded_file.filename,
                        "parsed": parsed,
                        "blob_url": blob_url,
                        "blob_name": blob_name,
                        "type": "file"
                    })
                else:
                    results.append({
                        "status": "error",
                        "file": uploaded_file.filename,
                        "error": f"Unsupported file format: {file_ext}"
                    })
            finally:
                # Clean up temporary file
                os.unlink(temp_path)

        return JSONResponse(content={"status": "success", "results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
