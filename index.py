"""
Обработчик для webhook (Yandex Cloud Functions, AWS Lambda и т.д.)
"""

from bot.bot import QRCheckBot

# Создание экземпляра бота
bot_instance = QRCheckBot()


def handler(event, context):
    """
    Обработчик событий для serverless функций
    
    Args:
        event: Событие от serverless платформы
        context: Контекст выполнения
        
    Returns:
        dict: Ответ для API Gateway
    """
    return bot_instance.process_update(event['body'])
