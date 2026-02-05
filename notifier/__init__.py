"""
Notifier - модуль для отправки уведомлений о событиях календаря в Home Assistant
"""

from .event_notifier import EventNotifier
from .config import WEBHOOK_URL

__all__ = ['EventNotifier', 'WEBHOOK_URL']
__version__ = '1.0.0'
