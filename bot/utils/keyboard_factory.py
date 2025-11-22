"""
Фабрика inline-клавиатур
"""

import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


class KeyboardFactory:
    """Класс для создания inline-клавиатур"""
    
    # Типы действий
    ACTION_CHOICE = "choice"
    ACTION_SUM = "summ"
    
    # Типы операций
    TYPE_PLUS = "plus"
    TYPE_MINUS = "minus"
    
    @classmethod
    def create_callback_data(cls, method: str, type_: Optional[str] = None, 
                            number: Optional[int] = None) -> str:
        """
        Создание данных для callback
        
        Args:
            method: Метод действия (choice, summ)
            type_: Тип операции (plus, minus)
            number: Номер товара
            
        Returns:
            str: JSON-строка с данными callback
        """
        data = {"method": method}
        
        if type_ is not None:
            data["type"] = type_
        
        if number is not None:
            data["number"] = number
        
        return json.dumps(data)
    
    @classmethod
    def parse_callback_data(cls, callback_data: str) -> dict:
        """
        Парсинг данных callback
        
        Args:
            callback_data: JSON-строка с данными
            
        Returns:
            dict: Словарь с данными
        """
        # Обработка случая, когда данные разделены подчеркиванием
        parts = callback_data.split('_')
        return json.loads(parts[0])
    
    @classmethod
    def create_product_selection_keyboard(cls, products_count: int, 
                                         selected_counts: Optional[List[int]] = None) -> InlineKeyboardMarkup:
        """
        Создание клавиатуры для выбора товаров
        
        Args:
            products_count: Количество товаров
            selected_counts: Список количества выбранных товаров для каждого продукта
            
        Returns:
            InlineKeyboardMarkup: Готовая клавиатура
        """
        markup = InlineKeyboardMarkup()
        
        if selected_counts is None:
            selected_counts = [0] * products_count
        
        for i in range(products_count):
            num = i + 1
            count = selected_counts[i]
            
            if count == 0:
                # Только кнопка "Выбрать"
                markup.add(
                    InlineKeyboardButton(
                        text=f'{num}. Выбрать',
                        callback_data=cls.create_callback_data(
                            cls.ACTION_CHOICE, cls.TYPE_PLUS, num
                        )
                    )
                )
            else:
                # Кнопки "Выбрать" и "Убрать"
                markup.add(
                    InlineKeyboardButton(
                        text=f'{num}. Выбрать',
                        callback_data=cls.create_callback_data(
                            cls.ACTION_CHOICE, cls.TYPE_PLUS, num
                        )
                    ),
                    InlineKeyboardButton(
                        text='Убрать',
                        callback_data=cls.create_callback_data(
                            cls.ACTION_CHOICE, cls.TYPE_MINUS, num
                        )
                    )
                )
        
        # Кнопка "Просуммировать"
        markup.add(
            InlineKeyboardButton(
                text='Просуммировать',
                callback_data=cls.create_callback_data(cls.ACTION_SUM)
            )
        )
        
        return markup
    
    @classmethod
    def create_keyboard_from_message(cls, message_text: str) -> InlineKeyboardMarkup:
        """
        Создание клавиатуры на основе текста сообщения
        
        Args:
            message_text: Текст сообщения с товарами
            
        Returns:
            InlineKeyboardMarkup: Готовая клавиатура
        """
        from .message_formatter import MessageFormatter
        
        couples = MessageFormatter.parse_message_lines(message_text)
        selected_counts = []
        
        for product_line, selection_line in couples:
            total = MessageFormatter.extract_total_selected(selection_line)
            selected_counts.append(total if total is not None else 0)
        
        return cls.create_product_selection_keyboard(len(couples), selected_counts)
