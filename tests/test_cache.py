#!/usr/bin/env python3
"""
Тест работы кэша событий
"""

import json
from calendar_checker.cache import (
    save_events_to_cache,
    load_events_from_cache,
    get_cache_info,
    is_cache_fresh
)


def test_cache():
    """Проверить работу кэша."""
    print("=" * 60)
    print("Тест кэша событий")
    print("=" * 60)
    print()
    
    # Проверка существования кэша
    print("1. Проверка кэша:")
    print("-" * 60)
    info = get_cache_info()
    
    if info:
        print(f"✓ Кэш найден")
        print(f"  Обновлен: {info['updated_at']}")
        print(f"  События: {info['event_count']}")
        print(f"  Размер файла: {info['file_size']} байт")
        
        # Проверка метаданных
        metadata = info.get('metadata', {})
        if metadata:
            print(f"  Источник: {metadata.get('source', 'unknown')}")
            print(f"  Timezone: {metadata.get('timezone', 'unknown')}")
        
        # Проверка актуальности
        if is_cache_fresh(max_age_seconds=1800):
            print(f"  ✓ Кэш актуален (< 30 минут)")
        else:
            print(f"  ⚠ Кэш устарел (> 30 минут)")
    else:
        print("✗ Кэш не найден")
        print("  Запустите server.py для создания кэша")
    print()
    
    # Загрузка событий
    print("2. Загрузка событий из кэша:")
    print("-" * 60)
    events = load_events_from_cache()
    
    if events:
        print(f"✓ Загружено {len(events)} событий")
        print()
        print("Примеры событий:")
        for i, event in enumerate(events[:3], 1):
            name = event.get('summary', 'Без названия')
            duration = event.get('duration_minutes')
            start = event.get('start', {}).get('dateTime', 'unknown')
            
            print(f"  {i}. {name}")
            if duration:
                print(f"     Длительность: {duration} мин")
            print(f"     Начало: {start}")
    else:
        print("✗ События не найдены")
    print()
    
    # Тест записи (опционально)
    print("3. Тест записи в кэш:")
    print("-" * 60)
    test_events = [
        {
            'id': 'test123',
            'summary': 'Тестовое событие',
            'start': {'dateTime': '2026-02-05T14:00:00Z'},
            'end': {'dateTime': '2026-02-05T15:00:00Z'},
            'duration_minutes': 60
        }
    ]
    
    try:
        save_events_to_cache(
            test_events,
            metadata={'source': 'test_script', 'test': True}
        )
        print("✓ Тестовые данные сохранены")
        
        # Загрузить обратно
        loaded = load_events_from_cache()
        if loaded and loaded[0]['summary'] == 'Тестовое событие':
            print("✓ Тестовые данные загружены корректно")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    print()
    
    # Итог
    print("=" * 60)
    if info and events:
        print("✓ КЭШ РАБОТАЕТ КОРРЕКТНО!")
        print()
        print("Архитектура:")
        print("  server.py → events_cache.json → notifier_server.py")
    else:
        print("⚠ Кэш не готов")
        print()
        print("Для работы notifier нужно:")
        print("1. Запустить server.py (создаст кэш)")
        print("2. Дождаться первого опроса календаря")
        print("3. Запустить notifier_server.py (будет читать кэш)")
    print("=" * 60)


if __name__ == '__main__':
    test_cache()
