from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=None)

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    admin_email: EmailStr
    admin_password: str

    secret_key: str

    jwt_algorithm: str
    access_token_expire_minutes: int

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()

