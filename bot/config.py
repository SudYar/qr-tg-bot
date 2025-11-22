"""
Модуль конфигурации бота
Управление настройками через переменные окружения
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    """Класс конфигурации приложения"""
    
    def __init__(self):
        """Инициализация конфигурации из переменных окружения"""
        self.TG_TOKEN: str = os.getenv('BOT_TOKEN', '')
        self.PROVERKACHEKA_TOKEN: str = os.getenv('CHEK_TOKEN', '')
        self.PROVERKACHEKA_URL: str = os.getenv(
            'CHEK_URL', 
            'https://proverkacheka.com/api/v1/check/get'
        )
        
        # Попытка загрузки из старого config.py для обратной совместимости
        if not self.TG_TOKEN or not self.PROVERKACHEKA_TOKEN:
            self._load_from_legacy_config()
        
    def _load_from_legacy_config(self) -> None:
        """Загрузка из старого файла config.py для обратной совместимости"""
        try:
            import config as legacy_config
            if not self.TG_TOKEN and hasattr(legacy_config, 'TG_token'):
                self.TG_TOKEN = legacy_config.TG_token
            if not self.PROVERKACHEKA_TOKEN and hasattr(legacy_config, 'proverkacheka_token'):
                self.PROVERKACHEKA_TOKEN = legacy_config.proverkacheka_token
            if hasattr(legacy_config, 'proverkacheka_url'):
                self.PROVERKACHEKA_URL = legacy_config.proverkacheka_url
        except ImportError:
            pass
        
    def validate(self) -> bool:
        """
        Проверка наличия обязательных параметров
        
        Returns:
            bool: True если все обязательные параметры присутствуют
        """
        if not self.TG_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        if not self.PROVERKACHEKA_TOKEN:
            raise ValueError("CHEK_TOKEN не установлен")
        return True


# Глобальный экземпляр конфигурации
config = Config()
