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