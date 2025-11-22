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
        
    def get_receipt_from_qr(self, qr_data: str) -> tuple[pd.DataFrame, dict]:
        """Получение данных чека по QR-коду"""
        try:
            data = {
                'token': self.token,
                'qrraw': qr_data
            }
            response = requests.post(self.url, data=data, timeout=config.API_TIMEOUT)
            response.raise_for_status()
            
            result = json.loads(response.text)
            return self._parse_receipt_data(result), self._extract_metadata(result)
            
        except requests.RequestException as e:
            raise ReceiptAPIError(f"Ошибка при запросе к API: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ReceiptAPIError(f"Ошибка при разборе ответа API: {e}")
    
    def get_receipt_from_file(self, file_bytes: bytes) -> tuple[pd.DataFrame, dict]:
        """Получение данных чека по файлу изображения"""
        try:
            data = {'token': self.token}
            files = {'qrfile': file_bytes}
            
            response = requests.post(self.url, data=data, files=files, timeout=config.API_TIMEOUT)
            response.raise_for_status()
            
            result = json.loads(response.text)
            return self._parse_receipt_data(result), self._extract_metadata(result)
            
        except requests.RequestException as e:
            raise ReceiptAPIError(f"Ошибка при запросе к API: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ReceiptAPIError(f"Ошибка при разборе ответа API: {e}")
    
    @staticmethod
    def _parse_receipt_data(api_response: dict) -> pd.DataFrame:
        """Разбор ответа API и формирование таблицы товаров"""
        df = pd.json_normalize(api_response['data']['json']['items'])
        # Конвертация копеек в рубли
        df['price'] = df['price'].apply(lambda x: x / 100.0)
        return df[['name', 'price', 'quantity']]
    
    @staticmethod
    def _extract_metadata(api_response: dict) -> dict:
        """Извлечение метаданных чека"""
        data = api_response.get('data', {})
        json_data = data.get('json', {})
        
        metadata = {}
        
        # Извлекаем общую сумму (конвертируем копейки в рубли)
        if 'totalSum' in json_data:
            metadata['total_sum'] = json_data['totalSum'] / 100.0
        
        # Извлекаем адрес магазина
        if 'retailPlaceAddress' in data:
            metadata['store_address'] = data['retailPlaceAddress']
        
        # Извлекаем название магазина
        if 'user' in data:
            metadata['store_name'] = data['user']
        
        return metadata
