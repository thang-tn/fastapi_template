"""Simple task."""
import logging

from celery import shared_task

from app.constants import CELERY_QUEUE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@shared_task(queue=CELERY_QUEUE)
def simple_task(data):
    """Return Simple task."""
    logger.debug("Receiving data: %s", data)
