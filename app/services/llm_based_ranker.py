"""
LLM-Based Resume Ranking System
Uses GPT with few-shot prompting to evaluate resumes like a human HR professional.
Combines 30% keyword matching with 70% LLM-based human-like evaluation.
"""

import json
import logging
from typing import Dict, List, Tuple
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class LLMBasedRanker:
    """
    Advanced resume ranking using LLM with few-shot prompting.
    Evaluates resumes considering experience, skills, projects, career gaps, etc.
    """
    
    def __init__(self):
        # Configure Azure OpenAI
        self.client = AzureOpenAI(
            api_key="C6GA6hGNxN48a6A2jR6JyhDYTzbnwfvHJuYTM2FUz4olCPa2mBq0JQQJ99BIAC77bzfXJ3w3AAABACOGAz1x",
            api_version="2024-12-01-preview",
            azure_endpoint="https://parseroa.openai.azure.com/"
        )
        
        # Few-shot examples for resume evaluation
        self.few_shot_examples = self._create_few_shot_examples()
    
    def rank_resumes(self, resumes: List[Dict], job_description: str, 
                    keyword_weight: float = 0.3) -> List[Dict]:
        """
        Rank resumes using LLM-based evaluation combined with keyword matching.
        
        Args:
            resumes: List of parsed resume dictionaries
            job_description: Job description to evaluate against
            keyword_weight: Weight for keyword matching (default 0.3)
            
        Returns:
            Ranked list of resumes with detailed LLM-based scoring
        """
        ranked_results = []
        
        for resume in resumes:
            try:
                # Extract resume content
                resume_text = self._extract_resume_content(resume)
                
                # Get LLM evaluation (70% weight)
                llm_evaluation = self._get_llm_evaluation(resume_text, job_description)
                
                # Calculate keyword matching score (30% weight)
                keyword_score = self._calculate_keyword_score(resume_text, job_description)
                
                # Combine scores
                final_score = (keyword_weight * keyword_score + 
                              (1 - keyword_weight) * llm_evaluation['overall_score'])
                
                # Extract skills from parsed data
                parsed = resume.get('parsed', {}) or {}
                skills = parsed.get('skills', [])
                if not isinstance(skills, list):
                    skills = []
                
                result = {
                    'file': resume.get('file', 'Unknown'),
                    'candidate_name': parsed.get('name', 'Unknown'),
                    'email': parsed.get('email', ''),
                    'final_score': round(final_score, 4),
                    'keyword_score': round(keyword_score, 4),
                    'llm_score': round(llm_evaluation['overall_score'], 4),
                    
                    # Detailed LLM evaluation
                    'experience_score': llm_evaluation['experience_score'],
                    'skills_score': llm_evaluation['skills_score'],
                    'education_score': llm_evaluation['education_score'],
                    'projects_score': llm_evaluation['projects_score'],
                    'career_progression_score': llm_evaluation['career_progression_score'],
                    'cultural_fit_score': llm_evaluation['cultural_fit_score'],
                    
                    # LLM insights
                    'strengths': llm_evaluation['strengths'],
                    'concerns': llm_evaluation['concerns'],
                    'missing_skills': llm_evaluation['missing_skills'],
                    'recommendation': llm_evaluation['recommendation'],
                    'reasoning': llm_evaluation['reasoning'],
                    
                    # Additional metadata
                    'total_experience': llm_evaluation.get('total_experience', 'Not specified'),
                    'education_level': llm_evaluation.get('education_level', 'Not specified'),
                    'key_achievements': llm_evaluation.get('key_achievements', []),
                    
                    # Skills from parsed resume
                    'skills': skills
                }
                
                ranked_results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing resume {resume.get('file', 'Unknown')}: {str(e)}")
                ranked_results.append({
                    'file': resume.get('file', 'Unknown'),
                    'error': str(e),
                    'final_score': 0.0,
                    'recommendation': 'Error in processing'
                })
        
        # Sort by final score descending
        ranked_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Add ranking positions
        for i, result in enumerate(ranked_results, 1):
            result['rank'] = i
        
        return ranked_results
    
    def _get_llm_evaluation(self, resume_text: str, job_description: str) -> Dict:
        """
        Get comprehensive LLM evaluation of resume against job description.
        """
        prompt = self._build_evaluation_prompt(resume_text, job_description)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-35-turbo",
                messages=prompt,
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            evaluation_text = response.choices[0].message.content
            evaluation = json.loads(evaluation_text)
            
            # Ensure all required fields are present with defaults
            return {
                'overall_score': float(evaluation.get('overall_score', 0.5)),
                'experience_score': float(evaluation.get('experience_score', 0.5)),
                'skills_score': float(evaluation.get('skills_score', 0.5)),
                'education_score': float(evaluation.get('education_score', 0.5)),
                'projects_score': float(evaluation.get('projects_score', 0.5)),
                'career_progression_score': float(evaluation.get('career_progression_score', 0.5)),
                'cultural_fit_score': float(evaluation.get('cultural_fit_score', 0.5)),
                'strengths': evaluation.get('strengths', []),
                'concerns': evaluation.get('concerns', []),
                'missing_skills': evaluation.get('missing_skills', []),
                'recommendation': evaluation.get('recommendation', 'Neutral'),
                'reasoning': evaluation.get('reasoning', 'No reasoning provided'),
                'total_experience': evaluation.get('total_experience', 'Not specified'),
                'education_level': evaluation.get('education_level', 'Not specified'),
                'key_achievements': evaluation.get('key_achievements', [])
            }
            
        except Exception as e:
            logger.error(f"LLM evaluation failed: {str(e)}")
            # Return default neutral evaluation
            return {
                'overall_score': 0.5,
                'experience_score': 0.5,
                'skills_score': 0.5,
                'education_score': 0.5,
                'projects_score': 0.5,
                'career_progression_score': 0.5,
                'cultural_fit_score': 0.5,
                'strengths': [],
                'concerns': ['Unable to evaluate due to processing error'],
                'missing_skills': [],
                'recommendation': 'Manual Review Required',
                'reasoning': 'Automated evaluation failed',
                'total_experience': 'Unknown',
                'education_level': 'Unknown',
                'key_achievements': []
            }
    
    def _build_evaluation_prompt(self, resume_text: str, job_description: str) -> List[Dict]:
        """
        Build the few-shot prompt for LLM evaluation.
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert HR professional and technical recruiter with 15+ years of experience. Your task is to evaluate resumes against job descriptions and provide comprehensive, fair, and insightful assessments.

You must evaluate candidates based on these criteria:
1. **Experience Relevance** (25%): How well does their experience match the role?
2. **Technical Skills** (20%): Do they have the required technical competencies?
3. **Education Background** (15%): Does their education align with requirements?
4. **Project Portfolio** (15%): Quality and relevance of projects/achievements
5. **Career Progression** (15%): Growth trajectory and advancement
6. **Cultural & Role Fit** (10%): Soft skills, leadership, teamwork

**Important Guidelines:**
- Be objective and fair - avoid bias based on name, gender, or background
- Consider career gaps contextually (education, family, economic factors)
- Value diverse paths to expertise (bootcamps, self-taught, non-traditional backgrounds)
- Look for growth potential, not just current perfect matches
- Consider the full candidate profile, not just keyword matching
- Provide actionable, constructive feedback

**Output Format:** Always respond with valid JSON containing all required fields."""
            }
        ]
        
        # Add few-shot examples
        messages.extend(self.few_shot_examples)
        
        # Add the actual evaluation request
        messages.append({
            "role": "user",
            "content": f"""Please evaluate this resume against the job description:

**Job Description:**
{job_description}

**Resume:**
{resume_text}

Provide a comprehensive evaluation in JSON format with all the following fields:
- overall_score (0.0-1.0)
- experience_score (0.0-1.0)
- skills_score (0.0-1.0)
- education_score (0.0-1.0)
- projects_score (0.0-1.0)
- career_progression_score (0.0-1.0)
- cultural_fit_score (0.0-1.0)
- strengths (array of strings)
- concerns (array of strings)
- missing_skills (array of strings)
- recommendation (string: "Strong Hire" | "Hire" | "Consider" | "Weak Fit" | "No Hire")
- reasoning (string explaining the overall assessment)
- total_experience (string describing years/type of experience)
- education_level (string describing highest education)
- key_achievements (array of notable accomplishments)"""
        })
        
        return messages
    
    def _create_few_shot_examples(self) -> List[Dict]:
        """
        Create few-shot examples for consistent LLM evaluation.
        """
        return [
            # Example 1: Strong Senior Candidate
            {
                "role": "user",
                "content": """Please evaluate this resume against the job description:

**Job Description:**
Senior Software Engineer - Python/Django
We're seeking a Senior Software Engineer with 5+ years of experience in Python, Django, and cloud technologies. The role involves leading a small team, architecting scalable solutions, and mentoring junior developers. Requirements: Python, Django, AWS, PostgreSQL, Redis, leadership experience.

**Resume:**
Sarah Johnson
sarah.j@email.com | LinkedIn: linkedin.com/in/sarahj

EXPERIENCE:
Lead Software Engineer | TechCorp | 2020-Present (4 years)
- Led team of 4 developers building e-commerce platform serving 500K+ users
- Architected microservices using Python/Django, deployed on AWS EKS
- Implemented caching with Redis, reduced response times by 60%
- Mentored 3 junior developers, 2 promoted to mid-level

Software Engineer | StartupXYZ | 2018-2020 (2 years)  
- Built REST APIs using Django REST Framework
- Designed PostgreSQL database schemas for user management system
- Implemented CI/CD pipeline with GitHub Actions and AWS

Software Developer | LocalCorp | 2016-2018 (2 years)
- Developed web applications using Python/Flask
- Worked with MySQL databases and basic AWS services

EDUCATION:
B.S. Computer Science | State University | 2016
GPA: 3.7/4.0

PROJECTS:
- Open Source Contributor: Django REST framework (200+ stars)
- Personal Project: ML-powered recommendation engine using TensorFlow

SKILLS: Python, Django, Flask, AWS (EC2, RDS, S3), PostgreSQL, Redis, Docker, Kubernetes"""
            },
            {
                "role": "assistant", 
                "content": json.dumps({
                    "overall_score": 0.88,
                    "experience_score": 0.90,
                    "skills_score": 0.95,
                    "education_score": 0.80,
                    "projects_score": 0.85,
                    "career_progression_score": 0.90,
                    "cultural_fit_score": 0.85,
                    "strengths": [
                        "Strong technical match - all required skills present",
                        "Excellent leadership experience with team management",
                        "Clear career progression from developer to lead",
                        "Quantifiable achievements (500K users, 60% performance improvement)",
                        "Active open source contributor shows commitment to craft",
                        "Relevant mentoring experience"
                    ],
                    "concerns": [
                        "Slightly below 5 years requirement (4 years current + 2+2 = 8 total)",
                        "No specific mention of system design at scale"
                    ],
                    "missing_skills": [],
                    "recommendation": "Strong Hire",
                    "reasoning": "Sarah is an excellent candidate who meets or exceeds most requirements. Her 8 years of progressive experience, strong technical skills, and proven leadership make her ideal for this senior role. The quantifiable impact and mentoring experience demonstrate she can both deliver results and grow team members.",
                    "total_experience": "8 years in software development with 4 years in leadership",
                    "education_level": "Bachelor's in Computer Science",
                    "key_achievements": [
                        "Led team building platform for 500K+ users",
                        "60% performance improvement through optimization",
                        "Successfully mentored developers to promotion"
                    ]
                })
            },
            
            # Example 2: Junior Candidate with Potential  
            {
                "role": "user",
                "content": """Please evaluate this resume against the job description:

**Job Description:**
Software Engineer - Full Stack
Looking for a Software Engineer with 2+ years experience in React, Node.js, and database technologies. Will work on our web application serving enterprise clients. Requirements: JavaScript, React, Node.js, SQL databases, REST APIs.

**Resume:**
Alex Chen
alex.chen@email.com

EXPERIENCE:
Junior Developer | WebCorp | 2022-Present (2 years)
- Built React components for customer dashboard
- Created Node.js APIs for user authentication
- Worked with MongoDB for data storage
- Fixed bugs and implemented small features

Intern | TechStart | Summer 2022 (3 months)
- Learned React and JavaScript fundamentals  
- Built simple CRUD application with Express.js
- Assisted senior developers with testing

EDUCATION:
Coding Bootcamp - Full Stack Web Development | 2022
- 6-month intensive program
- Final project: E-commerce site using MERN stack

B.A. Marketing | University | 2019
GPA: 3.2/4.0

PROJECTS:
- Personal Portfolio: React website with Node.js backend
- Todo App: CRUD app with MongoDB

SKILLS: JavaScript, React, Node.js, Express, MongoDB, HTML, CSS, Git"""
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "overall_score": 0.65,
                    "experience_score": 0.70,
                    "skills_score": 0.75,
                    "education_score": 0.60,
                    "projects_score": 0.55,
                    "career_progression_score": 0.60,
                    "cultural_fit_score": 0.70,
                    "strengths": [
                        "Meets minimum 2-year experience requirement",
                        "Good technical skill alignment with React, Node.js",
                        "Career transition shows adaptability and motivation",
                        "Practical experience with full-stack development",
                        "Bootcamp education demonstrates commitment to career change"
                    ],
                    "concerns": [
                        "Limited depth in experience - mostly basic implementations",
                        "No SQL database experience (uses MongoDB only)",
                        "Projects are basic/tutorial-level",
                        "No experience with enterprise-level applications",
                        "Non-technical educational background"
                    ],
                    "missing_skills": [
                        "SQL databases (PostgreSQL, MySQL)",
                        "Advanced React patterns",
                        "System design knowledge",
                        "Testing frameworks"
                    ],
                    "recommendation": "Consider",
                    "reasoning": "Alex meets the basic requirements but shows limited depth. The career transition from marketing to development is positive, showing motivation. However, the experience is quite junior and lacks exposure to enterprise-scale challenges. Could be a good fit if mentoring is available.",
                    "total_experience": "2+ years software development, career transition from marketing",
                    "education_level": "Coding Bootcamp + Bachelor's in Marketing",
                    "key_achievements": [
                        "Successfully transitioned careers to software development",
                        "Built full-stack applications using modern technologies",
                        "Gained practical experience in production environment"
                    ]
                })
            },
            
            # Example 3: Poor Fit Candidate
            {
                "role": "user", 
                "content": """Please evaluate this resume against the job description:

**Job Description:**
Senior Data Scientist - Machine Learning
Seeking a Senior Data Scientist with 5+ years experience in machine learning, Python, SQL, and statistical modeling. Will lead ML initiatives and work with large datasets. Requirements: Python, scikit-learn, TensorFlow/PyTorch, SQL, statistics, 5+ years ML experience.

**Resume:**
John Smith
john@email.com

EXPERIENCE:
Web Developer | DesignCorp | 2019-Present (5 years)
- Built WordPress websites for small businesses
- Customized themes using PHP and CSS
- Basic HTML/JavaScript for frontend work

Freelance Web Designer | 2017-2019 (2 years)
- Created static websites using HTML/CSS
- Used Photoshop for design mockups
- Managed client communications

EDUCATION:
Associate Degree in Graphic Design | Community College | 2017

PROJECTS:
- Portfolio Website: HTML/CSS/JavaScript
- Client Websites: WordPress customizations

SKILLS: HTML, CSS, JavaScript, PHP, WordPress, Photoshop"""
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "overall_score": 0.15,
                    "experience_score": 0.05,
                    "skills_score": 0.10,
                    "education_score": 0.20,
                    "projects_score": 0.15,
                    "career_progression_score": 0.25,
                    "cultural_fit_score": 0.30,
                    "strengths": [
                        "7 years of total technology experience",
                        "Self-directed freelance experience shows initiative",
                        "Web development background provides some technical foundation"
                    ],
                    "concerns": [
                        "Zero machine learning or data science experience",
                        "No Python, statistical modeling, or ML framework experience",
                        "No database or SQL experience",
                        "Educational background completely unrelated",
                        "Skill set is entirely focused on web design/development",
                        "No evidence of analytical or mathematical capabilities"
                    ],
                    "missing_skills": [
                        "Python programming",
                        "Machine learning frameworks (scikit-learn, TensorFlow, PyTorch)",
                        "Statistical analysis and modeling",
                        "SQL and database technologies",
                        "Data manipulation libraries (pandas, numpy)",
                        "Mathematics and statistics background"
                    ],
                    "recommendation": "No Hire",
                    "reasoning": "John's background is entirely in web development/design with no relevant data science or machine learning experience. While he has technical experience, it's in a completely different domain. This would require essentially starting from scratch in a senior-level role, which is not appropriate for the position requirements.",
                    "total_experience": "7 years in web development/design, 0 years in data science/ML",
                    "education_level": "Associate Degree in Graphic Design",
                    "key_achievements": [
                        "Built successful freelance web development business",
                        "7 years of consistent technology work"
                    ]
                })
            }
        ]
    
    def _extract_resume_content(self, resume: Dict) -> str:
        """
        Extract comprehensive resume content for LLM evaluation.
        """
        content_parts = []
        
        # Add parsed structured data if available
        parsed = resume.get('parsed', {})
        if parsed:
            # Basic info
            if parsed.get('name'):
                content_parts.append(f"Name: {parsed['name']}")
            if parsed.get('email'):
                content_parts.append(f"Email: {parsed['email']}")
            if parsed.get('phone'):
                content_parts.append(f"Phone: {parsed['phone']}")
            
            # Experience
            if parsed.get('experience'):
                content_parts.append("\nEXPERIENCE:")
                if isinstance(parsed['experience'], list):
                    for exp in parsed['experience']:
                        content_parts.append(f"- {exp}")
                else:
                    content_parts.append(f"- {parsed['experience']}")
            
            # Education
            if parsed.get('education'):
                content_parts.append("\nEDUCATION:")
                if isinstance(parsed['education'], list):
                    for edu in parsed['education']:
                        content_parts.append(f"- {edu}")
                else:
                    content_parts.append(f"- {parsed['education']}")
            
            # Skills
            if parsed.get('skills'):
                content_parts.append(f"\nSKILLS: {', '.join(parsed['skills'])}")
        
        # Add raw text if structured parsing is insufficient
        preprocessed = resume.get('preprocessed', {})
        if preprocessed.get('cleaned_text'):
            if not content_parts or len('\n'.join(content_parts)) < 200:
                # Use raw text if structured data is minimal
                content_parts = [preprocessed['cleaned_text']]
        
        return '\n'.join(content_parts) if content_parts else "No resume content available"
    
    def _calculate_keyword_score(self, resume_text: str, job_description: str) -> float:
        """
        Calculate simple keyword matching score for the 30% weight component.
        """
        if not resume_text or not job_description:
            return 0.0
        
        resume_words = set(word.lower() for word in resume_text.split() if len(word) > 2)
        job_words = set(word.lower() for word in job_description.split() if len(word) > 2)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
                     'her', 'was', 'one', 'our', 'had', 'with', 'have', 'this', 'will',
                     'his', 'from', 'they', 'she', 'been', 'than', 'has', 'were'}
        
        resume_words = resume_words - stop_words
        job_words = job_words - stop_words
        
        if not job_words:
            return 0.0
        
        common_words = resume_words.intersection(job_words)
        return len(common_words) / len(job_words)


# Global instance for easy import
llm_ranker = LLMBasedRanker()