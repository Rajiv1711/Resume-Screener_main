import re
import spacy
from typing import List

# Load spaCy model for English
nlp = spacy.load("en_core_web_sm")

# Optional: Define custom stopwords
STOPWORDS = nlp.Defaults.stop_words

def clean_text(text: str) -> str:
    """
    Basic cleaning: lowercasing, removing special chars, numbers.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # keep only letters
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_lemmatize(text: str) -> List[str]:
    """
    Tokenize, remove stopwords, and lemmatize words.
    """
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc 
        if token.is_alpha and token.text not in STOPWORDS
    ]
    return tokens


def extract_skills(tokens: List[str]) -> List[str]:
    """
    Extract skills from tokens using a predefined skills list.
    (This can later be replaced or enhanced with GPT-based skill extraction.)
    """
    predefined_skills = {
        "python", "java", "c++", "c", "javascript", "typescript",
        "sql", "mysql", "mongodb", "html", "css", "react", "angular",
        "nodejs", "flask", "django", "fastapi",
        "machine learning", "deep learning", "nlp",
        "azure", "aws", "gcp", "docker", "kubernetes",
        "git", "jira", "linux"
    }

    extracted = [tok for tok in tokens if tok in predefined_skills]
    return list(set(extracted))  # unique skills


def preprocess_resume_text(text: str) -> dict:
    """
    Full preprocessing pipeline.
    Returns cleaned tokens + extracted skills.
    """
    cleaned = clean_text(text)
    tokens = tokenize_and_lemmatize(cleaned)
    skills = extract_skills(tokens)

    return {
        "cleaned_text": cleaned,
        "tokens": tokens,
        "skills": skills
    }
