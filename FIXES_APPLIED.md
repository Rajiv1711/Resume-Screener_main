# Resume Screener - Fixes Applied

## Issues Identified

### 1. **Missing Skills in Reports and UI**
- **Problem**: Skills were not appearing in CSV, Excel, PDF reports or UI table
- **Root Cause**: Skills data is stored in `resume['parsed']['skills']` but reports and frontend were looking for `resume['skills']`

### 2. **Incorrect Scores in Reports**
- **Problem**: CSV and other reports showed 0.0 for all scores
- **Root Cause**: Report generation was looking for `resume['score']` but LLM ranker outputs `resume['final_score']` (0-1 scale)

### 3. **Wrong Data in UI Dashboard**
- **Problem**: Frontend showed incorrect names, scores, and missing skills
- **Root Cause**: Frontend was trying to extract `hybrid_score` and direct `skills` field, but LLM ranker uses `final_score` and skills are nested in `parsed`

## Fixes Applied

### 1. Backend: `app/services/report.py`

**Updated `_normalize_row()` function to:**
- Extract candidate name from multiple locations: `candidate_name`, `parsed.name`, or `file`
- Extract email from both direct and parsed locations
- Extract skills from both `resume['skills']` and `resume['parsed']['skills']`
- Handle score conversion properly:
  - Check for `score` (already percentage)
  - Check for `final_score` (0-1 scale, convert to percentage)
  - Fallback to `hybrid_score`

```python
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
    
    return name, email, score_val, skills
```

### 2. Backend: `app/routers/insights.py`

**Updated insights calculation to:**
- Check for `score` (percentage) first
- Fallback to `final_score` (0-1 scale, convert to percentage)
- Handle skills from both direct and parsed locations

```python
# Handle both 'score' (percentage) and 'final_score' (0-1 scale) fields
scores = []
for resume in ranked_data:
    score = resume.get("score")
    if score is None:
        # Try final_score from LLM ranker (0-1 scale, convert to percentage)
        final_score = resume.get("final_score", 0)
        score = final_score * 100
    scores.append(score)
```

### 3. Backend: `app/services/llm_based_ranker.py`

**Added skills extraction to ranking results:**
- Extract skills from `parsed['skills']` during ranking
- Include skills in the result dictionary

```python
# Extract skills from parsed data
parsed = resume.get('parsed', {}) or {}
skills = parsed.get('skills', [])
if not isinstance(skills, list):
    skills = []

result = {
    # ... other fields ...
    'skills': skills
}
```

### 4. Frontend: `frontend/src/pages/Dashboard.js`

**Updated data mapping to:**
- Handle `final_score` (0-1), `hybrid_score`, and `score` fields
- Extract name from `candidate_name`, `parsed.name`, or `file`
- Extract skills from both direct and parsed locations

```javascript
const mapped = ranked.map((r, i) => {
  // Extract score - handle both final_score (0-1 from LLM) and hybrid_score
  let score = 0;
  if (r?.final_score !== undefined) {
    score = Math.round(r.final_score * 100);
  } else if (r?.hybrid_score !== undefined) {
    score = Math.round(r.hybrid_score * 100);
  } else if (r?.score !== undefined) {
    score = Math.round(r.score);
  }

  // Extract name - try candidate_name first, then parsed.name, then file
  let name = r?.candidate_name || (r?.parsed && r.parsed.name) || r?.file || `Candidate ${i + 1}`;
  
  // Extract skills - check multiple locations
  let skills = [];
  if (Array.isArray(r?.skills)) {
    skills = r.skills;
  } else if (r?.parsed && Array.isArray(r.parsed.skills)) {
    skills = r.parsed.skills;
  }

  return {
    ...r,
    score,
    name,
    skills
  };
});
```

## Testing the Fixes

### Option 1: Regenerate Reports from Existing JSON
Run the provided script to regenerate reports from your existing JSON:

```bash
python regenerate_reports.py
```

This will:
1. Load `data/ranked_resumes (2).json`
2. Copy it to `reports/ranked_resumes.json`
3. Generate Excel, CSV, and PDF reports with correct data
4. Show you a sample of the first candidate with skills

### Option 2: Run Full Ranking Process
1. Start the backend: `uvicorn app.main:app --reload`
2. Upload resumes via the UI
3. Enter job description and click "Rank Resumes"
4. Download reports and verify:
   - ✓ Scores show correct percentages (not 0.0)
   - ✓ Skills appear in reports
   - ✓ Candidate names are correct
   - ✓ UI table shows all data properly

## Summary of Changes

| File | Changes |
|------|---------|
| `app/services/report.py` | Updated `_normalize_row()` to handle multiple data structures for name, email, skills, and score |
| `app/routers/insights.py` | Fixed score calculation to handle `final_score` and skills from parsed data |
| `app/services/llm_based_ranker.py` | Added skills extraction to ranking results |
| `frontend/src/pages/Dashboard.js` | Updated data mapping to handle LLM ranker output format |

## Expected Results After Fixes

### CSV Report (data/ranked_resumes (1).csv)
```csv
Rank,Candidate Name,Email,File,Score (%),Top Skills
1,SARAH JOHNSON,sarah.johnson@email.com,sample_resume_2.txt,64.05,"Python, Machine Learning, SQL, Data Science, Analytics"
2,JOHN SMITH,john.smith@email.com,sample_resume_1.txt,61.87,"Python, NumPy, Pandas, Scikit-learn, TensorFlow"
...
```

### UI Dashboard
- ✓ Correct candidate names displayed
- ✓ Scores show as percentages (64%, 62%, etc.)
- ✓ Skills badges appear for each candidate
- ✓ Insights charts work correctly

### Excel/PDF Reports
- ✓ All columns populated with correct data
- ✓ Skills listed in comma-separated format
- ✓ Scores displayed as percentages
