"""Sentry service."""
import traceback
import types

import sentry_sdk
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

from app.core.config import SentrySettings, get_settings

DENY_LIST = [
    *DEFAULT_DENYLIST,
    "document_html",
    "document_url",
]
sentry_settings: SentrySettings = get_settings("sentry")


class SentryService:
    """Sentry service for handling and reporting errors."""

    _instance: object = None

    def __new__(cls):
        """Create instance for service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def initialize():
        """Initialize the Sentry client."""
        sentry_sdk.init(
            dsn=sentry_settings.sentry_dsn,
            send_default_pii=False,
            traces_sample_rate=sentry_settings.sentry_traces_sample_rate,
            environment=sentry_settings.sentry_environment,
            before_send=SentryService._before_send,
            event_scrubber=EventScrubber(denylist=DENY_LIST),
        )

    @staticmethod
    def capture_exception(exception):
        """Capture and report an exception to sentry_settings."""
        if sentry_sdk.Hub.current.client:
            if isinstance(exception, str):
                sentry_sdk.capture_message(exception)
            elif isinstance(exception, types.TracebackType):
                traceback_str = traceback.format_exc()
                sentry_sdk.capture_message(traceback_str)
            else:
                sentry_sdk.capture_exception(exception)

    @staticmethod
    def _before_send(event, _):
        """Filter Sentry event before sending."""
        if "logger" in event:
            return None

        if "extra" in event:
            SentryService._scrub_sensitive_data(event["extra"], DENY_LIST)

        if "exception" in event:
            for exception in event["exception"]["values"]:
                SentryService._scrub_exception(exception)

        return event

    @staticmethod
    def _scrub_sensitive_data(data, fields_to_scrub):
        """Strip out sensitive data from the given dictionary."""
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key in fields_to_scrub:
                    data[key] = "[REDACTED]"
                else:
                    SentryService._scrub_sensitive_data(data[key], fields_to_scrub)
        elif isinstance(data, list):
            for item in data:
                SentryService._scrub_sensitive_data(item, fields_to_scrub)

    @staticmethod
    def _scrub_exception(exception):
        """Scrub sensitive data from exception messages and stack traces."""
        if "stacktrace" in exception:
            for frame in exception["stacktrace"]["frames"]:
                if "vars" in frame:
                    SentryService._scrub_sensitive_data(frame["vars"], DENY_LIST)
