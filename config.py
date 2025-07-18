# project/config.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Эта строка говорит Pydantic, откуда брать данные - из файла .env
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        # Эта опция позволяет Pydantic работать с моделями SQLAlchemy
        # без дополнительных предупреждений.
        protected_namespaces=('model_config', 'model_fields')
    )

    # --- Telegram Bot Settings ---
    BOT_TOKEN: str
    # Эта строка автоматически преобразует "123,456" в список чисел [123, 456]
    ADMIN_IDS: list[int] = Field(default=[], validation_alias='ADMIN_IDS')

    # --- Database Settings ---
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Это "вычисляемое" свойство. Оно автоматически собирает
    # полную строку подключения к БД из отдельных переменных.
    # Именно эту переменную будет использовать SQLAlchemy.
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Logging Settings ---
    LOG_LEVEL: str = 'INFO'

# Создаем единый, глобальный экземпляр настроек,
# который будем импортировать во всех остальных файлах проекта.
settings = Settings()