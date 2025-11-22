"""
Обработчики сообщений
"""

import telebot
from telebot.types import Message
from typing import Optional
import pandas as pd
from ..services.qr_scanner import QRScanner
from ..services.receipt_api import ReceiptAPI, ReceiptAPIError
from ..utils.message_formatter import MessageFormatter
from ..utils.keyboard_factory import KeyboardFactory


class MessageHandlers:
    """Класс обработчиков сообщений"""
    
    def __init__(self, bot: telebot.TeleBot):
        """Инициализация обработчиков"""
        self.bot = bot
        self.qr_scanner = QRScanner()
        self.receipt_api = ReceiptAPI()
        
    def handle_start(self, message: Message) -> None:
        """Обработка команды /start и /help"""
        welcome_text = (
            "Привет! Я бот для сканирования QR-кодов с чеков.\n\n"
            "Просто отправь мне фото QR-кода с чека, и я:\n"
            "- Распознаю QR-код\n"
            "- Получу данные о покупках\n"
            "- Помогу разделить счет между участниками\n\n"
            "Используй команду /help для получения помощи"
        )
        self.bot.send_message(message.chat.id, welcome_text)
    
    def handle_photo(self, message: Message) -> None:
        """Обработка фотографии с QR-кодом"""
        try:
            file_path = self.bot.get_file(message.photo[-1].file_id).file_path
            file_bytes = self.bot.download_file(file_path)
            
            qr_data, has_qr = self.qr_scanner.scan_qr_code(file_bytes)
            print(f"QR-код расшифрован: {qr_data}, найден: {has_qr}")
            
            result_text, success, receipt_data = self._process_qr_result(qr_data, has_qr, file_bytes)
            
            markup = None
            if success:
                # Создаем клавиатуру с данными о продуктах для улучшенных лейблов
                markup = KeyboardFactory.create_product_selection_keyboard_with_data(receipt_data)
            
            self.bot.send_message(
                message.chat.id, 
                result_text, 
                parse_mode='HTML',  # Используем HTML для поддержки blockquote
                reply_markup=markup,
                protect_content=True
            )
            
        except Exception as e:
            error_text = f"Произошла ошибка при обработке изображения: {str(e)}"
            self.bot.send_message(message.chat.id, error_text)
            print(f"Ошибка при обработке фото: {e}")
    
    def _process_qr_result(self, qr_data: str, has_qr: bool, 
                          file_bytes: bytes) -> tuple[str, bool, Optional[pd.DataFrame]]:
        """Обработка результата сканирования QR-кода"""
        if qr_data == '':
            if has_qr:
                try:
                    df, metadata = self.receipt_api.get_receipt_from_file(file_bytes)
                    return MessageFormatter.create_receipt_message(df, metadata), True, df
                except ReceiptAPIError:
                    return "Proverkacheka не отвечает. Попробуйте чуть позже", False, None
            else:
                return "Не получилось найти QR-код на снимке", False, None
        else:
            try:
                df, metadata = self.receipt_api.get_receipt_from_qr(qr_data)
                return MessageFormatter.create_receipt_message(df, metadata), True, df
            except ReceiptAPIError:
                return "QR-код перевернут или не для nalog.ru", False, None
    
    def handle_default(self, message: Message) -> None:
        """Обработка неизвестных команд"""
        self.bot.send_message(
            message.chat.id, 
            'Кажется, что-то пошло не так. Используйте /help для получения помощи'
        )
