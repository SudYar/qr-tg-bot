"""
Главный модуль бота
"""

import telebot
from .config import config
from .logger import logger
from .handlers.message_handlers import MessageHandlers
from .handlers.callback_handlers import CallbackHandlers


class QRCheckBot:
    """Основной класс бота для проверки чеков"""
    
    def __init__(self):
        """Инициализация бота и обработчиков"""
        logger.info("Инициализация бота...")
        
        if config.DEBUG:
            logger.debug("Режим отладки включен")
        
        try:
            config.validate()
            logger.info("Конфигурация валидна")
        except ValueError as e:
            logger.warning(f"Ошибка конфигурации: {e}")
            logger.warning("Используются демо-настройки. Установите переменные окружения для production.")
        
        self.bot = telebot.TeleBot(config.TG_TOKEN)
        self.message_handlers = MessageHandlers(self.bot)
        self.callback_handlers = CallbackHandlers(self.bot)
        self._register_handlers()
        
        logger.info("Бот успешно инициализирован")
    
    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков бота"""
        
        @self.bot.message_handler(commands=['help', 'start'])
        def handle_start(message):
            self.message_handlers.handle_start(message)
        
        # Регистрация debug команды /test только в DEBUG режиме
        if config.DEBUG:
            @self.bot.message_handler(commands=['test'])
            def handle_test(message):
                self.message_handlers.handle_test(message)
            logger.debug("Зарегистрирована debug команда /test")
        
        @self.bot.message_handler(func=lambda message: True, content_types=["photo"])
        def handle_photo(message):
            self.message_handlers.handle_photo(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_default(message):
            self.message_handlers.handle_default(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            self.callback_handlers.handle_callback_query(call)
    
    def run(self, use_webhook: bool = False) -> None:
        """
        Запуск бота
        
        Args:
            use_webhook: True для работы через webhook, False для polling
        """
        if not use_webhook:
            self.bot.remove_webhook()
            logger.info("Бот запущен в режиме polling...")
            self.bot.infinity_polling()
        else:
            logger.info("Бот готов к работе через webhook...")
    
    def process_update(self, update_data: dict) -> dict:
        """
        Обработка обновления для webhook
        
        Args:
            update_data: Данные обновления от Telegram
            
        Returns:
            dict: Ответ для API Gateway
        """
        message = telebot.types.Update.de_json(update_data)
        self.bot.process_new_updates([message])
        return {
            'statusCode': 200,
            'body': 'OK'
        }
