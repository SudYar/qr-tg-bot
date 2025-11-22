"""
Обработчики сообщений
"""

import telebot
from telebot.types import Message
from ..services.qr_scanner import QRScanner
from ..services.receipt_api import ReceiptAPI, ReceiptAPIError
from ..utils.message_formatter import MessageFormatter
from ..utils.keyboard_factory import KeyboardFactory


class MessageHandlers:
    """Класс обработчиков сообщений"""
    
    def __init__(self, bot: telebot.TeleBot):
        """
        Инициализация обработчиков
        
        Args:
            bot: Экземпляр TeleBot
        """
        self.bot = bot
        self.qr_scanner = QRScanner()
        self.receipt_api = ReceiptAPI()
        
    def handle_start(self, message: Message) -> None:
        """
        Обработка команды /start и /help
        
        Args:
            message: Объект сообщения
        """
        welcome_text = (
            "👋 Привет! Я бот для сканирования QR-кодов с чеков.\n\n"
            "📱 Просто отправь мне фото QR-кода с чека, и я:\n"
            "• Распознаю QR-код\n"
            "• Получу данные о покупках\n"
            "• Помогу разделить счет между участниками\n\n"
            "💡 Используй команду /help для получения помощи"
        )
        self.bot.send_message(message.chat.id, welcome_text)
    
    def handle_photo(self, message: Message) -> None:
        """
        Обработка фотографии с QR-кодом
        
        Args:
            message: Объект сообщения с фото
        """
        try:
            # Получение файла изображения
            file_path = self.bot.get_file(message.photo[-1].file_id).file_path
            file_bytes = self.bot.download_file(file_path)
            
            # Сканирование QR-кода
            qr_data, has_qr = self.qr_scanner.scan_qr_code(file_bytes)
            print(f"QR-код расшифрован: {qr_data}, найден: {has_qr}")
            
            # Обработка результата сканирования
            result_text, success = self._process_qr_result(qr_data, has_qr, file_bytes)
            
            # Создание клавиатуры
            markup = None
            if success:
                # Извлекаем количество товаров из сообщения
                lines = result_text.split('\n')
                products_count = (len(lines) - 1) // 2  # Минус заголовок, делить на 2
                markup = KeyboardFactory.create_product_selection_keyboard(products_count)
            
            # Отправка результата
            self.bot.send_message(
                message.chat.id, 
                result_text, 
                parse_mode='markdown',
                reply_markup=markup,
                protect_content=True
            )
            
        except Exception as e:
            error_text = f"❌ Произошла ошибка при обработке изображения: {str(e)}"
            self.bot.send_message(message.chat.id, error_text)
            print(f"Ошибка при обработке фото: {e}")
    
    def _process_qr_result(self, qr_data: str, has_qr: bool, 
                          file_bytes: bytes) -> tuple[str, bool]:
        """
        Обработка результата сканирования QR-кода
        
        Args:
            qr_data: Данные QR-кода
            has_qr: Найден ли QR-код
            file_bytes: Байты изображения
            
        Returns:
            tuple: (текст сообщения, успешность)
        """
        if qr_data == '':
            if has_qr:
                # QR-код найден, но не распознан - пробуем через API
                try:
                    df = self.receipt_api.get_receipt_from_file(file_bytes)
                    return MessageFormatter.create_receipt_message(df), True
                except ReceiptAPIError:
                    return "❌ Proverkacheka не отвечает. Попробуйте чуть позже", False
            else:
                return "❌ Не получилось найти QR-код на снимке", False
        else:
            # QR-код распознан
            try:
                df = self.receipt_api.get_receipt_from_qr(qr_data)
                return MessageFormatter.create_receipt_message(df), True
            except ReceiptAPIError:
                return "❌ QR-код перевернут или не для nalog.ru", False
    
    def handle_default(self, message: Message) -> None:
        """
        Обработка неизвестных команд
        
        Args:
            message: Объект сообщения
        """
        self.bot.send_message(
            message.chat.id, 
            'Кажется, что-то пошло не так. Используйте /help для получения помощи'
        )
