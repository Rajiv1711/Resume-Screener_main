from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
import os

from app.services.report import generate_reports_from_blob
from app.services.blob_storage import blob_storage

router = APIRouter(prefix="/api", tags=["reports"])

REPORTS_DIR = "reports"  # deprecated: local storage disabled


@router.get("/download/{report_type}")
async def download_report(report_type: str, request: Request = None):
    """
    Download ranked resumes report in Excel, CSV, or PDF format from blob storage.
    report_type: 'excel' | 'csv' | 'pdf'
    """
    try:
        # Ensure reports exist in blob storage (generate if missing)
        user_id = None
        if request is not None:
            user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        reports = generate_reports_from_blob(user_id=user_id)

        if report_type == "excel":
            blob_name = reports["excel_blob"]
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = os.path.basename(blob_name)
        elif report_type == "csv":
            blob_name = reports["csv_blob"]
            media_type = "text/csv"
            filename = os.path.basename(blob_name)
        elif report_type == "pdf":
            blob_name = reports["pdf_blob"]
            media_type = "application/pdf"
            filename = os.path.basename(blob_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel', 'csv', or 'pdf'.")

        content = blob_storage.download_file(blob_name)
        return Response(content=content, media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blob-url/{report_type}")
async def get_blob_url(report_type: str, request: Request = None):
    """
    Get the blob storage URL for a report.
    report_type: 'excel' | 'csv' | 'pdf'
    """
    try:
        # Ensure reports exist
        user_id = None
        if request is not None:
            user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")

        if report_type == "excel":
            blob_name = "reports/ranked_resumes.xlsx"
        elif report_type == "csv":
            blob_name = "reports/ranked_resumes.csv"
        elif report_type == "pdf":
            blob_name = "reports/ranked_resumes.pdf"
        else:
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel', 'csv', or 'pdf'.")

        exists = blob_storage.blob_exists(blob_name)
        if not exists:
            generate_reports_from_blob(user_id=user_id)

        blob_url = blob_storage.get_blob_url(blob_name)
        return JSONResponse(content={"blob_url": blob_url, "blob_name": blob_name})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
