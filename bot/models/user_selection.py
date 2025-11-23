"""
Модель выбора пользователя
"""

from typing import List, Tuple, Optional


class UserSelection:
    """Класс для управления выбором пользователей"""
    
    def __init__(self, users_with_at: List[Tuple[str, int]] = None,
                 users_without_at: List[Tuple[str, int]] = None):
        """
        Инициализация выбора пользователей
        
        Args:
            users_with_at: Список пользователей с @username
            users_without_at: Список пользователей по имени
        """
        self.users_with_at = users_with_at or []
        self.users_without_at = users_without_at or []
    
    def add_user(self, username: Optional[str], first_name: str) -> None:
        """
        Добавление пользователя к выбору
        
        Args:
            username: Username пользователя (может быть None)
            first_name: Имя пользователя
        """
        if username:
            # Проверяем, есть ли уже пользователь в списке
            for i, (user, count) in enumerate(self.users_with_at):
                if user == username:
                    # Увеличиваем счетчик
                    self.users_with_at[i] = (user, count + 1)
                    return
            # Если не найден, добавляем нового
            self.users_with_at.append((username, 1))
        else:
            # Аналогично для пользователей без username
            for i, (user, count) in enumerate(self.users_without_at):
                if user == first_name:
                    self.users_without_at[i] = (user, count + 1)
                    return
            self.users_without_at.append((first_name, 1))
    
    def remove_user(self, username: Optional[str], first_name: str) -> bool:
        """
        Удаление пользователя из выбора
        
        Args:
            username: Username пользователя (может быть None)
            first_name: Имя пользователя
            
        Returns:
            bool: True если пользователь был найден и удален
        """
        if username:
            for i, (user, count) in enumerate(self.users_with_at):
                if user == username:
                    if count == 1:
                        # Удаляем пользователя
                        self.users_with_at.pop(i)
                    else:
                        # Уменьшаем счетчик
                        self.users_with_at[i] = (user, count - 1)
                    return True
            return False
        else:
            for i, (user, count) in enumerate(self.users_without_at):
                if user == first_name:
                    if count == 1:
                        self.users_without_at.pop(i)
                    else:
                        self.users_without_at[i] = (user, count - 1)
                    return True
            return False
    
    def get_total_count(self) -> int:
        """
        Получение общего количества выбранных товаров
        
        Returns:
            int: Общее количество
        """
        total = sum(count for _, count in self.users_with_at)
        total += sum(count for _, count in self.users_without_at)
        return total
