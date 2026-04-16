# import re
# from dataclasses import dataclass, field
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import config
# from services.cache import text_hash, get_embedding, set_embedding

from dataclasses import dataclass, field
from services.llm import call_llm_json

# ── Match Result ──────────────────────────────────────────

# @dataclass
# class MatchScore:
#     semantic_score: float
#     keyword_score: float
#     hybrid_score: float
#     matched_keywords: list[str] = field(default_factory=list)

@dataclass
class MatchScore:
    overall_score: float
    skills_score: float
    experience_score: float
    reasoning: str
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)

# ── Model (lazy-loaded singleton) ─────────────────────────

# _model = None

# def _get_model() -> SentenceTransformer:
#     """Load the model once, reuse on every call."""
#     global _model
#     if _model is None:
#         _model = SentenceTransformer(config.MODEL_NAME)
#     return _model

# # ── Text Cleaning ─────────────────────────────────────────

# STOPWORDS = {
#     "the", "and", "for", "with", "that", "this", "are", "was",
#     "will", "have", "has", "been", "from", "they", "you", "your",
#     "our", "not", "but", "can", "all", "more", "when", "who",
#     # Job-specific stopwords
#     "experience", "skills", "knowledge", "responsibilities",
#     "ability", "requirements", "must", "preferred", "proficient",
#     "understanding", "good", "excellent", "required", "including",
#     "work", "working", "role", "team", "years", "strong",
# }

# def _clean_text(text: str) -> str:
#     """Lowercase, remove punctuation, filter short words."""
#     text = re.sub(r"[^a-zA-Z0-9\s\+\#]", " ", text.lower())
#     words = [w for w in text.split() if len(w) > 2 and w not in STOPWORDS]
#     return " ".join(words)

# # ── Embedding with Caching ────────────────────────────────

# def _embed(text: str) -> np.ndarray:
#     """
#     Get the embedding for a text, using Redis cache if available.
#     Long texts are chunked into ~200-word segments and averaged.
#     """
#     key = text_hash(text)
#     cached = get_embedding(key)
#     if cached is not None:
#         return cached

#     model = _get_model()
#     words = text.split()

#     if len(words) <= 200:
#         embedding = model.encode(text, convert_to_numpy=True)
#     else:
#         # Chunk into ~200-word segments, embed each, average
#         chunks = []
#         for i in range(0, len(words), 200):
#             chunk = " ".join(words[i : i + 200])
#             chunks.append(chunk)
#         embeddings = model.encode(chunks, convert_to_numpy=True)
#         embedding = np.mean(embeddings, axis=0)

#     set_embedding(key, embedding)
#     return embedding

# # ── Scoring Functions ─────────────────────────────────────

# def _semantic_score(resume_text: str, job_text: str) -> float:
#     """Cosine similarity between MiniLM embeddings (0.0 to 1.0)."""
#     resume_emb = _embed(resume_text)
#     job_emb = _embed(job_text)

#     similarity = np.dot(resume_emb, job_emb) / (
#         np.linalg.norm(resume_emb) * np.linalg.norm(job_emb)
#     )

#     return float(np.clip(similarity, 0.0, 1.0))

# def _keyword_score(resume_text: str, job_text: str) -> tuple[float, list[str]]:
#     """Keyword overlap ratio and matched keyword list."""
#     resume_clean = _clean_text(resume_text)
#     job_clean = _clean_text(job_text)

#     resume_words = set(resume_clean.split())
#     job_words = set(job_clean.split())

#     if not job_words:
#         return 0.0, []

#     common = sorted(resume_words & job_words)
#     score = len(common) / len(job_words)

#     return score, common

# ── Public API ────────────────────────────────────────────

# def compute_match(
#     resume_text: str,
#     job_text: str,
#     check_education: bool = False,
#     education_text: str | None = None,
# ) -> MatchScore:
#     """
#     Compute a hybrid match score between a resume and a job description.
#     Returns a MatchScore with semantic, keyword, and hybrid scores.
#     """
#     # Optional education pre-filter (for IBM-style requirements)
#     if check_education and education_text:
#         edu_keywords = [
#             "bachelor", "bachelors", "btech", "b.tech", "bsc", "b.sc",
#             "master", "masters", "mtech", "m.tech", "msc", "m.sc",
#             "phd", "doctorate",
#         ]
#         resume_lower = resume_text.lower()
#         edu_lower = education_text.lower()

#         job_needs_edu = any(kw in edu_lower for kw in edu_keywords)
#         resume_has_edu = any(kw in resume_lower for kw in edu_keywords)
#         if job_needs_edu and not resume_has_edu:
#             return MatchScore(
#                 semantic_score=0.0,
#                 keyword_score=0.0,
#                 hybrid_score=0.0,
#                 matched_keywords=[],
#             )

#     sem = _semantic_score(resume_text, job_text)
#     kw, matched = _keyword_score(resume_text, job_text)

#     hybrid = (config.SEMANTIC_WEIGHT * sem) + (config.KEYWORD_WEIGHT * kw)
    
#     return MatchScore(
#         semantic_score=round(sem * 100, 2),
#         keyword_score=round(kw * 100, 2),
#         hybrid_score=round(hybrid * 100, 2),
#         matched_keywords=matched,
#     )

@dataclass
class MatchScore:
    overall_score: float
    skills_score: float
    experience_score: float
    reasoning: str
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)


def compute_match(resume_text: str, job_text: str) -> MatchScore:
    """
    Use LLM to extract skills/experience and compute scores via fixed formula.
    """
    prompt = f"""You are a job matching expert. Your job is to extract and compare skills/experience between a resume and a job description, then compute scores using the EXACT formulas below.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_text[:2000]}

STEPS:
1. Extract all required skills/technologies from the JOB DESCRIPTION → call this "required_skills" (list)
2. Extract all skills/technologies from the RESUME → call this "resume_skills" (list)
3. Find the intersection → "matched_skills"
   - Use SEMANTIC matching: treat equivalent terms as the same skill.
     Examples: "React.js" = "React", "RESTful API" = "Web Services", "PostgreSQL" = "Postgres", "ML" = "Machine Learning"
4. Find required skills NOT in resume → "missing_skills"
5. Extract years of relevant experience from RESUME → "resume_exp_years" (integer)
   - If experience is not explicitly stated, estimate based on the earliest employment/project date provided.
   - If no dates exist at all, set to 0.
6. Extract required years of experience from JOB DESCRIPTION → "required_exp_years" (integer, 0 if not stated)

SCORING FORMULAS (use these exactly):
- skills_score = (len(matched_skills) / max(len(required_skills), 1)) * 100
- experience_score = min(resume_exp_years / max(required_exp_years, 1), 1.0) * 100
- overall_score = (0.6 * skills_score) + (0.4 * experience_score)

Round all scores to 1 decimal place.

Return ONLY valid JSON:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "skills_score": 0.0,
  "experience_score": 0.0,
  "overall_score": 0.0,
  "reasoning": "2-3 sentence explanation"
}}"""

    try:
        result = call_llm_json(prompt)
    except Exception as e:
        print(f"LLM matching failed: {e}")
        return MatchScore(
            overall_score=0.0,
            skills_score=0.0,
            experience_score=0.0,
            reasoning="LLM matching failed.",
        )

    return MatchScore(
        overall_score=result.get("overall_score", 0.0),
        skills_score=result.get("skills_score", 0.0),
        experience_score=result.get("experience_score", 0.0),
        reasoning=result.get("reasoning", ""),
        matched_skills=result.get("matched_skills", []),
        missing_skills=result.get("missing_skills", []),
    )