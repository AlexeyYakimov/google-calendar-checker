# Google Calendar Checker

Service that connects Google Calendar to Home Assistant: polls the calendar on a schedule and sends webhook notifications when events start.

**Docs:** [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) · **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Docker

Put `credentials.json` and `token.json` in the **project root**. Create them before the first run (otherwise Docker will create directories instead of files).

```bash
# After python setup.py, copy to root for Docker
cp calendar_checker/credentials.json calendar_checker/token.json .

# Build & run
docker build -t google-calendar-checker .
docker run --rm -it \
  -v "$(pwd)/credentials.json:/app/calendar_checker/credentials.json" \
  -v "$(pwd)/token.json:/app/calendar_checker/token.json" \
  --env-file .env \
  google-calendar-checker
```

Or use Docker Compose:

```bash
docker compose up -d
```

---

## Features

- **Polling**: Poll calendar at :00 and :30 of each hour (configurable)
- **Event notifications**: POST to Home Assistant webhook at each event start with `duration` and `name`
- **Timezone support**: Configurable (default Moscow, 9:00–19:00)
- **File cache**: Events cached in `events_cache.json`; notifier reads from cache (no duplicate API calls)
- **Modular**: `calendar_checker` (API + cache) and `notifier` (webhook sender)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env from template
cp .env.example .env
# Edit .env: set WEBHOOK_URL (and optionally TIMEZONE, POLL_*)

# 3. One-time OAuth setup
python setup.py

# 4. Run the service
python run.py
```

The service will:
- Poll Google Calendar every 30 minutes during configured hours
- Write events to `events_cache.json`
- Send POST to your Home Assistant webhook when each event starts

Stop with `Ctrl+C`.

**Full setup (Google API, .env, Home Assistant):** [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)

## Project Structure

```
google_calendar_checker/
├── calendar_checker/       # Google Calendar API, cache
│   ├── auth.py
│   ├── cache.py
│   ├── config.py
│   ├── operations.py
│   └── scheduler.py
├── notifier/               # Webhook notifications
│   ├── config.py
│   ├── event_notifier.py
│   └── webhook_sender.py
├── docs/
│   ├── DOCUMENTATION.md
│   └── ARCHITECTURE.md
├── tests/
│   ├── check_config.py
│   └── test_*.py
├── setup.py                # One-time OAuth
├── run.py                  # Run service
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBHOOK_URL` | Home Assistant webhook URL | — |
| `TIMEZONE` | Timezone (e.g. Europe/Moscow) | Europe/Moscow |
| `HTTP_TIMEOUT` | HTTP timeout (seconds) | 10 |
| `POLL_START_HOUR` / `POLL_END_HOUR` | Polling window | 9, 19 |
| `POLL_INTERVAL_MINUTES` | Poll interval | 30 |

See [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) for the full list.

## Webhook payload

When an event starts, the service sends:

```json
{
  "duration": 45,
  "name": "Team meeting"
}
```

## Testing

```bash
python tests/check_config.py      # Config check
python tests/test_env_loading.py  # .env loading
python tests/test_cache.py        # Cache
python tests/test_enrichment.py   # Event enrichment
```

## Home Assistant example

```yaml
automation:
  - alias: "Calendar event started"
    trigger:
      - platform: webhook
        webhook_id: "YOUR-WEBHOOK-ID"
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.json.name }} ({{ trigger.json.duration }} min)"
```

More examples in [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md#home-assistant).

## Debug

Test webhook manually:

```bash
curl -X POST http://YOUR-HA-IP:8123/api/webhook/YOUR-WEBHOOK-ID \
  -H "Content-Type: application/json" \
  -d '{"duration": 30, "name": "Test"}'
```

Run with logs to file:

```bash
python run.py > service.log 2>&1
```

## Requirements

- Python 3.7+
- Google Calendar API credentials (OAuth 2.0)
- Home Assistant (for webhook)
- Network access to Google API and Home Assistant
