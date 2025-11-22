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
    def create_receipt_message(cls, df: pd.DataFrame) -> str:
        """
        Создание сообщения со списком товаров из чека
        
        Args:
            df: DataFrame с колонками name, price, quantity
            
        Returns:
            str: Отформатированное сообщение
        """
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
        
        return cls.TITLE_TEMPLATE + '\n'.join(products)
    
    @classmethod
    def parse_message_lines(cls, message_text: str) -> List[Tuple[str, str]]:
        """
        Разбор сообщения на пары строк (товар, выборы)
        
        Args:
            message_text: Текст сообщения
            
        Returns:
            List[Tuple[str, str]]: Список пар (строка товара, строка выборов)
        """
        lines = message_text.split('\n')
        # Пропускаем заголовок
        lines = lines[1:] if lines else []
        
        couples = []
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                couples.append((lines[i], lines[i + 1]))
        
        return couples
    
    @classmethod
    def extract_quantity(cls, product_line: str) -> Optional[int]:
        """
        Извлечение количества товара из строки
        
        Args:
            product_line: Строка с информацией о товаре
            
        Returns:
            Optional[int]: Количество или None
        """
        match = cls.QUANTITY_PATTERN.search(product_line)
        return int(match.group(1)) if match else None
    
    @classmethod
    def extract_total_selected(cls, selection_line: str) -> Optional[int]:
        """
        Извлечение общего количества выбранных товаров
        
        Args:
            selection_line: Строка с информацией о выборах
            
        Returns:
            Optional[int]: Количество или None
        """
        match = cls.TOTAL_PATTERN.search(selection_line)
        return int(match.group(1)) if match else None
    
    @classmethod
    def extract_users(cls, selection_line: str) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
        """
        Извлечение пользователей и их количества из строки выборов
        
        Args:
            selection_line: Строка с информацией о выборах
            
        Returns:
            Tuple: (пользователи с @username, пользователи по имени)
        """
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
        """
        Форматирование строки с выборами пользователей
        
        Args:
            users_with_at: Список пользователей с @username
            users_without_at: Список пользователей по имени
            total: Общее количество выбранных товаров
            
        Returns:
            str: Отформатированная строка
        """
        users_with_at_str = ", ".join([f"@{user[0]} ({user[1]})" for user in users_with_at])
        users_without_at_str = ", ".join([f"{user[0]} ({user[1]})" for user in users_without_at])
        
        result = f"Выбрали: {users_with_at_str}, {users_without_at_str}, Всего: {total}"
        result = result.replace("Выбрали: , ", "Выбрали: ").replace(", , ", ", ").rstrip(", ")
        
        return result
    
    @classmethod
    def calculate_user_totals(cls, message_text: str) -> Dict[str, float]:
        """
        Расчет суммы для каждого пользователя
        
        Args:
            message_text: Текст сообщения с товарами и выборами
            
        Returns:
            Dict[str, float]: Словарь {пользователь: сумма}
        """
        user_totals = defaultdict(float)
        
        matches = cls.FULL_PRODUCT_PATTERN.findall(message_text)
        
        for match in matches:
            name = match[0]
            price = float(match[1])
            quantity = float(match[2])
            selected_users = match[3]
            total_selected = int(match[4])
            
            # Извлечение пользователей и их количества
            user_pattern = re.compile(r"(@?\w+)\s*\((\d+)\)")
            users = user_pattern.findall(selected_users)
            
            # Расчет суммы для каждого пользователя
            for user in users:
                username = user[0]
                user_count = int(user[1])
                # Расчет: (цена * количество) * (доля пользователя / общее количество выбранных)
                # Используем total_selected для деления, так как пользователи могут выбирать больше
                if total_selected > 0:
                    user_totals[username] += (price * quantity) * (user_count / total_selected)
        
        return dict(user_totals)
    
    @classmethod
    def format_totals_message(cls, user_totals: Dict[str, float]) -> str:
        """
        Форматирование итогового сообщения с суммами
        
        Args:
            user_totals: Словарь с суммами пользователей
            
        Returns:
            str: Отформатированное сообщение
        """
        if not user_totals:
            return 'Никто ещё не отметился'
        
        lines = [f"{user} должен {total:.2f} р." for user, total in user_totals.items()]
        return '\n'.join(lines)
