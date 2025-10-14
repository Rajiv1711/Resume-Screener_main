from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from app.services.ranker import rank_resumes
from app.services.parser import parse_resume, parse_zip, parse_resume_from_blob, parse_zip_from_blob
from app.services.blob_storage import blob_storage
import os
import json
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

        blob_names = blob_storage.list_blobs_user(prefix="raw_resumes/", user_id=user_id)
        
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

        # Step 3: Save ranked output for reporting (both locally and to blob storage)
        os.makedirs("reports", exist_ok=True)
        with open("reports/ranked_resumes.json", "w", encoding="utf-8") as f:
            json.dump(ranked_results, f, indent=4)
        
        # Also save to per-user blob storage
        json_content = json.dumps(ranked_results, indent=4).encode('utf-8')
        blob_storage.upload_file_user(json_content, "reports/ranked_resumes.json", user_id)

        return JSONResponse(content={"status": "success", "ranked_resumes": ranked_results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
