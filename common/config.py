import os
from pathlib import Path

# Base directories (if needed for the backend)
BASE_DIR = Path(__file__).parent.parent

# Database URL – read from environment or use default for local development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nbadb")

# API settings (for the backend)
API_TITLE = "NBA Analytics API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "REST API for NBA player impact scores, talent, badges, and similar seasons."

# Pagination defaults
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# Cache settings (if Redis is added later)
CACHE_TTL_SECONDS = 3600  # 1 hour