from pydantic import BaseSettings

class Settings(BaseSettings):
    # Dedupe Hub
    dedupe_hub_live: bool
    dedupe_hub_name: str
    dedupe_hub_version: str
    # Kafka config
    bootstrap_servers: str
    security_protocol: str
    consumer_group_id: str
    consumer_client_id: str
    topic_dedupe_basic_name: str
    # Environment
    env: str
    instance_source: str = "os_hub"
    # Rollbar SS AT
    rollbar_server_side_access_token: str
    # Postgres
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    # Git
    git_commit: str

settings = Settings()