"""
Модуль форматирования сообщений
"""

import pandas as pd
import re
from typing import List, Tuple, Dict, Optional
from collections import defaultdict


class MessageFormatter:
    """Класс для создания и парсинга сообщений"""
    
    # Шаблоны сообщений
    TITLE_TEMPLATE = "Список продуктов из чека:\n"
    PRODUCT_TEMPLATE = "{num}. Название: {name}, Цена: *{price}* р., Количество: *{quantity}*"
    SELECTION_TEMPLATE = "Выбрали: {users}, Всего: {total}"
    
    # Регулярные выражения
    QUANTITY_PATTERN = re.compile(r"Количество:\s*(\d+)")
    TOTAL_PATTERN = re.compile(r"Всего:\s*(\d+)")
    USERS_WITH_AT_PATTERN = re.compile(r"@(\w+)\s*\((\d+)\)")
    USERS_WITHOUT_AT_PATTERN = re.compile(r"(?<!@|\w)(\w+)\s*\((\d+)\)")
    FULL_PRODUCT_PATTERN = re.compile(
        r"Название:\s*(.*?),\s*Цена:\s*(\d+\.\d+)\s*р\.,\s*Количество:\s*(\d+)\.?\d*\s*"
        r"Выбрали:\s*(.*?),\s*Всего:\s*(\d+)"
    )
    
    @classmethod
    def create_receipt_message(cls, df: pd.DataFrame, metadata: dict = None) -> str:
        """Создание сообщения со списком товаров из чека"""
        message_parts = []
        
        # Добавляем метаданные чека в начало
        if metadata:
            meta_lines = []
            if 'store_name' in metadata:
                meta_lines.append(f"<b>Магазин:</b> {metadata['store_name']}")
            if 'store_address' in metadata:
                meta_lines.append(f"<b>Адрес:</b> {metadata['store_address']}")
            if 'total_sum' in metadata:
                meta_lines.append(f"<b>Итого:</b> {metadata['total_sum']:.2f} р.")
            
            if meta_lines:
                message_parts.append('\n'.join(meta_lines))
                message_parts.append('')  # Пустая строка для разделения
        
        # Создаем список продуктов
        products = []
        for idx, row in df.iterrows():
            product_line = cls.PRODUCT_TEMPLATE.format(
                num=idx + 1,
                name=row['name'],
                price=row['price'],
                quantity=row['quantity']
            )
            selection_line = cls.SELECTION_TEMPLATE.format(users='', total=0)
            products.append(f"{product_line}\n{selection_line}")
        
        # Оборачиваем список продуктов в collapsible блок
        products_text = '\n'.join(products)
        message_parts.append(f"<blockquote expandable>{cls.TITLE_TEMPLATE}{products_text}</blockquote>")
        
        return '\n'.join(message_parts)
    
    @classmethod
    def parse_message_lines(cls, message_text: str) -> List[Tuple[str, str]]:
        """Разбор сообщения на пары строк (товар, выборы)"""
        # Извлекаем содержимое из blockquote если оно есть
        if '<blockquote' in message_text:
            start = message_text.find('>')
            end = message_text.rfind('</blockquote>')
            if start != -1 and end != -1:
                message_text = message_text[start+1:end]
        
        lines = message_text.split('\n')
        lines = lines[1:] if lines else []  # Пропускаем заголовок
        
        couples = []
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                couples.append((lines[i], lines[i + 1]))
        
        return couples
    
    @classmethod
    def extract_quantity(cls, product_line: str) -> Optional[int]:
        """Извлечение количества товара из строки"""
        match = cls.QUANTITY_PATTERN.search(product_line)
        return int(match.group(1)) if match else None
    
    @classmethod
    def extract_total_selected(cls, selection_line: str) -> Optional[int]:
        """Извлечение общего количества выбранных товаров"""
        match = cls.TOTAL_PATTERN.search(selection_line)
        return int(match.group(1)) if match else None
    
    @classmethod
    def extract_users(cls, selection_line: str) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
        """Извлечение пользователей и их количества из строки выборов"""
        selected_text = selection_line.replace("Выбрали: ", "")
        
        users_with_at = [
            (match[0], int(match[1])) 
            for match in cls.USERS_WITH_AT_PATTERN.findall(selected_text)
        ]
        
        users_without_at = [
            (match[0], int(match[1])) 
            for match in cls.USERS_WITHOUT_AT_PATTERN.findall(selected_text)
        ]
        
        return users_with_at, users_without_at
    
    @classmethod
    def format_selection_line(cls, users_with_at: List[Tuple[str, int]], 
                             users_without_at: List[Tuple[str, int]], 
                             total: int) -> str:
        """Форматирование строки с выборами пользователей"""
        users_with_at_str = ", ".join([f"@{user[0]} ({user[1]})" for user in users_with_at])
        users_without_at_str = ", ".join([f"{user[0]} ({user[1]})" for user in users_without_at])
        
        result = f"Выбрали: {users_with_at_str}, {users_without_at_str}, Всего: {total}"
        result = result.replace("Выбрали: , ", "Выбрали: ").replace(", , ", ", ").rstrip(", ")
        
        return result
    
    @classmethod
    def calculate_user_totals(cls, message_text: str) -> Dict[str, float]:
        """Расчет суммы для каждого пользователя"""
        user_totals = defaultdict(float)
        
        matches = cls.FULL_PRODUCT_PATTERN.findall(message_text)
        
        for match in matches:
            name = match[0]
            price = float(match[1])
            quantity = float(match[2])
            selected_users = match[3]
            total_selected = int(match[4])
            
            user_pattern = re.compile(r"(@?\w+)\s*\((\d+)\)")
            users = user_pattern.findall(selected_users)
            
            # Пропорциональное распределение стоимости по пользователям
            for user in users:
                username = user[0]
                user_count = int(user[1])
                if total_selected > 0:
                    user_totals[username] += (price * quantity) * (user_count / total_selected)
        
        return dict(user_totals)
    
    @classmethod
    def format_totals_message(cls, user_totals: Dict[str, float]) -> str:
        """Форматирование итогового сообщения с суммами"""
        if not user_totals:
            return 'Никто ещё не отметился'
        
        lines = [f"{user} должен {total:.2f} р." for user, total in user_totals.items()]
        return '\n'.join(lines)
