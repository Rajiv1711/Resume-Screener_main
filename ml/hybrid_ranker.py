import math
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine


class TfidfHybridScorer:
    """Compute TF-IDF similarities and return normalized scores.

    This class builds an in-memory TF-IDF matrix for resumes plus the
    job description and computes cosine similarity. Designed for a single
    ranking call at a time (no persistence/state across calls).
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=20000,
            ngram_range=(1, 2),
            stop_words="english",
            lowercase=True,
        )

    def score(self, resumes_clean_text: List[str], job_description: str) -> List[float]:
        """Return TF-IDF cosine similarity scores resume->JD.

        Args:
            resumes_clean_text: list of cleaned resume texts
            job_description: raw JD text (will be normalized by vectorizer)

        Returns:
            A list of floats (len == number of resumes)
        """
        if not resumes_clean_text:
            return []

        corpus = resumes_clean_text + [job_description]
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # Last row is JD
        jd_vec = tfidf_matrix[-1]
        res_mat = tfidf_matrix[:-1]

        sims = sk_cosine(res_mat, jd_vec)
        # sims is shape (n_resumes, 1); flatten and clamp to [0,1]
        scores = [float(max(0.0, min(1.0, s))) for s in sims.ravel()]
        return scores


def combine_hybrid_scores(embedding_scores: List[float], tfidf_scores: List[float], alpha: float = 0.7) -> List[float]:
    """Linearly combine normalized scores: alpha*embed + (1-alpha)*tfidf.

    Assumes both lists are same length and scores already in [0,1].
    """
    if len(embedding_scores) != len(tfidf_scores):
        raise ValueError("Score lists must have same length")
    beta = 1.0 - alpha
    return [alpha * e + beta * t for e, t in zip(embedding_scores, tfidf_scores)]


