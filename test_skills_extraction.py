"""
Test script to verify that skills are being extracted properly from resumes
"""
import os
from app.services.parser import parse_resume

# Sample resume text to test
SAMPLE_RESUME = """
SARAH JOHNSON
Email: sarah.johnson@email.com | Phone: (555) 123-4567

SUMMARY
Experienced Data Scientist with 5+ years of expertise in machine learning, statistical modeling, and data visualization.

SKILLS
Technical: Python, R, SQL, Java
ML/AI: TensorFlow, PyTorch, scikit-learn, Keras
Data: Pandas, NumPy, Matplotlib, Seaborn, Tableau, Power BI
Cloud: AWS (S3, EC2, SageMaker), Azure ML
Tools: Git, Docker, Jupyter, VS Code

EXPERIENCE
Senior Data Scientist | Tech Corp | 2020 - Present
- Developed predictive models using TensorFlow and scikit-learn
- Built ETL pipelines with Apache Spark and Airflow
- Deployed models on AWS SageMaker and Kubernetes
- Created dashboards using Tableau and Plotly

Data Analyst | StartupXYZ | 2018 - 2020
- Analyzed data using Python (Pandas, NumPy) and SQL
- Implemented machine learning models with scikit-learn
- Visualized insights using Matplotlib and Seaborn

EDUCATION
Master of Science in Data Science | State University | 2018
Bachelor of Science in Statistics | State University | 2016

PROJECTS
- Customer Churn Prediction: Built model using Random Forest and XGBoost
- NLP Sentiment Analysis: Implemented using BERT and Transformers
- Recommendation System: Developed using Collaborative Filtering
"""

def test_local_file():
    """Test parsing a local file if available"""
    test_file = "data/raw_resumes/sample_resume.txt"
    
    if os.path.exists(test_file):
        print(f"Testing with local file: {test_file}")
        try:
            result = parse_resume(test_file)
            print("\n✓ Parsing successful!")
            print(f"\nFile: {result.get('file')}")
            
            parsed = result.get('parsed', {})
            print(f"Name: {parsed.get('name', 'NOT FOUND')}")
            print(f"Email: {parsed.get('email', 'NOT FOUND')}")
            
            skills = parsed.get('skills', [])
            print(f"\nSkills extracted: {len(skills)}")
            if skills:
                print("Skills:", ", ".join(skills))
            else:
                print("⚠️  No skills extracted!")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Local file not found: {test_file}")

def test_sample_text():
    """Test parsing sample resume text"""
    print("\n" + "=" * 60)
    print("Testing with sample resume text...")
    print("=" * 60)
    
    # Save to temp file
    temp_file = "temp_test_resume.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_RESUME)
    
    try:
        result = parse_resume(temp_file)
        print("\n✓ Parsing successful!")
        
        parsed = result.get('parsed', {})
        print(f"\nName: {parsed.get('name', 'NOT FOUND')}")
        print(f"Email: {parsed.get('email', 'NOT FOUND')}")
        
        skills = parsed.get('skills', [])
        print(f"\n📊 Skills extracted: {len(skills)}")
        
        if skills:
            print("\n✓ Skills found:")
            for i, skill in enumerate(skills, 1):
                print(f"  {i}. {skill}")
        else:
            print("\n❌ WARNING: No skills were extracted!")
            print("\nThis could mean:")
            print("  1. GPT parser needs better prompting")
            print("  2. API key issue")
            print("  3. Skills section format not recognized")
            
        # Show experience
        experience = parsed.get('experience', [])
        if experience:
            print(f"\n✓ Experience entries: {len(experience)}")
            for exp in experience[:2]:  # Show first 2
                print(f"  - {exp[:80]}...")
        
    except Exception as e:
        print(f"\n✗ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        processed = f"data/processed/{temp_file}.txt"
        if os.path.exists(processed):
            os.remove(processed)

def main():
    print("Skills Extraction Test")
    print("=" * 60)
    
    # Test with local file first
    test_local_file()
    
    # Test with sample text
    test_sample_text()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nIf skills are not being extracted:")
    print("  1. Check Azure OpenAI API key and endpoint")
    print("  2. Verify the model deployment name is correct")
    print("  3. Try running ranking again - the improved parser should work")

if __name__ == "__main__":
    main()
