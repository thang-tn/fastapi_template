"""Consumer kafka command."""
import asyncio
import logging
import signal

from ddtrace import tracer

from app.config import ConsumerSettings, get_settings
from app.services.kafka import KafkaService
from app.utils.logging import KafkaLogFilter
from app.utils.sentry import capture_exception
from app.utils.trace import path_kafka_trace

settings: ConsumerSettings = get_settings("consumer")  # type: ignore[assignment]
logger = logging.getLogger("aiokafka.consumer.group_coordinator")
logger.addFilter(KafkaLogFilter([logging.DEBUG, logging.CRITICAL, logging.ERROR]))


async def main() -> None:
    """Kafka service."""
    with tracer.trace("kafka.consume", service=settings.dd_service):
        path_kafka_trace()
        shutdown_event = asyncio.Event()
        kafka_service = KafkaService(kafka_settings=settings.kafka)

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
                print("Consumer task cancelled during shutdown.")  # noqa:  T201

        # Cancel the signal handler task if it's still running
        if not signal_handler_task.done():
            signal_handler_task.cancel()


async def shutdown_signal_handler(shutdown_event):
    """Shutdown signal handler."""
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_event.set)

    await shutdown_event.wait()
    print("Shutdown signal received.")  # noqa:  T201


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as ex:  # noqa:  BLE001
        capture_exception(ex)
