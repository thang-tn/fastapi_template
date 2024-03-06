"""Sentry helper."""
import contextlib

from app.services.sentry import SentryService


def capture_exception(exception):
    """Capture error helper."""
    sentry_sdk = SentryService()
    with contextlib.suppress(Exception):
        sentry_sdk.initialize()
    sentry_sdk.capture_exception(exception)
