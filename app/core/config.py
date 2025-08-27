from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # logging configuration
    logger_log_dir: str = "logs"
    logger_filename: str = "app.log"

    # authentication configuration
    token_secret_key: str = ""
    token_algorithm: str = "HS256"
    token_expire_minutes: int = 30

    # database configuration
    db_username: str = ""
    db_password: str = ""
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""

    # pgadmin configuration
    pgadmin_default_email: EmailStr = "fast@api.com"
    pgadmin_default_password: str = ""

    allowed_types: list = []
    max_file_size: int = 5

    # storage type: local or cloud
    storage_backend: str = ""

    # aws environment variables
    aws_s3_bucket_name: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
