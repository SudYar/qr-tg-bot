"""
Обработчики callback-запросов
"""

import telebot
from telebot.types import CallbackQuery
from ..utils.message_formatter import MessageFormatter
from ..utils.keyboard_factory import KeyboardFactory
from ..models.user_selection import UserSelection
from typing import Optional


class CallbackHandlers:
    """Класс обработчиков callback-запросов"""
    
    def __init__(self, bot: telebot.TeleBot):
        """
        Инициализация обработчиков
        
        Args:
            bot: Экземпляр TeleBot
        """
        self.bot = bot
    
    def handle_callback_query(self, call: CallbackQuery) -> None:
        """
        Обработка callback-запросов от inline-кнопок
        
        Args:
            call: Объект callback-запроса
        """
        try:
            # Парсинг данных callback
            data = KeyboardFactory.parse_callback_data(call.data)
            method = data['method']
            
            if method == KeyboardFactory.ACTION_CHOICE:
                # Обработка выбора товара
                type_ = data['type']
                number = data['number']
                is_plus = (type_ == KeyboardFactory.TYPE_PLUS)
                
                self._handle_product_selection(
                    call, number, 
                    call.from_user.username, 
                    call.from_user.first_name, 
                    is_plus
                )
                
            elif method == KeyboardFactory.ACTION_SUM:
                # Подсчет суммы
                self._handle_sum_calculation(call)
                
        except Exception as e:
            self.bot.answer_callback_query(
                call.id, 
                text=f"❌ Ошибка при обработке: {str(e)}"
            )
            print(f"Ошибка в callback handler: {e}")
    
    def _handle_product_selection(self, call: CallbackQuery, 
                                  product_num: int,
                                  username: Optional[str], 
                                  first_name: str,
                                  is_plus: bool) -> None:
        """
        Обработка выбора/снятия выбора товара
        
        Args:
            call: Объект callback-запроса
            product_num: Номер товара
            username: Username пользователя
            first_name: Имя пользователя
            is_plus: True для добавления, False для удаления
        """
        # Разбор сообщения на пары строк
        couples = MessageFormatter.parse_message_lines(call.message.text)
        
        if product_num < 1 or product_num > len(couples):
            self.bot.answer_callback_query(
                call.id, 
                text=f"❌ Некорректный номер товара: {product_num}"
            )
            return
        
        new_lines = []
        error_message = ''
        has_error = False
        
        for i, (product_line, selection_line) in enumerate(couples):
            n = i + 1
            
            # Извлечение данных
            quantity = MessageFormatter.extract_quantity(product_line)
            total_selected = MessageFormatter.extract_total_selected(selection_line)
            
            if quantity is None or total_selected is None:
                self.bot.answer_callback_query(
                    call.id, 
                    text=f"❌ У продукта {n} битый формат"
                )
                return
            
            # Если это не целевой товар, оставляем как есть
            if n != product_num:
                new_lines.append(f"{product_line}\n{selection_line}")
                continue
            
            # Обработка выбора для целевого товара
            users_with_at, users_without_at = MessageFormatter.extract_users(selection_line)
            selection = UserSelection(users_with_at, users_without_at)
            
            # Проверка на минимум при удалении
            if not is_plus and total_selected == 0:
                error_message = f"{first_name} и так не был отмечен у продукта №{n}"
                has_error = True
                break
            
            # Добавление или удаление пользователя
            if is_plus:
                selection.add_user(username, first_name)
            else:
                if not selection.remove_user(username, first_name):
                    display_name = f"@{username}" if username else first_name
                    error_message = f"{display_name} и так не был отмечен у продукта №{n}"
                    has_error = True
                    break
            
            # Формирование новой строки выбора
            new_total = selection.get_total_count()
            new_selection_line = MessageFormatter.format_selection_line(
                selection.users_with_at,
                selection.users_without_at,
                new_total
            )
            
            new_lines.append(f"{product_line}\n{new_selection_line}")
        
        # Обработка ошибок или обновление сообщения
        if has_error:
            self.bot.answer_callback_query(call.id, text=error_message)
        else:
            # Формирование нового сообщения
            new_text = MessageFormatter.TITLE_TEMPLATE + '\n'.join(new_lines)
            
            # Создание новой клавиатуры
            markup = KeyboardFactory.create_keyboard_from_message(new_text)
            
            # Обновление сообщения
            try:
                self.bot.edit_message_text(
                    new_text,
                    reply_markup=markup,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    entities=call.message.entities
                )
            except Exception as e:
                print(f"Ошибка при обновлении сообщения: {e}")
    
    def _handle_sum_calculation(self, call: CallbackQuery) -> None:
        """
        Обработка подсчета итоговой суммы
        
        Args:
            call: Объект callback-запроса
        """
        # Расчет сумм для пользователей
        user_totals = MessageFormatter.calculate_user_totals(call.message.text)
        
        # Форматирование сообщения
        result_text = MessageFormatter.format_totals_message(user_totals)
        
        # Отправка результата
        self.bot.reply_to(call.message, result_text)
