"""
Quick script to verify the data structure in your JSON file
"""
import json
import os

def verify_json_structure():
    json_path = "data/ranked_resumes (2).json"
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return
    
    print(f"✓ Loading {json_path}...\n")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total candidates: {len(data)}\n")
    print("=" * 60)
    
    # Check first candidate structure
    if data:
        first = data[0]
        print("First Candidate Data Structure:\n")
        
        # Top-level fields
        print("📋 Top-level fields:")
        print(f"  - file: {first.get('file', 'NOT FOUND')}")
        print(f"  - candidate_name: {first.get('candidate_name', 'NOT FOUND')}")
        print(f"  - email: {first.get('email', 'NOT FOUND')}")
        print(f"  - final_score: {first.get('final_score', 'NOT FOUND')}")
        print(f"  - recommendation: {first.get('recommendation', 'NOT FOUND')}")
        print(f"  - rank: {first.get('rank', 'NOT FOUND')}")
        
        # Skills check
        print(f"\n🔧 Skills check:")
        top_skills = first.get('skills', None)
        print(f"  - Direct skills field: {top_skills}")
        
        parsed = first.get('parsed', {})
        if parsed:
            parsed_skills = parsed.get('skills', None)
            print(f"  - Parsed skills field: {parsed_skills}")
        else:
            print(f"  - No 'parsed' field found")
        
        # Score conversion
        print(f"\n📊 Score information:")
        final_score = first.get('final_score', 0)
        print(f"  - final_score (raw): {final_score}")
        print(f"  - final_score (percentage): {final_score * 100:.2f}%")
        
        print("\n" + "=" * 60)
        print("\n💡 Issues detected:")
        
        issues = []
        if not first.get('skills') and not (parsed and parsed.get('skills')):
            issues.append("❌ Skills are missing from both direct and parsed locations")
        elif not first.get('skills') and parsed and parsed.get('skills'):
            issues.append("⚠️  Skills only in parsed location (needs fix)")
        else:
            issues.append("✓ Skills are available")
        
        if not first.get('score') and first.get('final_score'):
            issues.append("⚠️  Using final_score (0-1 scale) - needs conversion to percentage")
        
        for issue in issues:
            print(f"  {issue}")
        
        print("\n" + "=" * 60)
        print("\n✨ After applying fixes:")
        print("  ✓ Skills will be extracted from parsed location")
        print("  ✓ Scores will be converted to percentages (0-100)")
        print("  ✓ Reports will show correct data")
        print("  ✓ UI will display all information properly")

if __name__ == "__main__":
    verify_json_structure()
