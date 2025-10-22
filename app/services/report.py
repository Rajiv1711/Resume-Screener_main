import os
import json
from openpyxl import Workbook
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from app.services.blob_storage import blob_storage

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def _normalize_row(resume, idx):
    # Extract candidate name - check multiple possible locations
    parsed = resume.get("parsed", {}) or {}
    name = resume.get("candidate_name") or parsed.get("name") or resume.get("file", f"Candidate {idx}")
    
    # Extract email
    email = resume.get("email") or parsed.get("email", "N/A")
    
    # Extract skills - check both direct and parsed locations
    skills = resume.get("skills", []) or parsed.get("skills", []) or []
    if not isinstance(skills, list):
        skills = []
    
    # Extract score - handle different field names and formats
    score_val = resume.get("score")
    if score_val is None:
        # Try final_score from LLM ranker (0-1 scale)
        final_score = resume.get("final_score")
        if final_score is not None:
            score_val = round(float(final_score) * 100, 2)
        else:
            # Fallback to hybrid_score
            score_val = round(float(resume.get("hybrid_score", 0)) * 100, 2)
    
    # Extract recommendation and reasoning summary
    recommendation = resume.get("recommendation") or ""
    reasoning = resume.get("reasoning") or ""
    # Sanitize and summarize reasoning for CSV/tooltips
    reasoning_clean = str(reasoning).replace("\r", " ").replace("\n", " ").strip()
    if len(reasoning_clean) > 240:
        reasoning_clean = reasoning_clean[:237] + "..."
    
    return name, email, score_val, skills, recommendation, reasoning_clean


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
        name, email, score_val, skills, recommendation, reasoning_summary = _normalize_row(resume, idx)
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
    Generate a more insightful PDF report with summary and candidate details.
    """
    pdf_path = os.path.join(REPORTS_DIR, "ranked_resumes.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>Resume Screener - Ranked Candidates Report</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Summary Insights
    scores = []
    for r in ranked_results:
        sc = r.get("score")
        if sc is None:
            sc = float(r.get("final_score", 0)) * 100.0
        scores.append(float(sc or 0))
    total = len(ranked_results)
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    high = len([s for s in scores if s >= 80])
    med = len([s for s in scores if 60 <= s < 80])
    low = len([s for s in scores if s < 60])
    summary_par = Paragraph(
        f"<b>Summary:</b> Total Candidates: {total} | Average Score: {avg_score}% | High Matches: {high} | Medium: {med} | Low: {low}",
        styles["Normal"],
    )
    elements.append(summary_par)
    elements.append(Spacer(1, 12))

    # Ranked Table
    table_data = [["Rank", "Candidate", "Email", "Score (%)", "Top Skills"]]

    for idx, resume in enumerate(ranked_results, start=1):
        name, email, score_val, skills, recommendation, reasoning_summary = _normalize_row(resume, idx)
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
    elements.append(PageBreak())

    # Detailed Insights for Top Candidates
    elements.append(Paragraph("<b>Top Candidates - Detailed Insights</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    top_n = min(5, len(ranked_results))
    for i in range(top_n):
        r = ranked_results[i]
        name = r.get("candidate_name") or r.get("parsed", {}).get("name") or r.get("file", f"Candidate {i+1}")
        score = r.get("score")
        if score is None:
            score = round(float(r.get("final_score", 0)) * 100.0, 2)
        rec = r.get("recommendation", "")
        strengths = r.get("strengths", [])
        concerns = r.get("concerns", [])
        missing = r.get("missing_skills", [])

        elements.append(Paragraph(f"<b>#{i+1} {name}</b> — Score: {score}% — Recommendation: {rec}", styles["Heading3"]))
        if strengths:
            elements.append(Paragraph("<u>Strengths</u>", styles["BodyText"]))
            for s in strengths[:5]:
                elements.append(Paragraph(f"• {s}", styles["BodyText"]))
        if concerns:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("<u>Concerns</u>", styles["BodyText"]))
            for c in concerns[:5]:
                elements.append(Paragraph(f"• {c}", styles["BodyText"]))
        if missing:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("<u>Missing Skills</u>", styles["BodyText"]))
            elements.append(Paragraph(", ".join(missing[:10]), styles["BodyText"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)

    return pdf_path


def generate_csv_report(ranked_results):
    """
    Generate CSV report of ranked resumes.
    """
    csv_path = os.path.join(REPORTS_DIR, "ranked_resumes.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
    writer.writerow(["Rank", "Candidate Name", "Email", "File", "Score (%)", "Recommendation", "Reasoning", "Top Skills"])
    for idx, resume in enumerate(ranked_results, start=1):
        name, email, score_val, skills, recommendation, _reasoning_summary = _normalize_row(resume, idx)
        reasoning_full = resume.get("reasoning", "")
        writer.writerow([idx, name, email, resume.get("file", "N/A"), score_val, recommendation, reasoning_full, ", ".join(skills)])
    return sio.getvalue().encode("utf-8")


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


def generate_reports_from_blob(user_id: str | None = None):
    """
    Read the ranked JSON file from blob storage (prefer latest user session) and generate Excel/CSV/PDF.
    """
    ranked_results = []
    # Prefer per-user latest session file if user_id provided
    if user_id:
        try:
            sessions = blob_storage.list_user_sessions(user_id)
            for s in sessions:
                try:
                    content = blob_storage.download_file_session("reports/ranked_resumes.json", user_id, s['session_id'])
                    ranked_results = json.loads(content.decode('utf-8'))
                    if ranked_results:
                        break
                except Exception:
                    continue
        except Exception:
            ranked_results = []
    
    if not ranked_results:
        try:
            # Try shared/root blob as fallback
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
