#!/usr/bin/env python3
"""
Запуск сервиса Google Calendar Checker

Сервис выполняет:
1. Опрос Google Calendar каждые 30 минут (9:00-19:00 по Москве)
2. Кэширование событий в events_cache.json
3. Отправка уведомлений в Home Assistant при начале события

Запуск:
    python run.py
"""

import logging
import signal
import sys
import time
from threading import Thread

from calendar_checker.scheduler import CalendarPoller
from calendar_checker.cache import is_cache_fresh
from calendar_checker.config import POLL_START_HOUR, POLL_END_HOUR, POLL_INTERVAL_MINUTES
from notifier import EventNotifier
from notifier.config import WEBHOOK_URL, TIMEZONE, HTTP_TIMEOUT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalendarService:
    """
    Главный сервис, объединяющий poller и notifier.
    """
    
    def __init__(self):
        """Инициализация сервиса."""
        self.poller = None
        self.notifier = None
        self.poller_thread = None
        
    def start(self):
        """Запустить сервис."""
        logger.info("=" * 60)
        logger.info("Запуск Google Calendar Service")
        logger.info("=" * 60)
        logger.info("")
        
        # Создать Calendar Poller
        logger.info("Инициализация Calendar Poller...")
        self.poller = CalendarPoller(
            timezone=TIMEZONE,
            start_hour=POLL_START_HOUR,
            end_hour=POLL_END_HOUR,
            interval_minutes=POLL_INTERVAL_MINUTES
        )
        
        # Создать Event Notifier
        logger.info("Инициализация Event Notifier...")
        self.notifier = EventNotifier(
            webhook_url=WEBHOOK_URL,
            timezone=TIMEZONE,
            http_timeout=HTTP_TIMEOUT
        )
        
        logger.info("")
        logger.info("Конфигурация:")
        logger.info(f"  Timezone: {TIMEZONE}")
        logger.info(f"  Часы работы: {POLL_START_HOUR}:00-{POLL_END_HOUR}:00")
        logger.info(f"  Интервал опроса: каждые {POLL_INTERVAL_MINUTES} минут")
        logger.info(f"  Webhook URL: {WEBHOOK_URL}")
        logger.info(f"  HTTP Timeout: {HTTP_TIMEOUT}s")
        logger.info("")
        logger.info("=" * 60)
        logger.info("")
        
        # Обработка Ctrl+C
        def signal_handler(sig, frame):
            logger.info("")
            logger.info("Получен сигнал остановки...")
            logger.info("Остановка сервиса...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запустить poller в отдельном потоке
        logger.info("Запуск Calendar Poller в фоновом потоке...")
        self.poller_thread = Thread(target=self.poller.start, daemon=True)
        self.poller_thread.start()
        
        # Дождаться первого обновления кэша, чтобы notifier не стартовал по старому кэшу
        logger.info("Ожидание первого опроса календаря (до 30 сек)...")
        for _ in range(15):
            time.sleep(2)
            if is_cache_fresh(max_age_seconds=60):
                logger.info("Кэш обновлён, запуск Notifier.")
                break
        else:
            logger.info("Таймаут ожидания кэша, запуск Notifier (возможен старый/пустой кэш).")
        
        # Запустить notifier в главном потоке (блокирующий)
        logger.info("Запуск Event Notifier...")
        logger.info("")
        try:
            self.notifier.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("")
            logger.info("Сервис остановлен")


def main():
    """Точка входа."""
    service = CalendarService()
    service.start()


if __name__ == '__main__':
    main()
