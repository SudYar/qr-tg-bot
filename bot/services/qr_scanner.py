"""
Сервис сканирования QR-кодов
"""

import cv2
import numpy as np
from typing import Tuple
from ..logger import logger


class QRScanner:
    """Класс для сканирования QR-кодов с изображений"""
    
    @staticmethod
    def scan_qr_code(image_bytes: bytes) -> Tuple[str, bool]:
        """Сканирование QR-кода из байтового представления изображения"""
        logger.debug(f"Начало сканирования QR-кода (размер изображения: {len(image_bytes)} байт)")
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            if image is None:
                logger.warning("Не удалось декодировать изображение")
                return '', False
            
            logger.debug(f"Изображение декодировано, размер: {image.shape}")
            
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(image)
            has_qr = bbox is not None
            
            if has_qr:
                logger.info(f"QR-код обнаружен, длина данных: {len(data)}")
            else:
                logger.info("QR-код не обнаружен на изображении")
            
            return data, has_qr
            
        except Exception as e:
            logger.error(f"Ошибка при сканировании QR-кода: {e}", exc_info=True)
            return '', False
