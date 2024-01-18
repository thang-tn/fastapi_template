"""Kafka Service."""
import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from aiokafka.structs import ConsumerRecord
from celery import Task  # noqa: TCH002
from sentry_sdk import capture_exception

from app.config.kafka import KafkaSettings
from app.tasks.simple_task import simple_task

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class KafkaService:
    """Kafka Service."""

    handlers = {  # noqa: RUF012
        "Sample.Topic": simple_task,
    }

    def __init__(self, kafka_settings: KafkaSettings) -> None:
        self.settings = kafka_settings
        self.default_configs = dict(
            bootstrap_servers=kafka_settings.bootstrap_servers,
            ssl_context=create_ssl_context(),
            security_protocol=kafka_settings.security_protocol,
            sasl_plain_username=kafka_settings.username,
            sasl_plain_password=kafka_settings.password,
            sasl_mechanism=kafka_settings.mechanism,
        )

    @property
    def subscribed_topics(self):
        """Get subscribed topics."""
        return self.handlers.keys()

    @property
    def consumer_configs(self) -> dict:
        """
        Returning kafka consumer configurations.

        Returns
        -------
        dict
            Kafka consumer configurations data.
        """
        # ruff: noqa: C408
        extra_configs = dict(
            group_id=self.settings.group_id,
            consumer_timeout_ms=int(self.settings.consumer_timeout),
            auto_commit_interval_ms=int(self.settings.auto_commit_interval_ms),
            max_poll_records=int(self.settings.max_poll_records),
            session_timeout_ms=int(self.settings.session_time_out_ms),
        )

        return {
            **self.default_configs,
            **extra_configs,
        }

    async def consume(self, shutdown_event: asyncio.Event) -> None:
        """Kafka service consume message."""
        topics = self.subscribed_topics
        consumer = AIOKafkaConsumer(
            *topics,
            **self.consumer_configs,
        )
        await consumer.start()
        logger.debug("Starting consuming messages from topics %s", topics)
        try:
            while not shutdown_event.is_set():
                msg = await consumer.getone()
                logger.debug(
                    f"Consumed message from topic {msg.topic}: "
                    f"partition {msg.partition} offset {msg.offset} key {msg.key} "
                    f"value {msg.value} timestamp {msg.timestamp}"
                )
                self._process_message(msg)
        except Exception as ex:
            logger.exception("Error while consuming topic %s", topics)
            capture_exception(ex)
        finally:
            logger.debug("Stopping consumer for topic %s", topics)
            await consumer.stop()

    def _process_message(self, msg: ConsumerRecord):
        """Process a consumed message."""
        handler: Task = self.handlers.get(msg.topic)
        if not handler:
            raise ValueError(f"Handler not found for topic {msg.topic}")
        handler.delay(msg.value)

    async def send_message(self, producer_service):
        """Send message to Kafka by producer."""
        producer = AIOKafkaProducer(**self.default_configs)
        try:
            await producer.start()

            logger.debug("Starting to produce message on topic %s", producer_service.topic())
            await producer.send_and_wait(
                topic=producer_service.topic(),
                value=json.dumps(producer_service.message()).encode("utf-8"),
                key=producer_service.key().encode("utf-8"),
            )
            logger.debug("Sent message to topic %s", producer_service.topic())
        except Exception as ex:
            logger.exception("Sent message fail to topic %s", producer_service.topic())
            capture_exception(ex)
        finally:
            await producer.stop()
