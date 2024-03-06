"""Kafka configurations."""
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    """Kafka settings for the application."""

    environment: str = "development"
    kafka_brokers_tls: str
    kafka_group_id: str | None = None
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_mechanism: str = ""
    kafka_username: str = ""
    kafka_password: str = ""
    kafka_cert_file: str = ""
    kafka_cert_key_file: str = ""
    kafka_consumer_timeout: str = "60000"
    kafka_auto_commit_interval_ms: str = "1000"
    kafka_max_poll_records: str = "100"
    kafka_session_time_out_ms: str = "600000"
    dd_service: str = ""

    @property
    def bootstrap_servers(self) -> list[str]:
        """
        Return list of bootstrap servers.

        Returns
        -------
        list[str]
            List of string containing bootstrap server hosts.
        """
        return self.kafka_brokers_tls.split(",")
