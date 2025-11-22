"""
Сервис сканирования QR-кодов
"""

import cv2
import numpy as np
from typing import Tuple


class QRScanner:
    """Класс для сканирования QR-кодов с изображений"""
    
    @staticmethod
    def scan_qr_code(image_bytes: bytes) -> Tuple[str, bool]:
        """
        Сканирование QR-кода из байтового представления изображения
        
        Args:
            image_bytes: Изображение в байтах
            
        Returns:
            Tuple[str, bool]: Кортеж (данные QR-кода, найден ли QR-код)
        """
        try:
            # Конвертация байтов в numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            if image is None:
                return '', False
            
            # Инициализация детектора QR-кода
            detector = cv2.QRCodeDetector()
            
            # Обнаружение и декодирование QR-кода
            data, bbox, _ = detector.detectAndDecode(image)
            
            has_qr = bbox is not None
            
            return data, has_qr
            
        except Exception as e:
            print(f"Ошибка при сканировании QR-кода: {e}")
            return '', False
