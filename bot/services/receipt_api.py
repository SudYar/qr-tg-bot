"""
Сервис работы с API Proverkacheka
"""

import json
import requests
import pandas as pd
from typing import Optional
from ..config import config


class ReceiptAPIError(Exception):
    """Исключение при работе с API чеков"""
    pass


class ReceiptAPI:
    """Класс для взаимодействия с API Proverkacheka"""
    
    def __init__(self):
        """Инициализация API клиента"""
        self.token = config.PROVERKACHEKA_TOKEN
        self.url = config.PROVERKACHEKA_URL
        
    def get_receipt_from_qr(self, qr_data: str) -> pd.DataFrame:
        """
        Получение данных чека по QR-коду
        
        Args:
            qr_data: Строка с данными QR-кода
            
        Returns:
            pd.DataFrame: Таблица с товарами из чека
            
        Raises:
            ReceiptAPIError: При ошибке запроса к API
        """
        try:
            data = {
                'token': self.token,
                'qrraw': qr_data
            }
            response = requests.post(self.url, data=data, timeout=10)
            response.raise_for_status()
            
            result = json.loads(response.text)
            return self._parse_receipt_data(result)
            
        except requests.RequestException as e:
            raise ReceiptAPIError(f"Ошибка при запросе к API: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ReceiptAPIError(f"Ошибка при разборе ответа API: {e}")
    
    def get_receipt_from_file(self, file_bytes: bytes) -> pd.DataFrame:
        """
        Получение данных чека по файлу изображения
        
        Args:
            file_bytes: Изображение с QR-кодом в байтах
            
        Returns:
            pd.DataFrame: Таблица с товарами из чека
            
        Raises:
            ReceiptAPIError: При ошибке запроса к API
        """
        try:
            data = {'token': self.token}
            files = {'qrfile': file_bytes}
            
            response = requests.post(self.url, data=data, files=files, timeout=10)
            response.raise_for_status()
            
            result = json.loads(response.text)
            return self._parse_receipt_data(result)
            
        except requests.RequestException as e:
            raise ReceiptAPIError(f"Ошибка при запросе к API: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ReceiptAPIError(f"Ошибка при разборе ответа API: {e}")
    
    @staticmethod
    def _parse_receipt_data(api_response: dict) -> pd.DataFrame:
        """
        Разбор ответа API и формирование таблицы товаров
        
        Args:
            api_response: Ответ от API в формате словаря
            
        Returns:
            pd.DataFrame: Таблица с колонками name, price, quantity
        """
        df = pd.json_normalize(api_response['data']['json']['items'])
        # Конвертация цены из копеек в рубли
        df['price'] = df['price'].apply(lambda x: x / 100.0)
        return df[['name', 'price', 'quantity']]
