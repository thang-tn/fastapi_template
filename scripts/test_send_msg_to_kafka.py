import asyncio
import uuid

from app.core.config import KafkaSettings, get_settings
from app.services.kafka import KafkaService

settings: KafkaSettings = get_settings("kafka")


async def main(message_data):
    msg_id = str(uuid.uuid4())
    kafka_svc = KafkaService(kafka_settings=settings)
    await kafka_svc.produce_message(
        topic="Sample.Topic",
        msg_data=message_data,
        key=msg_id,
    )


if __name__ == "__main__":
    message_data = "Test sending message to celery"
    asyncio.run(main(message_data))
