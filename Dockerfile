# Google Calendar Checker — run poller + notifier in one container
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY calendar_checker/ calendar_checker/
COPY notifier/ notifier/
COPY run.py .

# credentials.json, token.json and .env are not in image — mount or pass at run
# Example: docker run -v ./calendar_checker/credentials.json:/app/calendar_checker/credentials.json ...
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
