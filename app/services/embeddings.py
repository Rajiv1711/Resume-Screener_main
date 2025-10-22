from typing import List, Dict
from openai import AzureOpenAI
from app.config import (
    OPENAI_EMBEDDING_API_KEY,
    OPENAI_EMBEDDING_ENDPOINT,
    OPENAI_EMBEDDING_API_VERSION,
    OPENAI_EMBEDDING_DEPLOYMENT,
)

# Configure Azure OpenAI (Embeddings)
if not OPENAI_EMBEDDING_API_KEY or not OPENAI_EMBEDDING_ENDPOINT:
    raise RuntimeError("Azure OpenAI embedding credentials not configured: set AZURE_OPENAI_EMBEDDING_API_KEY and AZURE_OPENAI_EMBEDDING_ENDPOINT (or AZURE_OPENAI_API_KEY/ENDPOINT)")
client = AzureOpenAI(
    api_key=OPENAI_EMBEDDING_API_KEY,
    api_version=OPENAI_EMBEDDING_API_VERSION,
    azure_endpoint=OPENAI_EMBEDDING_ENDPOINT,
)


def get_text_embedding(text: str, model: str = OPENAI_EMBEDDING_DEPLOYMENT) -> List[float]:
    """
    Generate embedding for a given text using Azure OpenAI embeddings.
    """
    if not text or len(text.strip()) == 0:
        return []

    response = client.embeddings.create(
        input=text,
        model=model  # Azure deployment name for embeddings
    )

    embedding_vector = response.data[0].embedding
    return embedding_vector


def generate_resume_embedding(preprocessed_data: Dict) -> Dict:
    """
    Generate embeddings for preprocessed resume data.
    Uses the cleaned_text field as input for semantic representation.
    """
    cleaned_text = preprocessed_data.get("cleaned_text", "")
    skills = " ".join(preprocessed_data.get("skills", []))

    # Combine cleaned text + skills to improve embedding quality
    combined_text = f"{cleaned_text}\nSkills: {skills}"

    embedding = get_text_embedding(combined_text)
    return {
        "text": combined_text,
        "embedding": embedding,
        "vector_length": len(embedding)
    }
