"""
Модуль настройки логирования
"""

import logging
import sys
from .config import config


def setup_logger(name: str = 'qr_bot') -> logging.Logger:
    """Настройка логгера для приложения"""
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    
    # Удаляем существующие обработчики
    if logger.handlers:
        logger.handlers.clear()
    
    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.LOG_LEVEL)
    
    # Формат логов
    if config.DEBUG:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Глобальный логгер для приложения
logger = setup_logger()
