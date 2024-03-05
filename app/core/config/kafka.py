from pydantic_settings import BaseSettings  # noqa: D100


class KafkaSettings(BaseSettings):
    """Kafka settings for the application."""

    brokers_tls: str
    group_id: str | None = None
    security_protocol: str = "PLAINTEXT"
    mechanism: str = ""
    username: str = ""
    password: str = ""
    cert_file: str = ""
    cert_key_file: str = ""
    consumer_timeout: str = "60000"
    auto_commit_interval_ms: str = "1000"
    max_poll_records: str = "100"
    session_time_out_ms: str = "600000"
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
        return self.brokers_tls.split(",")
