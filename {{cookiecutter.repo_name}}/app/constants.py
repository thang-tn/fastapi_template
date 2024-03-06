"""Defined constants."""
from pathlib import Path

# Project Base directory path
BASE_DIR: Path = Path(__file__).parent
# Celery queue
CELERY_QUEUE = "sample_queue"
