"""
Основной модуль для мониторинга событий календаря и отправки уведомлений
"""

import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from calendar_checker.cache import load_events_from_cache, get_cache_info
from .webhook_sender import WebhookSender

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventNotifier:
    """
    Сервис мониторинга событий календаря и отправки уведомлений в Home Assistant.
    """
    
    def __init__(self, webhook_url: str, timezone: str = 'Europe/Moscow', http_timeout: int = 10):
        """
        Инициализация notifier.
        
        Args:
            webhook_url: URL webhook в Home Assistant
            timezone: Часовой пояс для планировщика
            http_timeout: Таймаут для HTTP запросов
        """
        self.webhook_sender = WebhookSender(webhook_url, timeout=http_timeout)
        self.timezone = pytz.timezone(timezone)
        self.scheduler = BlockingScheduler(timezone=self.timezone)
        self.scheduled_events = set()
    
    def _send_event_notification(self, event_id: str, event_name: str, duration: int):
        """
        Отправить уведомление о событии в webhook.
        
        Args:
            event_id: ID события
            event_name: Название события
            duration: Длительность в минутах
        """
        notification = {
            "duration": duration,
            "name": event_name
        }
        
        logger.info("=" * 60)
        logger.info("🔔 СОБЫТИЕ НАЧИНАЕТСЯ!")
        logger.info(f"Название: {event_name}")
        logger.info(f"Длительность: {duration} минут")
        
        # Отправка POST запроса
        success = self.webhook_sender.send(notification)
        
        if not success:
            logger.error("Не удалось отправить уведомление")
        
        logger.info("=" * 60)
        
        # Удалить из списка запланированных
        self.scheduled_events.discard(event_id)
    
    def _schedule_event(self, event: dict):
        """
        Запланировать уведомление для события.
        
        Args:
            event: Объект события из календаря (обогащенный полем duration_minutes)
        """
        if not isinstance(event, dict):
            return
        
        event_id = event.get('id')
        if not event_id:
            logger.debug("Пропуск события без id")
            return
        
        if event.get('status') == 'cancelled':
            logger.info(f"Пропуск отменённого события: {event.get('summary', '?')}")
            return
        
        start_obj = event.get('start')
        if not isinstance(start_obj, dict):
            logger.debug("Пропуск события без start")
            return
        
        start_datetime_str = start_obj.get('dateTime')
        event_name = event.get('summary', 'Без названия')
        
        if not start_datetime_str:
            logger.info(f"Пропуск события на весь день: {event_name}")
            return
        
        if event_id in self.scheduled_events:
            return
        
        try:
            start_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            logger.warning(f"Некорректное время начала события: {event_name}")
            return
        
        start_dt_local = start_dt.astimezone(self.timezone)
        now = datetime.now(self.timezone)
        if start_dt_local < now:
            logger.info(f"Пропуск прошедшего события: {event_name} (начало в {start_dt_local.strftime('%H:%M')})")
            return
        
        duration = event.get('duration_minutes')
        if duration is None:
            logger.info(f"Пропуск события без длительности: {event_name}")
            return
        
        job_id = f"event_{event_id}"
        self.scheduler.add_job(
            self._send_event_notification,
            'date',
            run_date=start_dt_local,
            args=[event_id, event_name, duration],
            id=job_id,
            replace_existing=True
        )
        self.scheduled_events.add(event_id)
        logger.info(f"✓ Запланировано: '{event_name}' в {start_dt_local.strftime('%H:%M')} ({duration} мин)")
    
    def refresh_events(self):
        """
        Обновить список событий на сегодня и запланировать уведомления.
        Читает события из кэша, созданного calendar_checker.
        """
        try:
            logger.info("=" * 60)
            logger.info("Обновление событий из кэша...")
            
            # Получить информацию о кэше
            cache_info = get_cache_info()
            if cache_info:
                updated_at = cache_info.get('updated_at', 'unknown')
                logger.info(f"Кэш обновлен: {updated_at}")
            else:
                logger.warning("Кэш не найден - ждем обновления от calendar_checker")
            
            # Загрузить события из кэша (только за текущую сессию — один рабочий день)
            events = load_events_from_cache(timezone=self.timezone)
            
            if not events:
                logger.warning("Событий в кэше нет")
                logger.info("Убедитесь что calendar_checker (server.py) запущен")
            else:
                logger.info(f"Найдено событий: {len(events)}")
                for event in events:
                    self._schedule_event(event)
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Ошибка обновления событий: {e}", exc_info=True)
    
    def start(self):
        """
        Запустить notifier сервис.
        """
        logger.info("=" * 60)
        logger.info("Запуск Event Notifier Service")
        logger.info(f"Часовой пояс: {self.timezone}")
        logger.info(f"Webhook URL: {self.webhook_sender.webhook_url}")
        logger.info("=" * 60)
        
        # Начальное обновление событий
        self.refresh_events()
        
        # Запланировать периодическое обновление в :00 и :30 каждого часа
        self.scheduler.add_job(
            self.refresh_events,
            'cron',
            minute='0,30',
            id='refresh_events',
            replace_existing=True
        )
        
        current_time = datetime.now(self.timezone)
        logger.info(f"Текущее время: {current_time.strftime('%H:%M:%S')}")
        logger.info("Обновление событий будет происходить в :00 и :30 каждого часа")
        logger.info("=" * 60)
        logger.info("Планировщик запущен. Нажмите Ctrl+C для остановки.")
        logger.info("")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Остановка планировщика...")
            self.scheduler.shutdown()
            logger.info("Планировщик остановлен.")
