# Документация Google Calendar Checker

Сервис интеграции Google Calendar с Home Assistant: опрос календаря по расписанию и отправка уведомлений в webhook при начале события.

---

## Docker

Положите **`credentials.json`** и **`token.json`** в корень проекта; они монтируются в контейнер в `/app/calendar_checker/`. Создайте файлы до первого запуска (иначе Docker создаст каталоги с такими именами).

```bash
# Один раз на хосте: python setup.py, затем скопировать в корень
cp calendar_checker/credentials.json calendar_checker/token.json .

docker build -t google-calendar-checker .
docker run --rm -it \
  -v "$(pwd)/credentials.json:/app/calendar_checker/credentials.json" \
  -v "$(pwd)/token.json:/app/calendar_checker/token.json" \
  --env-file .env \
  google-calendar-checker
```

Или через Docker Compose (из корня проекта):

```bash
docker compose up -d
```

---

## Быстрый старт

### 1. Установка

```bash
pip install -r requirements.txt
```

### 2. Google Calendar API

1. [Google Cloud Console](https://console.cloud.google.com/) → создать проект → включить **Google Calendar API**
2. Создать OAuth 2.0 Client ID (тип: Desktop)
3. Скачать credentials и сохранить как `calendar_checker/credentials.json`

### 3. Переменные окружения

```bash
cp .env.example .env
```

Минимально в `.env` нужно указать:

```bash
WEBHOOK_URL=http://IP-HOME-ASSISTANT:8123/api/webhook/ВАШ-WEBHOOK-ID
TIMEZONE=Europe/Moscow
```

Остальное опционально (см. таблицу ниже).

### 4. Первичная настройка (один раз)

```bash
python setup.py
```

Откроется браузер для входа в Google. После авторизации создастся `calendar_checker/token.json`.

### 5. Запуск сервиса

```bash
python run.py
```

Сервис будет:
- опрашивать календарь каждые 30 минут (в :00 и :30) с 9:00 до 19:00 по выбранному часовому поясу;
- сохранять события в `events_cache.json`;
- отправлять POST в Home Assistant в момент начала каждого события.

Остановка: `Ctrl+C`.

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| **WEBHOOK_URL** | URL webhook в Home Assistant | — |
| **TIMEZONE** | Часовой пояс (например Europe/Moscow) | Europe/Moscow |
| **HTTP_TIMEOUT** | Таймаут HTTP (сек) | 10 |
| **POLL_START_HOUR** | Час начала опроса | 9 |
| **POLL_END_HOUR** | Час окончания опроса | 19 |
| **POLL_INTERVAL_MINUTES** | Интервал опроса (мин) | 30 |
| **CREDENTIALS_FILE** | Путь к credentials.json | calendar_checker/credentials.json |
| **TOKEN_FILE** | Путь к token.json | calendar_checker/token.json |
| **CALENDAR_ID** | ID календаря | primary |

Пример полного `.env`:

```bash
WEBHOOK_URL=http://192.168.1.100:8123/api/webhook/abc123
TIMEZONE=Europe/Moscow
HTTP_TIMEOUT=10
POLL_START_HOUR=9
POLL_END_HOUR=19
POLL_INTERVAL_MINUTES=30
```

---

## Home Assistant

### Создание webhook

1. **Настройки** → **Автоматизации и сцены** → **Создать автоматизацию** → **Пустая**
2. Триггер: **Webhook** → скопировать Webhook ID
3. В `.env` указать: `WEBHOOK_URL=http://ВАШ-IP:8123/api/webhook/ВАШ-ID`

### Формат POST запроса

В момент начала события сервис отправляет JSON:

```json
{
  "duration": 45,
  "name": "Встреча с командой"
}
```

### Пример автоматизации

```yaml
automation:
  - alias: "Событие календаря"
    trigger:
      - platform: webhook
        webhook_id: "YOUR-WEBHOOK-ID"
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.json.name }} ({{ trigger.json.duration }} мин)"
```

---

## Проверка и тесты

```bash
# Проверка конфигурации
python tests/check_config.py

# Загрузка переменных из .env
python tests/test_env_loading.py

# Кэш событий
python tests/test_cache.py
```

---

## Структура проекта

```
google_calendar_checker/
├── calendar_checker/    # Работа с Google Calendar, кэш
├── notifier/            # Уведомления в Home Assistant
├── docs/                # Документация и архитектура
├── tests/               # Тесты и проверки
├── setup.py             # OAuth (один раз)
├── run.py               # Запуск сервиса
├── .env.example         # Шаблон .env
└── requirements.txt
```

Подробная схема работы и поток данных — в [ARCHITECTURE.md](ARCHITECTURE.md).
