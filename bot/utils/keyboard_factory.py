"""
Фабрика inline-клавиатур
"""

import json
import re

import pandas as pd
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
        """Создание данных для callback"""
        data = {"method": method}
        
        if type_ is not None:
            data["type"] = type_
        
        if number is not None:
            data["number"] = number
        
        return json.dumps(data)
    
    @classmethod
    def parse_callback_data(cls, callback_data: str) -> dict:
        """Парсинг данных callback"""
        parts = callback_data.split('_')
        return json.loads(parts[0])
    
    @classmethod
    def create_product_selection_keyboard_with_data(cls, df: pd.DataFrame, 
                                                    selected_counts: Optional[List[int]] = None) -> InlineKeyboardMarkup:
        """Создание клавиатуры с улучшенными лейблами, включающими имена продуктов и количество"""
        markup = InlineKeyboardMarkup()
        
        if selected_counts is None:
            selected_counts = [0] * len(df)
        
        for idx, row in df.iterrows():
            num = idx + 1
            count = selected_counts[idx]
            total_qty = int(row['quantity'])
            
            # Извлекаем первые несколько слов из названия продукта (до 15 символов)
            product_name = row['name']
            short_name = product_name[:13] + '...' if len(product_name) > 13 else product_name
            
            # Формат кнопки: "1. Хлеб 0/2" (номер, название, выбрано/всего)
            button_text = f'{num}. {short_name} {count}/{total_qty}'
            
            if count == 0:
                markup.add(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=cls.create_callback_data(
                            cls.ACTION_CHOICE, cls.TYPE_PLUS, num
                        )
                    )
                )
            else:
                markup.add(
                    InlineKeyboardButton(
                        text=button_text,
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
        
        markup.add(
            InlineKeyboardButton(
                text='Просуммировать',
                callback_data=cls.create_callback_data(cls.ACTION_SUM)
            )
        )
        
        return markup
    
    @classmethod
    def create_product_selection_keyboard(cls, products_count: int, 
                                         selected_counts: Optional[List[int]] = None) -> InlineKeyboardMarkup:
        """Создание клавиатуры для выбора товаров (упрощенная версия без названий)"""
        markup = InlineKeyboardMarkup()
        
        if selected_counts is None:
            selected_counts = [0] * products_count
        
        for i in range(products_count):
            num = i + 1
            count = selected_counts[i]
            
            if count == 0:
                markup.add(
                    InlineKeyboardButton(
                        text=f'{num}. Выбрать',
                        callback_data=cls.create_callback_data(
                            cls.ACTION_CHOICE, cls.TYPE_PLUS, num
                        )
                    )
                )
            else:
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
        
        markup.add(
            InlineKeyboardButton(
                text='Просуммировать',
                callback_data=cls.create_callback_data(cls.ACTION_SUM)
            )
        )
        
        return markup

    @classmethod
    def change_product_selection_keyboard(cls, products_count: int, old_markup: InlineKeyboardMarkup,
                                          selected_counts: Optional[List[int]] = None) -> InlineKeyboardMarkup:
        """Редактирование клавиатуры для выбора товаров"""
        # TODO: При переходе на aiogram использовать InlineKeyboardBuilder для более удобного
        # динамического создания клавиатур вместо модификации существующей
        markup = InlineKeyboardMarkup()

        if selected_counts is None:
            selected_counts = [0] * products_count
        if len(selected_counts) + 1 == len(old_markup.keyboard):
            for i in range(products_count):
                num = i + 1
                count = selected_counts[i]
                row = old_markup.keyboard[i]

                if count == 0 and len(row) > 1:
                    row.pop(-1)
                elif count > 0 and len(row) == 1:
                    row.append(
                        InlineKeyboardButton(
                            text='Убрать',
                            callback_data=cls.create_callback_data(
                                cls.ACTION_CHOICE, cls.TYPE_MINUS, num
                            )
                        )
                    )
                row[0].text = re.sub(r"\d(?=/\d$)", str(count), row[0].text)

        return old_markup

    @classmethod
    def create_keyboard_from_message(cls, message_text: str, df: pd.DataFrame = None, old_markup: InlineKeyboardMarkup = None) -> InlineKeyboardMarkup:
        """Создание клавиатуры на основе текста сообщения"""
        from .message_formatter import MessageFormatter
        
        couples = MessageFormatter.parse_message_lines(message_text)
        selected_counts = []
        
        for product_line, selection_line in couples:
            total = MessageFormatter.extract_total_selected(selection_line)
            selected_counts.append(total if total is not None else 0)
        
        # Если есть DataFrame, используем улучшенные кнопки
        if df is not None:
            return cls.create_product_selection_keyboard_with_data(df, selected_counts)
        if old_markup is not None:
            return cls.change_product_selection_keyboard(len(couples), old_markup, selected_counts)
        return cls.create_product_selection_keyboard(len(couples), selected_counts)
