from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class TgBot:
    token: str
    admins_ids: list[int]
    use_redis: bool

    @staticmethod
    def load_from_env(env: Env):
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMIN_IDS")))
        use_redis = env.bool("USE_REDIS")

        return TgBot(token=token, admins_ids=admin_ids, use_redis=use_redis)


@dataclass
class DbConfig:
    password: str
    user: str
    database: str
    host: str
    port: int = 5432

    def create_uri(
        self, driver: str = "asyncpg", host: str = None, port: int = None
    ) -> str:
        if not host:
            host = self.host
        if not port:
            port = self.port

        uri = f"postgresql+{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

        return uri

    @staticmethod
    def load_from_env(env: Env):
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)

        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class RedisConfig:
    host: Optional[str]
    password: Optional[str]
    port: Optional[int]
    database: Optional[int]

    def create_uri(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"

    @staticmethod
    def load_from_env(env: Env):
        password = env.str("REDIS_PASSWORD")
        port = env.int("REDIS_PORT")
        host = env.str("REDIS_HOST")
        database = env.int("REDIS_DB")

        return RedisConfig(
            password=password,
            port=port,
            host=host,
            database=database,
        )


@dataclass
class Config:
    tg_bot: TgBot
    db: Optional[DbConfig]
    redis: Optional[RedisConfig] = None


def _get_environment(path: str | None = None) -> Env:
    env: Env = Env()
    env.read_env(path=path)

    return env


def load_config(path: str | None) -> Config:
    env = _get_environment(path)

    config = Config(
        tg_bot=TgBot.load_from_env(env),
        redis=RedisConfig.load_from_env(env),
        db=DbConfig.load_from_env(env),
    )

    return config
