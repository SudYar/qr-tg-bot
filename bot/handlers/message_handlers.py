"""
Обработчики сообщений
"""

import telebot
from telebot.types import Message
from typing import Optional
import pandas as pd
from ..config import config
from ..logger import logger
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
        logger.debug("MessageHandlers инициализирован")
        
    def handle_start(self, message: Message) -> None:
        """Обработка команды /start и /help"""
        logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
        
        welcome_text = (
            "Привет! Я бот для сканирования QR-кодов с чеков.\n\n"
            "Просто отправь мне фото QR-кода с чека, и я:\n"
            "- Распознаю QR-код\n"
            "- Получу данные о покупках\n"
            "- Помогу разделить счет между участниками\n\n"
            "Используй команду /help для получения помощи"
        )
        
        if config.DEBUG:
            welcome_text += "\n\n[DEBUG] Доступна команда /test для тестирования интерфейса"
        
        self.bot.send_message(message.chat.id, welcome_text)
        logger.debug(f"Отправлено приветственное сообщение пользователю {message.from_user.id}")
    
    def handle_photo(self, message: Message) -> None:
        """Обработка фотографии с QR-кодом"""
        logger.info(f"Получено фото от пользователя {message.from_user.id}")
        
        try:
            logger.debug(f"Загрузка файла изображения...")
            file_path = self.bot.get_file(message.photo[-1].file_id).file_path
            file_bytes = self.bot.download_file(file_path)
            logger.debug(f"Файл загружен: {len(file_bytes)} байт")
            
            logger.debug("Сканирование QR-кода...")
            qr_data, has_qr = self.qr_scanner.scan_qr_code(file_bytes)
            logger.info(f"QR-код расшифрован: {qr_data[:50] if qr_data else 'Нет данных'}, найден: {has_qr}")
            
            result_text, success, receipt_data = self._process_qr_result(qr_data, has_qr, file_bytes)
            
            markup = None
            if success:
                logger.debug(f"Создание клавиатуры для {len(receipt_data)} продуктов")
                # Создаем клавиатуру с данными о продуктах для улучшенных лейблов
                markup = KeyboardFactory.create_product_selection_keyboard_with_data(receipt_data)
            
            self.bot.send_message(
                message.chat.id, 
                result_text, 
                parse_mode='HTML',  # Используем HTML для поддержки blockquote
                reply_markup=markup,
                protect_content=True
            )
            logger.info(f"Сообщение успешно отправлено пользователю {message.from_user.id}")
            
        except Exception as e:
            error_text = f"Произошла ошибка при обработке изображения: {str(e)}"
            self.bot.send_message(message.chat.id, error_text)
            logger.error(f"Ошибка при обработке фото от пользователя {message.from_user.id}: {e}", exc_info=True)
    
    def _process_qr_result(self, qr_data: str, has_qr: bool, 
                          file_bytes: bytes) -> tuple[str, bool, Optional[pd.DataFrame]]:
        """Обработка результата сканирования QR-кода"""
        if qr_data == '':
            if has_qr:
                logger.debug("QR-код найден, но не распознан. Отправка в API...")
                try:
                    df, metadata = self.receipt_api.get_receipt_from_file(file_bytes)
                    logger.info(f"Чек успешно получен через API: {len(df)} товаров")
                    return MessageFormatter.create_receipt_message(df, metadata), True, df
                except ReceiptAPIError as e:
                    logger.error(f"Ошибка API при получении чека: {e}")
                    return "Proverkacheka не отвечает. Попробуйте чуть позже", False, None
            else:
                logger.warning("QR-код не найден на изображении")
                return "Не получилось найти QR-код на снимке", False, None
        else:
            logger.debug("QR-код распознан, получение данных через API...")
            try:
                df, metadata = self.receipt_api.get_receipt_from_qr(qr_data)
                logger.info(f"Чек успешно получен: {len(df)} товаров")
                return MessageFormatter.create_receipt_message(df, metadata), True, df
            except ReceiptAPIError as e:
                logger.error(f"Ошибка API при получении чека по QR: {e}")
                return "QR-код перевернут или не для nalog.ru", False, None
    
    def handle_test(self, message: Message) -> None:
        """Тестовая команда с mock данными (только в DEBUG режиме)"""
        if not config.DEBUG:
            logger.warning(f"Попытка использовать /test в production режиме от пользователя {message.from_user.id}")
            return
        
        logger.info(f"Получена команда /test от пользователя {message.from_user.id}")
        
        # Mock данные для тестирования
        mock_data = {
            'name': ['Блинчик с сыром и ветчиной', 'Борщ с беконом', 'Блин "Цезарь" с кетчупом'],
            'price': [95.35, 145.88, 212.77],
            'quantity': [3, 1, 1]
        }
        
        mock_metadata = {
            'store_name': 'Тестовый магазин',
            'store_address': 'ул. Тестовая, д. 1',
            'total_sum': 454.0
        }
        
        df = pd.DataFrame(mock_data)
        logger.debug(f"Создан mock DataFrame с {len(df)} товарами")
        
        result_text = MessageFormatter.create_receipt_message(df, mock_metadata)
        markup = KeyboardFactory.create_product_selection_keyboard_with_data(df)
        
        self.bot.send_message(
            message.chat.id,
            result_text,
            parse_mode='HTML',
            reply_markup=markup,
            protect_content=True
        )
        
        logger.info(f"Тестовое сообщение отправлено пользователю {message.from_user.id}")
    
    def handle_default(self, message: Message) -> None:
        """Обработка неизвестных команд"""
        logger.debug(f"Получено неизвестное сообщение от пользователя {message.from_user.id}: {message.text[:50] if message.text else 'Нет текста'}")
        self.bot.send_message(
            message.chat.id, 
            'Кажется, что-то пошло не так. Используйте /help для получения помощи'
        )
