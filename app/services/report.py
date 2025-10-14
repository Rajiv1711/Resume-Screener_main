import os
import json
from openpyxl import Workbook
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from app.services.blob_storage import blob_storage

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def _normalize_row(resume, idx):
    parsed = resume.get("parsed", {}) or {}
    name = parsed.get("name") or resume.get("file", f"Candidate {idx}")
    email = parsed.get("email", "N/A")
    skills = resume.get("skills", []) or []
    # Prefer 'score' if already computed; else derive from hybrid_score
    score_val = resume.get("score")
    if score_val is None:
        score_val = round(float(resume.get("hybrid_score", 0)) * 100, 2)
    return name, email, score_val, skills


def generate_excel_report(ranked_results):
    """
    Generate Excel report of ranked resumes.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Ranked Resumes"

    headers = ["Rank", "Candidate Name", "Email", "File", "Score (%)", "Top Skills"]
    ws.append(headers)

    # Populate rows
    for idx, resume in enumerate(ranked_results, start=1):
        name, email, score_val, skills = _normalize_row(resume, idx)
        ws.append([
            idx,
            name,
            email,
            resume.get("file", "N/A"),
            score_val,
            ", ".join(skills)
        ])

    excel_path = os.path.join(REPORTS_DIR, "ranked_resumes.xlsx")
    wb.save(excel_path)
    return excel_path


def generate_pdf_report(ranked_results):
    """
    Generate PDF summary of ranked resumes.
    """
    pdf_path = os.path.join(REPORTS_DIR, "ranked_resumes.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>Resume Screener - Ranked Candidates Report</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table Data
    table_data = [["Rank", "Candidate", "Email", "Score (%)", "Top Skills"]]

    for idx, resume in enumerate(ranked_results, start=1):
        name, email, score_val, skills = _normalize_row(resume, idx)
        row = [idx, name, email, score_val, ", ".join(skills)]
        table_data.append(row)

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4B8BBE")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

    return pdf_path


def generate_csv_report(ranked_results):
    """
    Generate CSV report of ranked resumes.
    """
    csv_path = os.path.join(REPORTS_DIR, "ranked_resumes.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Candidate Name", "Email", "File", "Score (%)", "Top Skills"])
        for idx, resume in enumerate(ranked_results, start=1):
            name, email, score_val, skills = _normalize_row(resume, idx)
            writer.writerow([idx, name, email, resume.get("file", "N/A"), score_val, ", ".join(skills)])
    return csv_path


def generate_reports():
    """
    Read the ranked JSON file and generate both Excel and PDF reports.
    """
    json_path = os.path.join(REPORTS_DIR, "ranked_resumes.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError("Ranked results JSON not found. Please run ranking first.")

    with open(json_path, "r", encoding="utf-8") as f:
        ranked_results = json.load(f)

    excel_path = generate_excel_report(ranked_results)
    csv_path = generate_csv_report(ranked_results)
    pdf_path = generate_pdf_report(ranked_results)

    return {
        "excel_report": excel_path,
        "csv_report": csv_path,
        "pdf_report": pdf_path
    }


def generate_reports_from_blob():
    """
    Read the ranked JSON file from blob storage and generate both Excel and PDF reports.
    """
    try:
        # Try to read from blob storage first
        json_content = blob_storage.download_file("reports/ranked_resumes.json")
        ranked_results = json.loads(json_content.decode('utf-8'))
    except Exception:
        # Fallback to local file
        json_path = os.path.join(REPORTS_DIR, "ranked_resumes.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError("Ranked results JSON not found. Please run ranking first.")
        
        with open(json_path, "r", encoding="utf-8") as f:
            ranked_results = json.load(f)

    excel_path = generate_excel_report(ranked_results)
    csv_path = generate_csv_report(ranked_results)
    pdf_path = generate_pdf_report(ranked_results)
    
    # Upload reports to blob storage
    with open(excel_path, "rb") as f:
        excel_content = f.read()
    blob_storage.upload_file(excel_content, f"reports/{os.path.basename(excel_path)}")
    
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()
    blob_storage.upload_file(pdf_content, f"reports/{os.path.basename(pdf_path)}")

    # Upload CSV as well
    with open(csv_path, "rb") as f:
        csv_content = f.read()
    blob_storage.upload_file(csv_content, f"reports/{os.path.basename(csv_path)}")

    return {
        "excel_report": excel_path,
        "csv_report": csv_path,
        "pdf_report": pdf_path,
        "excel_blob": f"reports/{os.path.basename(excel_path)}",
        "csv_blob": f"reports/{os.path.basename(csv_path)}",
        "pdf_blob": f"reports/{os.path.basename(pdf_path)}"
    }
