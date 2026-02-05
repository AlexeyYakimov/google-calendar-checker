# Notifier Module

Отдельный модуль для отправки уведомлений о событиях календаря в Home Assistant.

## Описание

Модуль `notifier` - это независимый компонент, который:
- Мониторит события из Google Calendar (через `calendar_checker`)
- Использует обогащенные события с уже рассчитанной длительностью от `calendar_checker`
- Отправляет POST запросы в Home Assistant webhook в момент начала каждого события
- Обновляет список событий каждые 30 минут
- Обрабатывает ошибки сети и таймауты

## Структура

```
notifier/
├── __init__.py           # Экспорты модуля
├── config.py             # Конфигурация (webhook URL, timezone, timeout)
├── event_notifier.py     # Основной класс EventNotifier
└── webhook_sender.py     # Класс WebhookSender для HTTP запросов
```

## Компоненты

### EventNotifier

Основной класс для мониторинга событий и планирования уведомлений.

**Основные методы:**
- `__init__(webhook_url, timezone, http_timeout)` - инициализация
- `start()` - запуск сервиса (блокирующий)
- `refresh_events()` - обновление списка событий
- `_schedule_event(event)` - планирование уведомления для события
- `_send_event_notification(event_id, event_name, duration)` - отправка уведомления

**Логика работы:**
1. При запуске загружает все события на сегодня
2. Планирует уведомления для каждого будущего события
3. В момент начала события отправляет POST запрос
4. Каждые 30 минут (:00 и :30) обновляет список событий

### WebhookSender

Класс для отправки HTTP POST запросов в webhook.

**Методы:**
- `__init__(webhook_url, timeout)` - инициализация
- `send(data)` - отправка POST запроса с данными

**Обработка ошибок:**
- Timeout (если webhook не отвечает)
- Connection errors (если webhook недоступен)
- HTTP errors (если webhook возвращает не 200)

## Конфигурация

Файл `config.py` содержит все настройки:

```python
# Home Assistant webhook URL
WEBHOOK_URL = 'http://homeassistant/api/webhook/YOUR-WEBHOOK-ID'

# Таймаут для HTTP запросов (в секундах)
HTTP_TIMEOUT = 10

# Часовой пояс для планировщика
TIMEZONE = 'Europe/Moscow'
```

## Использование

### Базовое использование

```python
from notifier import EventNotifier
from notifier.config import WEBHOOK_URL, TIMEZONE, HTTP_TIMEOUT

notifier = EventNotifier(
    webhook_url=WEBHOOK_URL,
    timezone=TIMEZONE,
    http_timeout=HTTP_TIMEOUT
)

notifier.start()  # Блокирующий вызов
```

### Кастомная конфигурация

```python
from notifier import EventNotifier

notifier = EventNotifier(
    webhook_url='http://192.168.1.100:8123/api/webhook/abc123',
    timezone='Asia/Tokyo',
    http_timeout=15
)

notifier.start()
```

## Формат данных

### POST запрос в webhook

```http
POST http://homeassistant/api/webhook/YOUR-ID
Content-Type: application/json

{
  "duration": 45,
  "name": "Встреча с командой"
}
```

**Поля:**
- `duration` (int): Длительность события в минутах
- `name` (str): Название события из календаря

## Логирование

Модуль использует стандартный Python logging:

```python
2026-02-05 14:30:00 - notifier.event_notifier - INFO - 🔔 СОБЫТИЕ НАЧИНАЕТСЯ!
2026-02-05 14:30:00 - notifier.event_notifier - INFO - Название: Встреча
2026-02-05 14:30:00 - notifier.event_notifier - INFO - Длительность: 45 минут
2026-02-05 14:30:00 - notifier.webhook_sender - INFO - Отправка POST запроса в: http://...
2026-02-05 14:30:01 - notifier.webhook_sender - INFO - ✓ Успешно отправлено (status: 200)
```

## Зависимости

- `requests` - для HTTP запросов
- `APScheduler` - для планирования задач
- `pytz` - для работы с часовыми поясами
- `calendar_checker` - для получения событий из Google Calendar

## Примеры интеграции

### Запуск как systemd сервис (Linux)

```ini
[Unit]
Description=Calendar Event Notifier
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/google_calendar_checker
ExecStart=/usr/bin/python3 notifier_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Запуск в Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "notifier_server.py"]
```

## Отладка

### Тест подключения к webhook

```bash
curl -X POST http://homeassistant/api/webhook/YOUR-ID \
  -H "Content-Type: application/json" \
  -d '{"duration": 30, "name": "Test Event"}'
```

### Проверка логов

```bash
# Запуск с выводом в файл
python notifier_server.py > notifier.log 2>&1

# Просмотр логов в реальном времени
tail -f notifier.log
```

### Увеличение уровня логирования

В начале `event_notifier.py` измените:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Было: INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Возможные проблемы

### "Connection error" в логах
- Проверьте доступность Home Assistant по сети
- Проверьте правильность URL в config.py
- Проверьте firewall правила

### "Request timeout"
- Увеличьте `HTTP_TIMEOUT` в config.py
- Проверьте нагрузку на Home Assistant

### События не отправляются
- Убедитесь что события есть в календаре на сегодня
- Проверьте что события не в прошлом
- Проверьте логи на наличие ошибок при получении событий

## Лицензия

MIT
