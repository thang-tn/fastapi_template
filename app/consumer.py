"""Consumer kafka command."""
import asyncio
import signal

import structlog
from ddtrace import tracer

from app.core.config import KafkaSettings, get_settings
from app.services.kafka import KafkaService
from app.utils.sentry import capture_exception
from app.utils.structlog import configure_logging
from app.utils.trace import path_kafka_trace

settings: KafkaSettings = get_settings("consumer")
logger = structlog.stdlib.get_logger("aiokafka.consumer.group_coordinator")


async def main() -> None:
    """Kafka service."""
    with tracer.trace("kafka.consume", service=settings.dd_service):
        path_kafka_trace()
        shutdown_event = asyncio.Event()
        kafka_service = KafkaService(kafka_settings=settings)

        loop = asyncio.get_event_loop()

        signal_handler_task = loop.create_task(shutdown_signal_handler(shutdown_event))
        consumer_task = loop.create_task(kafka_service.consume(shutdown_event))

        await asyncio.wait([signal_handler_task, consumer_task], return_when=asyncio.FIRST_COMPLETED)

        # Cancel the consumer task if it's still running
        if not consumer_task.done():
            consumer_task.cancel()
            try:
                await consumer_task  # Ensure the task has a chance to clean up
            except asyncio.CancelledError:
                logger.info("Consumer task cancelled during shutdown.")

        # Cancel the signal handler task if it's still running
        if not signal_handler_task.done():
            signal_handler_task.cancel()


async def shutdown_signal_handler(shutdown_event):
    """Shutdown signal handler."""
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_event.set)

    await shutdown_event.wait()
    logger.info("Shutdown signal received.")


if __name__ == "__main__":
    configure_logging(debug=False, enable_json=True)
    try:
        asyncio.run(main())
    except Exception as ex:  # noqa:  BLE001
        capture_exception(ex)
