from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    REF_ID: str = '1jwII9PnSOUKmhnIx'

    USE_RANDOM_DELAY_IN_RUN: bool = False
    RANDOM_DELAY_IN_RUN: list[int] = [3, 29800]
    SLEEP_BETWEEN_CLAIM: tuple[int, int] = (360, 540)

    CLAIM_RETRY: int = 1

    AUTO_UPGRADE_FARM: bool = True
    MAX_UPGRADE_LEVEL: int = 7

    SLEEP_TIME: list[int] = [31000, 42000]


settings = Settings()
