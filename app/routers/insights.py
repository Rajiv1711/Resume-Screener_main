# app/routers/insights.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import json
import os

router = APIRouter(prefix="/api", tags=["insights"])

@router.get("/insights")
async def get_insights(
    request: Request = None,
):
    """
    Get insights and analytics data from the latest ranking results.
    Works with both Azure AD and guest authentication.
    """
    try:
        # Allow access without strict auth for now
        current_user = getattr(request.state, "user", {}) or {}
        # Try to read from per-user blob storage first
        user_id = None
        if request is not None:
            user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        reports_file = "reports/ranked_resumes.json"
        
        if user_id:
            try:
                from app.services.blob_storage import blob_storage
                content = blob_storage.download_file_user("reports/ranked_resumes.json", user_id)
                ranked_data = json.loads(content.decode('utf-8'))
            except Exception:
                ranked_data = []
        elif os.path.exists(reports_file):
            with open(reports_file, "r", encoding="utf-8") as f:
                ranked_data = json.load(f)
        else:
            # If no local file, return empty insights
            ranked_data = []
        
        if not ranked_data:
            return JSONResponse(content={
                "status": "success",
                "insights": {
                    "total_resumes": 0,
                    "average_score": 0,
                    "high_matches": 0,
                    "medium_matches": 0,
                    "low_matches": 0,
                    "skills_distribution": [],
                    "score_distribution": []
                }
            })
        
        # Calculate insights
        total_resumes = len(ranked_data)
        scores = [resume.get("score", 0) for resume in ranked_data]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Score categories
        high_matches = len([s for s in scores if s >= 80])
        medium_matches = len([s for s in scores if 60 <= s < 80])
        low_matches = len([s for s in scores if s < 60])
        
        # Skills distribution (simplified)
        skills_count = {}
        for resume in ranked_data:
            skills = resume.get("skills", [])
            if isinstance(skills, list):
                for skill in skills:
                    if isinstance(skill, str):
                        skills_count[skill] = skills_count.get(skill, 0) + 1
        
        # Top 10 skills
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
        skills_distribution = [{"skill": skill, "count": count} for skill, count in top_skills]
        
        # Score distribution (bins)
        score_bins = [
            {"range": "90-100", "count": len([s for s in scores if 90 <= s <= 100])},
            {"range": "80-89", "count": len([s for s in scores if 80 <= s < 90])},
            {"range": "70-79", "count": len([s for s in scores if 70 <= s < 80])},
            {"range": "60-69", "count": len([s for s in scores if 60 <= s < 70])},
            {"range": "50-59", "count": len([s for s in scores if 50 <= s < 60])},
            {"range": "0-49", "count": len([s for s in scores if s < 50])}
        ]
        
        insights = {
            "total_resumes": total_resumes,
            "average_score": round(average_score, 2),
            "high_matches": high_matches,
            "medium_matches": medium_matches,
            "low_matches": low_matches,
            "skills_distribution": skills_distribution,
            "score_distribution": score_bins,
            # Provide minimal user details for UI; middleware model uses dict
            "user_type": current_user.get("auth_type"),
            "user_name": current_user.get("username"),
        }
        
        return JSONResponse(content={
            "status": "success",
            "insights": insights
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))