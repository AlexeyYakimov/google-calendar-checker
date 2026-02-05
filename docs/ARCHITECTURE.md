# Архитектура проекта

## Схема

```
┌─────────────────────────────┐
│  run.py                     │
│  ┌───────────────────────┐  │
│  │ CalendarPoller         │  │  ← Опрос Google Calendar каждые 30 мин
│  │ (calendar_checker)     │  │     Обогащает события (duration_minutes)
│  └───────────┬────────────┘  │
└──────────────│───────────────┘
               │
               │ save_events_to_cache()
               ▼
        events_cache.json     ← Общий файл-кэш
               │
               │ load_events_from_cache()
               ▼
┌─────────────────────────────┐
│  run.py                     │
│  ┌───────────────────────┐  │
│  │ EventNotifier         │  │  ← Читает кэш, планирует уведомления
│  │ (notifier)            │  │     POST в Home Assistant в момент начала
│  └───────────────────────┘  │
└─────────────────────────────┘
```

Один процесс `run.py`: в фоне — CalendarPoller, в основном потоке — EventNotifier.

---

## Модули

| Модуль | Ответственность |
|--------|-----------------|
| **calendar_checker** | OAuth, запросы к Google Calendar, расчёт `duration_minutes`, запись в кэш |
| **notifier** | Чтение кэша, планирование уведомлений по времени начала, POST в webhook |

Длительность считается только в `calendar_checker`; notifier использует готовое поле `duration_minutes` из кэша.

---

## Поток данных (run.py)

```
CalendarPoller (фоновый поток)
  └─> poll_calendar() [каждые 30 мин, в рабочие часы]
        └─> get_today_events(service, enrich=True)
        └─> save_events_to_cache(events)
              └─> events_cache.json

EventNotifier (основной поток)
  └─> refresh_events() [периодически]
        └─> load_events_from_cache()
        └─> для каждого события: запланировать уведомление на start
        └─> в момент начала: POST {"duration": N, "name": "..."} → WEBHOOK_URL
```

---

## Кэш (events_cache.json)

```json
{
  "updated_at": "2026-02-05T10:30:00Z",
  "event_count": 3,
  "metadata": { "source": "calendar_poller", "timezone": "Europe/Moscow" },
  "events": [
    {
      "id": "abc123",
      "summary": "Встреча",
      "start": {"dateTime": "2026-02-05T14:00:00Z"},
      "end": {"dateTime": "2026-02-05T14:45:00Z"},
      "duration_minutes": 45
    }
  ]
}
```

Обновляется poller’ом; notifier только читает. Один источник правды для событий на день, без повторных запросов к API при уведомлениях.
