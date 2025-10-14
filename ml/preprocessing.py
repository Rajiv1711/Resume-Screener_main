import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from typing import List

# Download required NLTK data (will skip if already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize NLTK components
lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words('english'))

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
    tokens = word_tokenize(text)
    tokens = [
        lemmatizer.lemmatize(token.lower()) for token in tokens 
        if token.isalpha() and token.lower() not in STOPWORDS
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
