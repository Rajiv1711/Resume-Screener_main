from fastapi import APIRouter, HTTPException, Body, Request, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.ranker import rank_resumes
from app.services.parser import parse_resume, parse_zip, parse_resume_from_blob, parse_zip_from_blob
from app.services.enhanced_text_extractor import enhanced_extractor
from app.services.blob_storage import blob_storage
import os
import json
import tempfile
# from app.routers.auth import get_current_user
# from app.routers.azure_auth import get_current_user_azure

router = APIRouter(prefix="/api", tags=["ranking"])

DATA_PATH = "data/raw_resumes"


@router.post("/rank")
async def rank_uploaded_resumes(
    job_description: str = Body(..., embed=True, description="Job description text"),
    request: Request = None
):
    """
    Rank uploaded resumes against a given job description.
    Parses all resumes from Azure Blob Storage, generates embeddings, and returns ranked output.
    """
    try:
        resumes = []

        # Step 1: Collect all uploaded resumes from per-user blob storage
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header

        blob_names = blob_storage.list_blobs_session(user_id=user_id, prefix="raw_resumes/")
        
        for blob_name in blob_names:
            if blob_name.startswith("raw_resumes/"):
                ext = os.path.splitext(blob_name)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    try:
                        parsed = parse_resume_from_blob(blob_name, user_id=user_id)
                        resumes.append(parsed)
                    except Exception as e:
                        resumes.append({"file": os.path.basename(blob_name), "error": str(e)})
                elif ext == ".zip":
                    try:
                        parsed_zip = parse_zip_from_blob(blob_name, user_id=user_id)
                        resumes.extend(parsed_zip)
                    except Exception as e:
                        resumes.append({"file": os.path.basename(blob_name), "error": str(e)})

        if not resumes:
            raise HTTPException(status_code=404, detail="No resumes found in blob storage")

        # Step 2: Rank resumes based on job description
        ranked_results = rank_resumes(resumes, job_description)

        # Step 3: Save ranked output for reporting to session-based blob storage
        json_content = json.dumps(ranked_results, indent=4).encode('utf-8')
        blob_storage.upload_file_session(json_content, "reports/ranked_resumes.json", user_id)
        
        # Also save locally for backward compatibility
        os.makedirs("reports", exist_ok=True)
        with open("reports/ranked_resumes.json", "w", encoding="utf-8") as f:
            json.dump(ranked_results, f, indent=4)

        return JSONResponse(content={"status": "success", "ranked_resumes": ranked_results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rank-from-file")
async def rank_uploaded_resumes_from_file(
    jd_file: UploadFile = File(..., description="Job description file: PDF, DOCX, or TXT"),
    request: Request = None
):
    """
    Rank uploaded resumes using a job description provided as a document upload.
    Accepts PDF, DOCX, or TXT. Extracts text and runs the same ranking pipeline.
    """
    try:
        # Identify user
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header

        # Read file bytes and extract text
        file_bytes = await jd_file.read()
        ext = os.path.splitext(jd_file.filename)[1].lower()
        if ext not in [".pdf", ".docx", ".txt", ".doc"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, DOCX, or TXT.")
        # Handle legacy .doc as .docx not supported; user should convert, but attempt txt fallback
        if ext == ".doc":
            # Best-effort: write and treat as binary text (may be messy)
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf:
                tf.write(file_bytes)
                temp_path = tf.name
            try:
                extracted = enhanced_extractor.extract_text(temp_path)
                job_description_text = extracted.get("raw_text", "")
            finally:
                os.unlink(temp_path)
        else:
            extracted = enhanced_extractor.extract_text_from_bytes(file_bytes, ext)
            job_description_text = extracted.get("raw_text", "")

        if not job_description_text or len(job_description_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Failed to extract meaningful text from the uploaded file.")

        # Collect resumes from user's current session in blob storage
        blob_names = blob_storage.list_blobs_session(user_id=user_id, prefix="raw_resumes/")
        resumes = []
        for blob_name in blob_names:
            if blob_name.startswith("raw_resumes/"):
                ext_r = os.path.splitext(blob_name)[1].lower()
                if ext_r in [".pdf", ".docx", ".txt"]:
                    try:
                        parsed = parse_resume_from_blob(blob_name, user_id=user_id)
                        resumes.append(parsed)
                    except Exception as e:
                        resumes.append({"file": os.path.basename(blob_name), "error": str(e)})
                elif ext_r == ".zip":
                    try:
                        parsed_zip = parse_zip_from_blob(blob_name, user_id=user_id)
                        resumes.extend(parsed_zip)
                    except Exception as e:
                        resumes.append({"file": os.path.basename(blob_name), "error": str(e)})

        if not resumes:
            raise HTTPException(status_code=404, detail="No resumes found in blob storage")

        # Rank resumes using extracted text
        ranked_results = rank_resumes(resumes, job_description_text)

        # Save ranked output to session-based blob storage and locally
        json_content = json.dumps(ranked_results, indent=4).encode('utf-8')
        blob_storage.upload_file_session(json_content, "reports/ranked_resumes.json", user_id)
        os.makedirs("reports", exist_ok=True)
        with open("reports/ranked_resumes.json", "w", encoding="utf-8") as f:
            json.dump(ranked_results, f, indent=4)

        return JSONResponse(content={"status": "success", "ranked_resumes": ranked_results})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
