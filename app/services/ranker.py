import numpy as np
from typing import List, Dict
from app.services.embeddings import generate_resume_embedding, get_text_embedding
from ml.hybrid_ranker import TfidfHybridScorer, combine_hybrid_scores


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    """
    if not vec1 or not vec2:
        return 0.0
    v1, v2 = np.array(vec1), np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def rank_resumes(resume_list: List[Dict], job_description: str, alpha: float = 0.7) -> List[Dict]:
    """
    Rank resumes using hybrid scoring: alpha*embedding + (1-alpha)*TF-IDF.
    Each resume is expected to contain preprocessed text.
    """

    # Step 1: Generate embedding for job description
    job_embedding = get_text_embedding(job_description)

    ranked_results = []

    # Prepare TF-IDF scorer inputs
    tfidf = TfidfHybridScorer()
    resumes_clean_text: List[str] = []
    preprocessed_cache: List[Dict] = []

    for resume in resume_list:
        try:
            # Step 2: Generate embedding for each resume
            preprocessed = resume.get("preprocessed", {})
            embedding_data = generate_resume_embedding(preprocessed)
            resume_embedding = embedding_data["embedding"]

            # Step 3: Compute similarity score
            score = cosine_similarity(job_embedding, resume_embedding)

            # Collect TF-IDF inputs
            resumes_clean_text.append(preprocessed.get("cleaned_text", ""))
            preprocessed_cache.append(preprocessed)

            # Step 4: Collect ranked data
            ranked_results.append({
                "file": resume.get("file"),
                "embedding_score": round(score, 4),
                "skills": preprocessed.get("skills", []),
                "parsed": resume.get("parsed", {}),
            })
        except Exception as e:
            ranked_results.append({
                "file": resume.get("file"),
                "error": str(e)
            })

    # Step 4b: Compute TF-IDF scores for all resumes in one shot
    try:
        tfidf_scores = tfidf.score(resumes_clean_text, job_description)
    except Exception:
        tfidf_scores = [0.0 for _ in ranked_results]

    # Normalize embedding scores to [0,1] for fair combination
    embed_scores = [max(0.0, min(1.0, (r.get("embedding_score", 0.0) + 1.0) / 2.0)) for r in ranked_results]
    # Combine
    hybrid_scores = combine_hybrid_scores(embed_scores, tfidf_scores, alpha=alpha)

    for r, h, t in zip(ranked_results, hybrid_scores, tfidf_scores):
        r["tfidf_score"] = round(float(t), 4)
        r["hybrid_score"] = round(float(h), 4)

    # Step 5: Sort results in descending order by hybrid_score
    ranked_results.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
    return ranked_results
