from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    use_sliding_window_counter: int = 0
    capacity: int                   = 10
    leaks_per_second: float         = 0.5
    window_size: float              = 1
    requests_per_window: int        = 2

    model_config = SettingsConfigDict(env_file=".env")
