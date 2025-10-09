from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os

from app.services.report import generate_reports, generate_reports_from_blob
from app.services.blob_storage import blob_storage
from fastapi import Depends
from app.routers.azure_auth import get_current_user_azure

router = APIRouter(prefix="/api", tags=["reports"])

REPORTS_DIR = "reports"


@router.get("/download/{report_type}")
async def download_report(report_type: str , _current_user= Depends(get_current_user_azure)):
    """
    Download ranked resumes report in Excel or PDF format.
    report_type: 'excel' or 'pdf'
    """
    try:
        # Generate reports from blob storage
        reports = generate_reports_from_blob()

        if report_type == "excel":
            file_path = reports["excel_report"]
            filename = os.path.basename(file_path)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        elif report_type == "pdf":
            file_path = reports["pdf_report"]
            filename = os.path.basename(file_path)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/pdf"
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel' or 'pdf'.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blob-url/{report_type}")
async def get_blob_url(report_type: str, _current_user= Depends(get_current_user_azure)):
    """
    Get the blob storage URL for a report.
    report_type: 'excel' or 'pdf'
    """
    try:
        if report_type == "excel":
            blob_name = "reports/ranked_resumes.xlsx"
        elif report_type == "pdf":
            blob_name = "reports/ranked_resumes.pdf"
        else:
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel' or 'pdf'.")
        
        if not blob_storage.blob_exists(blob_name):
            # Generate reports if they don't exist
            generate_reports_from_blob()
        
        blob_url = blob_storage.get_blob_url(blob_name)
        return JSONResponse(content={"blob_url": blob_url, "blob_name": blob_name})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
