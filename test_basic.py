"""
Базовые тесты для проверки функциональности бота
"""

import pandas as pd
from bot.utils.message_formatter import MessageFormatter
from bot.utils.keyboard_factory import KeyboardFactory
from bot.models.user_selection import UserSelection


def test_message_formatter():
    """Тест создания сообщения из DataFrame"""
    # Создание тестовых данных
    df = pd.DataFrame({
        'name': ['Хлеб', 'Молоко'],
        'price': [45.5, 65.0],
        'quantity': [1, 2]
    })
    
    # Создание сообщения
    message = MessageFormatter.create_receipt_message(df)
    
    # Проверки
    assert 'Список продуктов из чека:' in message
    assert 'Хлеб' in message
    assert '45.5' in message
    assert 'Молоко' in message
    assert '65.0' in message
    assert 'Всего: 0' in message
    print("✅ test_message_formatter passed")


def test_parse_message_lines():
    """Тест парсинга сообщения"""
    message = """Список продуктов из чека:
1. Название: Хлеб, Цена: 45.5 р., Количество: 1
Выбрали: , Всего: 0
2. Название: Молоко, Цена: 65.0 р., Количество: 2
Выбрали: , Всего: 0"""
    
    couples = MessageFormatter.parse_message_lines(message)
    
    assert len(couples) == 2
    assert 'Хлеб' in couples[0][0]
    assert 'Молоко' in couples[1][0]
    print("✅ test_parse_message_lines passed")


def test_extract_quantity():
    """Тест извлечения количества"""
    line = "1. Название: Хлеб, Цена: 45.5 р., Количество: 3"
    quantity = MessageFormatter.extract_quantity(line)
    
    assert quantity == 3
    print("✅ test_extract_quantity passed")


def test_extract_total_selected():
    """Тест извлечения общего количества выбранных"""
    line = "Выбрали: @user1 (2), user2 (1), Всего: 3"
    total = MessageFormatter.extract_total_selected(line)
    
    assert total == 3
    print("✅ test_extract_total_selected passed")


def test_extract_users():
    """Тест извлечения пользователей"""
    line = "Выбрали: @user1 (2), user2 (1), Всего: 3"
    users_with_at, users_without_at = MessageFormatter.extract_users(line)
    
    assert len(users_with_at) == 1
    assert users_with_at[0] == ('user1', 2)
    assert len(users_without_at) == 1
    assert users_without_at[0] == ('user2', 1)
    print("✅ test_extract_users passed")


def test_user_selection_add():
    """Тест добавления пользователя"""
    selection = UserSelection()
    
    # Добавление пользователя с username
    selection.add_user('john', 'John')
    assert selection.get_total_count() == 1
    assert len(selection.users_with_at) == 1
    
    # Добавление еще раз того же пользователя
    selection.add_user('john', 'John')
    assert selection.get_total_count() == 2
    assert selection.users_with_at[0][1] == 2
    
    print("✅ test_user_selection_add passed")


def test_user_selection_remove():
    """Тест удаления пользователя"""
    selection = UserSelection([('user1', 2)], [('User2', 1)])
    
    # Удаление одного выбора пользователя
    result = selection.remove_user('user1', 'User1')
    assert result is True
    assert selection.users_with_at[0][1] == 1
    
    # Удаление последнего выбора пользователя
    result = selection.remove_user('user1', 'User1')
    assert result is True
    assert len(selection.users_with_at) == 0
    
    # Попытка удалить несуществующего пользователя
    result = selection.remove_user('user3', 'User3')
    assert result is False
    
    print("✅ test_user_selection_remove passed")


def test_keyboard_factory():
    """Тест создания клавиатуры"""
    # Создание клавиатуры для 3 товаров
    keyboard = KeyboardFactory.create_product_selection_keyboard(3)
    
    # Проверка наличия кнопок
    assert keyboard is not None
    assert len(keyboard.keyboard) == 4  # 3 товара + кнопка "Просуммировать"
    
    print("✅ test_keyboard_factory passed")


def test_callback_data():
    """Тест создания и парсинга callback данных"""
    # Создание callback данных
    data = KeyboardFactory.create_callback_data('choice', 'plus', 1)
    
    # Парсинг обратно
    parsed = KeyboardFactory.parse_callback_data(data)
    
    assert parsed['method'] == 'choice'
    assert parsed['type'] == 'plus'
    assert parsed['number'] == 1
    
    print("✅ test_callback_data passed")


def test_calculate_user_totals():
    """Тест расчета итоговых сумм"""
    message = """Список продуктов из чека:
1. Название: Хлеб, Цена: 50.0 р., Количество: 2
Выбрали: @user1 (1), user2 (1), Всего: 2
2. Название: Молоко, Цена: 60.0 р., Количество: 1
Выбрали: @user1 (1), Всего: 1"""
    
    totals = MessageFormatter.calculate_user_totals(message)
    
    # user1: (50*2)*(1/2) + (60*1)*(1/1) = 50 + 60 = 110
    # user2: (50*2)*(1/2) = 50
    # Расчет исправлен: используется total_selected для деления
    assert '@user1' in totals
    assert 'user2' in totals
    assert abs(totals['@user1'] - 110.0) < 0.01
    assert abs(totals['user2'] - 50.0) < 0.01
    
    print("✅ test_calculate_user_totals passed")


def run_all_tests():
    """Запуск всех тестов"""
    print("\n🧪 Запуск тестов...\n")
    
    test_message_formatter()
    test_parse_message_lines()
    test_extract_quantity()
    test_extract_total_selected()
    test_extract_users()
    test_user_selection_add()
    test_user_selection_remove()
    test_keyboard_factory()
    test_callback_data()
    test_calculate_user_totals()
    
    print("\n✅ Все тесты пройдены успешно!\n")


if __name__ == '__main__':
    run_all_tests()
