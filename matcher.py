import re
from dataclasses import dataclass, field
import numpy as np
from sentence_transformers import SentenceTransformer
import config
from services.cache import text_hash, get_embedding, set_embedding

# ── Match Result ──────────────────────────────────────────

@dataclass
class MatchScore:
    semantic_score: float
    keyword_score: float
    hybrid_score: float
    matched_keywords: list[str] = field(default_factory=list)

# ── Model (lazy-loaded singleton) ─────────────────────────

_model = None

def _get_model() -> SentenceTransformer:
    """Load the model once, reuse on every call."""
    global _model
    if _model is None:
        _model = SentenceTransformer(config.MODEL_NAME)
    return _model

# ── Text Cleaning ─────────────────────────────────────────

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "are", "was",
    "will", "have", "has", "been", "from", "they", "you", "your",
    "our", "not", "but", "can", "all", "more", "when", "who",
    # Job-specific stopwords
    "experience", "skills", "knowledge", "responsibilities",
    "ability", "requirements", "must", "preferred", "proficient",
    "understanding", "good", "excellent", "required", "including",
    "work", "working", "role", "team", "years", "strong",
}

def _clean_text(text: str) -> str:
    """Lowercase, remove punctuation, filter short words."""
    text = re.sub(r"[^a-zA-Z0-9\s\+\#]", " ", text.lower())
    words = [w for w in text.split() if len(w) > 2 and w not in STOPWORDS]
    return " ".join(words)

# ── Embedding with Caching ────────────────────────────────

def _embed(text: str) -> np.ndarray:
    """
    Get the embedding for a text, using Redis cache if available.
    Long texts are chunked into ~200-word segments and averaged.
    """
    key = text_hash(text)
    cached = get_embedding(key)
    if cached is not None:
        return cached

    model = _get_model()
    words = text.split()

    if len(words) <= 200:
        embedding = model.encode(text, convert_to_numpy=True)
    else:
        # Chunk into ~200-word segments, embed each, average
        chunks = []
        for i in range(0, len(words), 200):
            chunk = " ".join(words[i : i + 200])
            chunks.append(chunk)
        embeddings = model.encode(chunks, convert_to_numpy=True)
        embedding = np.mean(embeddings, axis=0)

    set_embedding(key, embedding)
    return embedding

# ── Scoring Functions ─────────────────────────────────────

def _semantic_score(resume_text: str, job_text: str) -> float:
    """Cosine similarity between MiniLM embeddings (0.0 to 1.0)."""
    resume_emb = _embed(resume_text)
    job_emb = _embed(job_text)

    similarity = np.dot(resume_emb, job_emb) / (
        np.linalg.norm(resume_emb) * np.linalg.norm(job_emb)
    )

    return float(np.clip(similarity, 0.0, 1.0))

def _keyword_score(resume_text: str, job_text: str) -> tuple[float, list[str]]:
    """Keyword overlap ratio and matched keyword list."""
    resume_clean = _clean_text(resume_text)
    job_clean = _clean_text(job_text)

    resume_words = set(resume_clean.split())
    job_words = set(job_clean.split())

    if not job_words:
        return 0.0, []

    common = sorted(resume_words & job_words)
    score = len(common) / len(job_words)

    return score, common

# ── Public API ────────────────────────────────────────────

def compute_match(
    resume_text: str,
    job_text: str,
    check_education: bool = False,
    education_text: str | None = None,
) -> MatchScore:
    """
    Compute a hybrid match score between a resume and a job description.
    Returns a MatchScore with semantic, keyword, and hybrid scores.
    """
    # Optional education pre-filter (for IBM-style requirements)
    if check_education and education_text:
        edu_keywords = [
            "bachelor", "bachelors", "btech", "b.tech", "bsc", "b.sc",
            "master", "masters", "mtech", "m.tech", "msc", "m.sc",
            "phd", "doctorate",
        ]
        resume_lower = resume_text.lower()
        edu_lower = education_text.lower()

        job_needs_edu = any(kw in edu_lower for kw in edu_keywords)
        resume_has_edu = any(kw in resume_lower for kw in edu_keywords)
        if job_needs_edu and not resume_has_edu:
            return MatchScore(
                semantic_score=0.0,
                keyword_score=0.0,
                hybrid_score=0.0,
                matched_keywords=[],
            )

    sem = _semantic_score(resume_text, job_text)
    kw, matched = _keyword_score(resume_text, job_text)

    hybrid = (config.SEMANTIC_WEIGHT * sem) + (config.KEYWORD_WEIGHT * kw)
    
    return MatchScore(
        semantic_score=round(sem * 100, 2),
        keyword_score=round(kw * 100, 2),
        hybrid_score=round(hybrid * 100, 2),
        matched_keywords=matched,
    )