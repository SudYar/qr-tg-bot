"""
Обработчики callback-запросов
"""

import telebot
from telebot.types import CallbackQuery
from ..logger import logger
from ..utils.message_formatter import MessageFormatter
from ..utils.keyboard_factory import KeyboardFactory
from ..models.user_selection import UserSelection
from typing import Optional


class CallbackHandlers:
    """Класс обработчиков callback-запросов"""
    
    def __init__(self, bot: telebot.TeleBot):
        """Инициализация обработчиков"""
        self.bot = bot
        logger.debug("CallbackHandlers инициализирован")
    
    def handle_callback_query(self, call: CallbackQuery) -> None:
        """Обработка callback-запросов от inline-кнопок"""
        logger.info(f"Получен callback от пользователя {call.from_user.username}: {call.data[:50]}")
        
        try:
            data = KeyboardFactory.parse_callback_data(call.data)
            method = data['method']
            logger.debug(f"Метод callback: {method}")
            
            if method == KeyboardFactory.ACTION_CHOICE:
                type_ = data['type']
                number = data['number']
                is_plus = (type_ == KeyboardFactory.TYPE_PLUS)
                logger.debug(f"Обработка выбора продукта #{number}, действие: {'добавить' if is_plus else 'убрать'}")
                
                self._handle_product_selection(
                    call, number, 
                    call.from_user.username, 
                    call.from_user.first_name, 
                    is_plus
                )
                
            elif method == KeyboardFactory.ACTION_SUM:
                logger.debug("Обработка подсчета суммы")
                self._handle_sum_calculation(call)
                
        except Exception as e:
            self.bot.answer_callback_query(
                call.id, 
                text=f"Ошибка при обработке: {str(e)}"
            )
            logger.error(f"Ошибка в callback handler от пользователя {call.from_user.username}: {e}", exc_info=True)
    
    def _handle_product_selection(self, call: CallbackQuery, 
                                  product_num: int,
                                  username: Optional[str], 
                                  first_name: str,
                                  is_plus: bool) -> None:
        """Обработка выбора/снятия выбора товара"""
        from telebot import formatting
        html_text = formatting.apply_html_entities(call.message.text, call.message.entities, None)
        couples = MessageFormatter.parse_message_lines(html_text)
        if product_num < 1 or product_num > len(couples):
            self.bot.answer_callback_query(
                call.id, 
                text=f"Некорректный номер товара: {product_num}"
            )
            return
        
        new_lines = []
        error_message = ''
        has_error = False
        
        for i, (product_line, selection_line) in enumerate(couples):
            n = i + 1
            
            quantity = MessageFormatter.extract_quantity(product_line)
            total_selected = MessageFormatter.extract_total_selected(selection_line)
            
            if quantity is None or total_selected is None:
                self.bot.answer_callback_query(
                    call.id, 
                    text=f"У продукта {n} битый формат"
                )
                return
            
            if n != product_num:
                new_lines.append(f"{product_line}\n{selection_line}")
                continue
            
            users_with_at, users_without_at = MessageFormatter.extract_users(selection_line)
            selection = UserSelection(users_with_at, users_without_at)
            
            if not is_plus and total_selected == 0:
                error_message = f"{first_name} и так не был отмечен у продукта №{n}"
                has_error = True
                break
            
            if is_plus:
                selection.add_user(username, first_name)
            else:
                if not selection.remove_user(username, first_name):
                    display_name = f"@{username}" if username else first_name
                    error_message = f"{display_name} и так не был отмечен у продукта №{n}"
                    has_error = True
                    break
            
            new_total = selection.get_total_count()
            new_selection_line = MessageFormatter.format_selection_line(
                selection.users_with_at,
                selection.users_without_at,
                new_total
            )
            
            new_lines.append(f"{product_line}\n{new_selection_line}")
        
        if has_error:
            self.bot.answer_callback_query(call.id, text=error_message)
        else:
            new_text = MessageFormatter.change_message_lines(html_text, new_lines)
            current_markup = call.message.reply_markup
            markup = KeyboardFactory.create_keyboard_from_message(new_text, old_markup=current_markup)
            
            try:
                self.bot.edit_message_text(
                    new_text,
                    reply_markup=markup,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    entities=call.message.entities,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Ошибка при обновлении сообщения: {e}")
    
    def _handle_sum_calculation(self, call: CallbackQuery) -> None:
        """Обработка подсчета итоговой суммы"""
        user_totals = MessageFormatter.calculate_user_totals(call.message.text)
        logger.info(f"Подсчитана сумма для {len(user_totals)} пользователей")
        logger.debug(f"Суммы: {user_totals}")
        
        result_text = MessageFormatter.format_totals_message(user_totals)
        self.bot.reply_to(call.message, result_text)
        logger.debug(f"Итоговое сообщение отправлено пользователю {call.from_user.username}")
