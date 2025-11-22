"""
Главный модуль бота
"""

import telebot
from .config import config
from .handlers.message_handlers import MessageHandlers
from .handlers.callback_handlers import CallbackHandlers


class QRCheckBot:
    """Основной класс бота для проверки чеков"""
    
    def __init__(self):
        """Инициализация бота и обработчиков"""
        try:
            config.validate()
        except ValueError as e:
            print(f"Предупреждение: {e}")
            print("Используются демо-настройки. Установите переменные окружения для production.")
        
        self.bot = telebot.TeleBot(config.TG_TOKEN)
        self.message_handlers = MessageHandlers(self.bot)
        self.callback_handlers = CallbackHandlers(self.bot)
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков бота"""
        
        @self.bot.message_handler(commands=['help', 'start'])
        def handle_start(message):
            self.message_handlers.handle_start(message)
        
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
            print("Бот запущен в режиме polling...")
            self.bot.infinity_polling()
        else:
            print("Бот готов к работе через webhook...")
    
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
