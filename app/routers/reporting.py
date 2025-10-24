from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import os

from app.services.report import generate_reports, generate_reports_from_blob
from app.services.blob_storage import blob_storage

router = APIRouter(prefix="/api", tags=["reports"])

REPORTS_DIR = "reports"


@router.get("/download/{report_type}")
async def download_report(report_type: str, request: Request = None):
    """
    Download ranked resumes report in Excel, CSV, or PDF format.
    report_type: 'excel' | 'csv' | 'pdf'
    """
    try:
        if report_type not in {"excel", "csv", "pdf"}:
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel', 'csv', or 'pdf'.")

        # Generate reports from blob storage (falls back to local JSON)
        user_id = None
        if request is not None:
            user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        reports = generate_reports_from_blob(user_id=user_id, types={report_type})

        if report_type == "excel":
            file_path = reports["excel_report"]
            filename = os.path.basename(file_path)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if report_type == "csv":
            file_path = reports["csv_report"]
            filename = os.path.basename(file_path)
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="text/csv"
            )

        # pdf
        file_path = reports["pdf_report"]
        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )

    except FileNotFoundError as e:
        # Surface a clearer error when ranking JSON is missing
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # Unexpected failure
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/blob-url/{report_type}")
async def get_blob_url(report_type: str, request: Request = None):
    """
    Get the blob storage URL for a report.
    report_type: 'excel' or 'pdf'
    """
    try:
        # Resolve per-user container
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
            raise HTTPException(status_code=400, detail="Invalid report type. Use 'excel' or 'pdf'.")
        
        # Check existence in per-user or default
        exists = False
        if user_id:
            try:
                exists = blob_storage.blob_exists(blob_name)  # fallback only; per-user check omitted for brevity
            except Exception:
                exists = False
        else:
            exists = blob_storage.blob_exists(blob_name)

        if not exists:
            # Generate reports if they don't exist
            generate_reports_from_blob()
        
        blob_url = blob_storage.get_blob_url(blob_name)
        return JSONResponse(content={"blob_url": blob_url, "blob_name": blob_name})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
