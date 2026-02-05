"""
Модуль для кэширования событий календаря.
Кэш считается актуальным только в рамках одной рабочей сессии (один календарный день в настроенном timezone).
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Путь к файлу кэша (относительно корня проекта)
CACHE_FILE = 'events_cache.json'


def save_events_to_cache(events: List[Dict], metadata: Optional[Dict] = None):
    """
    Сохранить события в кэш файл.
    
    Args:
        events: Список событий из Google Calendar
        metadata: Дополнительные метаданные (время обновления, источник и т.д.)
    """
    cache_data = {
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'event_count': len(events),
        'metadata': metadata or {},
        'events': events
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Сохранено {len(events)} событий в кэш")
    except Exception as e:
        logger.error(f"Ошибка сохранения кэша: {e}")


def load_events_from_cache(timezone=None) -> List[Dict]:
    """
    Загрузить события из кэш файла.
    Кэш хранится не дольше одной рабочей сессии (один календарный день).
    Если кэш от предыдущего дня (в заданном timezone) — файл перезаписывается пустым и возвращается [].
    
    Args:
        timezone: pytz timezone или None. Если задан — проверяется, что кэш от сегодня; иначе без проверки сессии.
    
    Returns:
        Список событий или пустой список если кэш недоступен / устарел
    """
    if not os.path.exists(CACHE_FILE):
        logger.warning(f"Файл кэша не найден: {CACHE_FILE}")
        return []
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        events = cache_data.get('events', [])
        updated_at_str = cache_data.get('updated_at')
        
        if timezone is not None and updated_at_str:
            try:
                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                updated_at_local = updated_at.astimezone(timezone)
                today_local = datetime.now(timezone).date()
                if updated_at_local.date() < today_local:
                    logger.info("Кэш от предыдущего дня — сессия истекла, очищаем кэш")
                    save_events_to_cache([], {'reason': 'new_session', 'previous_updated_at': updated_at_str})
                    return []
            except Exception as e:
                logger.warning(f"Не удалось проверить дату кэша: {e}")
        
        logger.info(f"✓ Загружено {len(events)} событий из кэша (обновлено: {updated_at_str or 'unknown'})")
        return events
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга кэша: {e}")
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки кэша: {e}")
        return []


def get_cache_info() -> Optional[Dict]:
    """
    Получить информацию о кэше.
    
    Returns:
        Словарь с метаданными кэша или None если кэш недоступен
    """
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        return {
            'updated_at': cache_data.get('updated_at'),
            'event_count': cache_data.get('event_count', 0),
            'metadata': cache_data.get('metadata', {}),
            'file_size': os.path.getsize(CACHE_FILE)
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о кэше: {e}")
        return None


def is_cache_fresh(max_age_seconds: int = 1800) -> bool:
    """
    Проверить актуальность кэша.
    
    Args:
        max_age_seconds: Максимальный возраст кэша в секундах (по умолчанию 30 минут)
        
    Returns:
        True если кэш свежий, False если устарел или недоступен
    """
    info = get_cache_info()
    if not info:
        return False
    
    try:
        updated_at = datetime.fromisoformat(info['updated_at'].replace('Z', '+00:00'))
        age_seconds = (datetime.utcnow() - updated_at.replace(tzinfo=None)).total_seconds()
        
        is_fresh = age_seconds < max_age_seconds
        if not is_fresh:
            logger.info(f"Кэш устарел: {int(age_seconds)}с > {max_age_seconds}с")
        
        return is_fresh
    except Exception as e:
        logger.error(f"Ошибка проверки актуальности кэша: {e}")
        return False
