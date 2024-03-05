"""Kafka Service."""
import asyncio
import json
import logging
from collections.abc import Mapping
from types import MappingProxyType

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from aiokafka.structs import ConsumerRecord
from celery import Task
from sentry_sdk import capture_exception

from app.core.config.kafka import KafkaSettings
from app.tasks import simple_task

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class KafkaService:
    """Kafka Service."""

    handlers: Mapping[str, Task] = MappingProxyType(
        {
            "Sample.Topic": simple_task,
        },
    )

    def __init__(self, kafka_settings: KafkaSettings | None) -> None:
        self.settings = kafka_settings

    @property
    def subscribed_topics(self):
        """Get subscribed topics."""
        return self.handlers.keys()

    @property
    def default_configs(self):
        """Return kafka default configurations.

        Returns
        -------
        dict
            Kafka consumer configurations data.
        """
        if not self.settings:
            return {}

        return {
            "bootstrap_servers": self.settings.bootstrap_servers,
            "ssl_context": create_ssl_context(),
            "security_protocol": self.settings.security_protocol,
            "sasl_plain_username": self.settings.username,
            "sasl_plain_password": self.settings.password,
            "sasl_mechanism": self.settings.mechanism,
        }

    @property
    def consumer_configs(self) -> dict:
        """
        Returning kafka consumer configurations.

        Returns
        -------
        dict
            Kafka consumer configurations data.
        """
        if not self.settings:
            return {}

        extra_configs = {
            "group_id": self.settings.group_id,
            "consumer_timeout_ms": int(self.settings.consumer_timeout),
            "auto_commit_interval_ms": int(self.settings.auto_commit_interval_ms),
            "max_poll_records": int(self.settings.max_poll_records),
            "session_timeout_ms": int(self.settings.session_time_out_ms),
        }

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
                    "Consumed message from topic %s: partition %s offset %s key %s value %s timestamp %s",
                    msg.topic,
                    msg.partition,
                    msg.offset,
                    msg.key,
                    msg.value,
                    msg.timestamp,
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

    async def produce_message(self, topic: str, msg_data: dict, key: str):
        """
        Produce message to Kafka.

        Parameters
        ----------
        topic : str
            kafka topic to produce the message to
        msg_data : dict
            content data
        key : str
            unique key
        """
        producer = AIOKafkaProducer(**self.default_configs)
        try:
            await producer.start()

            logger.debug("Starting to produce message on topic %s", topic)
            await producer.send_and_wait(
                topic=topic,
                value=json.dumps(msg_data).encode("utf-8"),
                key=key.encode("utf-8"),
            )
            logger.debug("Sent message to topic %s", topic)
        except Exception as ex:
            logger.exception("Sent message fail to topic %s", topic)
            capture_exception(ex)
        finally:
            await producer.stop()
