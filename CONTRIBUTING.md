# Руководство по разработке

Благодарим за интерес к проекту! Это руководство поможет вам внести свой вклад в развитие Telegram QR Check Bot.

## 📋 Содержание

- [Подготовка окружения](#подготовка-окружения)
- [Структура проекта](#структура-проекта)
- [Стандарты кода](#стандарты-кода)
- [Процесс разработки](#процесс-разработки)
- [Тестирование](#тестирование)
- [Документация](#документация)

## 🛠️ Подготовка окружения

### Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git

### Установка

1. Форк репозитория на GitHub

2. Клонирование форка:
```bash
git clone https://github.com/your-username/qr-tg-bot.git
cd qr-tg-bot
```

3. Создание виртуального окружения:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

4. Установка зависимостей:
```bash
pip install -r requirements.txt
```

5. Настройка конфигурации:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте свои токены
```

## 📁 Структура проекта

Ознакомьтесь с [ARCHITECTURE.md](ARCHITECTURE.md) для понимания архитектуры проекта.

Основные директории:
- `bot/handlers/` - обработчики сообщений и событий
- `bot/services/` - бизнес-логика и внешние сервисы
- `bot/utils/` - вспомогательные функции
- `bot/models/` - модели данных

## 📝 Стандарты кода

### Стиль кода

Проект следует [PEP 8](https://pep8.org/) - стандарту стиля кода Python.

#### Основные правила:

**Именование:**
- Классы: `PascalCase` (например, `MessageHandler`)
- Функции и переменные: `snake_case` (например, `handle_message`)
- Константы: `UPPER_SNAKE_CASE` (например, `API_TIMEOUT`)
- Приватные методы: `_leading_underscore` (например, `_process_data`)

**Строки:**
- Максимальная длина строки: 100 символов
- Используйте f-strings для форматирования

**Импорты:**
```python
# Стандартная библиотека
import os
import json

# Сторонние библиотеки
import telebot
import pandas as pd

# Локальные импорты
from .config import config
from .utils import MessageFormatter
```

### Документация кода

Все публичные функции и классы должны иметь docstrings:

```python
def process_receipt(receipt_data: dict) -> pd.DataFrame:
    """
    Обработка данных чека
    
    Args:
        receipt_data: Словарь с данными чека от API
        
    Returns:
        pd.DataFrame: Таблица с товарами
        
    Raises:
        ValueError: Если данные имеют неверный формат
    """
    pass
```

### Type Hints

Используйте аннотации типов для всех функций:

```python
from typing import List, Optional, Tuple

def get_users(message: str) -> Tuple[List[str], List[str]]:
    users_with_at: List[str] = []
    users_without_at: List[str] = []
    return users_with_at, users_without_at
```

## 🔄 Процесс разработки

### 1. Создание ветки

Создайте новую ветку для вашей функции:

```bash
git checkout -b feature/new-feature-name
# или
git checkout -b fix/bug-description
```

Префиксы:
- `feature/` - новая функциональность
- `fix/` - исправление ошибки
- `docs/` - изменения документации
- `refactor/` - рефакторинг кода

### 2. Внесение изменений

**Следуйте принципам:**
- **Single Responsibility** - один модуль делает одну вещь
- **DRY** (Don't Repeat Yourself) - избегайте дублирования
- **KISS** (Keep It Simple, Stupid) - простота важнее сложности

**Добавление новой функции:**

1. Определите, в какой модуль она логически вписывается
2. Создайте необходимые методы в соответствующих классах
3. Добавьте обработчик, если требуется
4. Обновите документацию

### 3. Коммиты

Используйте понятные сообщения коммитов:

```bash
git commit -m "Добавлена функция экспорта чека в PDF"
git commit -m "Исправлена ошибка при парсинге даты"
git commit -m "Обновлена документация API"
```

Формат сообщения:
```
<тип>: <краткое описание>

<детальное описание (опционально)>

<ссылки на issues (опционально)>
```

Типы:
- `feat:` - новая функция
- `fix:` - исправление
- `docs:` - документация
- `style:` - форматирование
- `refactor:` - рефакторинг
- `test:` - тесты

### 4. Pull Request

1. Убедитесь, что все тесты проходят
2. Обновите документацию, если нужно
3. Создайте Pull Request в основной репозиторий
4. Опишите изменения и их причину

## 🧪 Тестирование

### Запуск тестов

```bash
python test_basic.py
```

### Написание тестов

Создавайте тесты для новой функциональности:

```python
def test_new_feature():
    """Тест новой функции"""
    # Arrange (подготовка)
    data = prepare_test_data()
    
    # Act (действие)
    result = new_feature(data)
    
    # Assert (проверка)
    assert result == expected_result
    print("✅ test_new_feature passed")
```

### Что тестировать

- ✅ Основные функции и методы
- ✅ Граничные случаи
- ✅ Обработку ошибок
- ✅ Парсинг данных
- ✅ Форматирование вывода

### Что НЕ нужно тестировать

- ❌ Внешние API (используйте моки)
- ❌ Библиотечные функции
- ❌ Очевидный код

## 📚 Документация

### Обновление документации

При добавлении новой функциональности обновите:

1. **README.md** - если изменился процесс использования
2. **ARCHITECTURE.md** - если добавлены новые модули или изменена архитектура
3. **CHANGELOG.md** - добавьте запись об изменении

### Комментарии в коде

```python
# Хорошо: объясняет "почему"
# Используем max() для предотвращения деления на ноль
divisor = max(1, total_selected)

# Плохо: объясняет "что" (очевидно из кода)
# Прибавляем 1
counter += 1
```

## 🎯 Примеры вклада

### Добавление новой команды

```python
# 1. В bot/handlers/message_handlers.py
def handle_stats(self, message: Message) -> None:
    """Обработка команды /stats"""
    stats = self._get_statistics()
    self.bot.send_message(message.chat.id, stats)

# 2. В bot/bot.py, метод _register_handlers()
@self.bot.message_handler(commands=['stats'])
def handle_stats(message):
    self.message_handlers.handle_stats(message)
```

### Добавление нового сервиса

```python
# 1. Создайте bot/services/export_service.py
class ExportService:
    """Сервис экспорта данных"""
    
    def export_to_pdf(self, data: pd.DataFrame) -> bytes:
        """Экспорт данных в PDF"""
        # Реализация
        pass

# 2. Используйте в обработчике
from ..services.export_service import ExportService

self.export_service = ExportService()
```

### Улучшение существующей функции

```python
# До
def parse_users(text: str):
    # Простой парсинг
    return re.findall(r'@\w+', text)

# После
def parse_users(text: str) -> List[Tuple[str, int]]:
    """
    Парсинг пользователей с количеством
    
    Args:
        text: Текст для парсинга
        
    Returns:
        List[Tuple[str, int]]: Список (username, count)
    """
    pattern = re.compile(r'@(\w+)\s*\((\d+)\)')
    return [(m[0], int(m[1])) for m in pattern.findall(text)]
```

## ❓ Вопросы и помощь

Если у вас есть вопросы:

1. Проверьте документацию (README.md, ARCHITECTURE.md)
2. Посмотрите существующие Issues
3. Создайте новый Issue с описанием вопроса

## 🙏 Благодарности

Спасибо всем, кто вносит вклад в проект!

## 📄 Лицензия

Внося вклад в проект, вы соглашаетесь с условиями лицензии проекта.
