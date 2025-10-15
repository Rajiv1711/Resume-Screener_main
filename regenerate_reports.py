"""
Script to regenerate reports from existing ranked_resumes.json
This will test if the fixes work correctly.
"""
import json
import os
from app.services.report import generate_reports

def main():
    # Check if ranked_resumes.json exists
    json_path = "data/ranked_resumes (2).json"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found!")
        return
    
    # Load the JSON data
    print(f"Loading data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        ranked_data = json.load(f)
    
    print(f"Found {len(ranked_data)} candidates")
    
    # Copy to reports directory
    os.makedirs("reports", exist_ok=True)
    reports_json = "reports/ranked_resumes.json"
    
    print(f"Copying to {reports_json}...")
    with open(reports_json, 'w', encoding='utf-8') as f:
        json.dump(ranked_data, f, indent=4)
    
    # Generate reports
    print("Generating reports...")
    try:
        reports = generate_reports()
        print("\n✓ Reports generated successfully!")
        print(f"  - Excel: {reports['excel_report']}")
        print(f"  - CSV: {reports['csv_report']}")
        print(f"  - PDF: {reports['pdf_report']}")
        
        # Show sample of first candidate
        if ranked_data:
            print("\n=== Sample Data ===")
            first = ranked_data[0]
            print(f"Name: {first.get('candidate_name', 'N/A')}")
            print(f"Email: {first.get('email', 'N/A')}")
            print(f"Score: {first.get('final_score', 0) * 100:.2f}%")
            
            # Check for skills
            skills = first.get('skills', [])
            if not skills:
                parsed = first.get('parsed', {})
                skills = parsed.get('skills', []) if parsed else []
            print(f"Skills: {', '.join(skills) if skills else 'No skills found'}")
            
    except Exception as e:
        print(f"\n✗ Error generating reports: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
