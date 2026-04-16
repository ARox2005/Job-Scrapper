import os
from dotenv import load_dotenv

load_dotenv()

# Database -----------------------------------------------------------------------
DATABASE = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/jobscrapper"
)

# Redis --------------------------------------------------------------------------
REDIS = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Matcher ------------------------------------------------------------------------
MODEL_NAME = "all-MiniLM-L6-v2"
SEMANTIC_WEIGHT = 0.6
KEYWORD_WEIGHT = 0.4

# Jobs ---------------------------------------------------------------------------
JOB_RETENTION_DAYS = 7

# Celery -------------------------------------------------------------------------
CELERY_BROKER_URL = REDIS
CELERY_RESULT_BACKEND = REDIS

# LLM ---------------------------------------------------------------------------
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
LLM_ENDPOINT = os.getenv(
    "LLM_ENDPOINT",
    "https://integrate.api.nvidia.com/v1/chat/completions"
)