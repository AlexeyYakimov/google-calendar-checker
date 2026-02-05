"""
Модуль для отправки POST запросов в Home Assistant webhook
"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WebhookSender:
    """
    Класс для отправки уведомлений в Home Assistant webhook.
    """
    
    def __init__(self, webhook_url: str, timeout: int = 10):
        """
        Инициализация отправителя webhook.
        
        Args:
            webhook_url: URL webhook в Home Assistant
            timeout: Таймаут для HTTP запросов в секундах
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
    
    def send(self, data: Dict[str, Any]) -> bool:
        """
        Отправить POST запрос с данными в webhook.
        
        Args:
            data: Словарь с данными для отправки
            
        Returns:
            True если отправка успешна, False в противном случае
        """
        logger.info(f"Отправка POST запроса в: {self.webhook_url}")
        logger.debug(f"Данные: {data}")
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Успешно отправлено (status: {response.status_code})")
                return True
            else:
                logger.warning(f"⚠ Webhook вернул статус: {response.status_code}")
                logger.warning(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"✗ Таймаут - webhook не ответил за {self.timeout} секунд")
            return False
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"✗ Ошибка подключения: {e}")
            return False
            
        except Exception as e:
            logger.error(f"✗ Ошибка отправки: {e}")
            return False
