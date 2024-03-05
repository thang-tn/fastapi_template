"""Structlog configurations."""
import logging
from logging.config import dictConfig
from typing import Any

import structlog
from ddtrace import tracer
from structlog.types import EventDict, Processor


def _init_config():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.NullHandler",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.NullHandler",
                },
            },
            "loggers": {
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": True,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["access"],
                    "propagate": True,
                },
            },
        },
    )


def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """Drop duplicated color message.

    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def _tracer_injection(_, __, event_dict: EventDict) -> EventDict:
    """Add Datadog `span_id` and `trace_id`."""
    # get correlation ids from current tracer context
    span = tracer.current_span()
    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

    # add ids to structlog event dictionary
    event_dict["dd.trace_id"] = str(trace_id or 0)
    event_dict["dd.span_id"] = str(span_id or 0)

    return event_dict


def _remove_processors_meta(_, __, event_dict: EventDict) -> EventDict:
    """Override structlog.Processors.remove_processors_meta."""
    if "_record" in event_dict:
        del event_dict["_record"]

    if "_from_structlog" in event_dict:
        del event_dict["_from_structlog"]

    return event_dict


def _get_shared_processors(*, enable_json: bool = False) -> list[Processor]:
    """Get shared processors.

    Parameters
    ----------
    enable_json : bool, optional
        is json logging enabled?, by default False
    """
    if enable_json:
        return [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.THREAD,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.PROCESS_NAME,
                },
            ),
            structlog.stdlib.ExtraAdder(),
            _drop_color_message_key,
            _tracer_injection,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
            # `message` key but the pretty ConsoleRenderer looks for `event`
            structlog.processors.EventRenamer(to="message"),
            # Format the exception only for JSON logs, as we want to pretty-print them when
            # using the ConsoleRenderer
            structlog.processors.format_exc_info,
        ]

    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        _drop_color_message_key,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]


def configure_logging(*, debug: bool = False, enable_json: bool = False):
    """Configure logging.

    Parameters
    ----------
    debug : bool, optional
        is debug mode enabled ?, by default False
    enable_json : bool, optional
        is json log enabled ?, by default False
    """
    _init_config()

    shared_processors: list[Processor] = _get_shared_processors(enable_json=enable_json)

    structlog.configure(
        # Prepare event dict for `ProcessorFormatter`.
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: Any = structlog.processors.JSONRenderer() if enable_json else structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            _remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logging.getLogger("celery.bootsteps").setLevel(logging.WARNING)
    logging.getLogger("ddtrace.internal.processor").setLevel(logging.WARNING)
    logging.getLogger("kombu").setLevel(logging.WARNING)

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True
