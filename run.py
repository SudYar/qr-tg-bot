"""
Точка входа для запуска бота
"""

from bot.bot import QRCheckBot


if __name__ == '__main__':
    bot = QRCheckBot()
    bot.run(use_webhook=False)
