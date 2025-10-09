import openai
from typing import List, Dict

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_key = "CYAwdpz6QRguMec53YUv1imw8Asf1s97jz1HwpuCUNPIsylrqkwnJQQJ99BJAC77bzfXJ3w3AAABACOGZ5GD"
openai.api_base = "https://embedderresume.openai.azure.com/"
openai.api_version = "2024-12-01-preview"


def get_text_embedding(text: str, model: str = "text-embedding-3-large") -> List[float]:
    """
    Generate embedding for a given text using Azure OpenAI embeddings.
    """
    if not text or len(text.strip()) == 0:
        return []

    response = openai.Embedding.create(
        input=text,
        engine=model  # use the name of your Azure deployment
    )

    embedding_vector = response["data"][0]["embedding"]
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
