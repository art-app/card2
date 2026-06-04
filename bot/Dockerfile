FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# BOT_TOKEN и WEBAPP_URL приходят из окружения (docker-compose).
CMD ["python", "bot.py"]
