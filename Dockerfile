FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DATABASE_PATH=/app/data/app.sqlite3 \
    APP_TIMEZONE=America/Sao_Paulo \
    TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY wsgi.py ./

RUN mkdir -p /app/data
VOLUME ["/app/data"]

EXPOSE 8000

CMD ["python", "-m", "flask", "--app", "wsgi", "run", "--host=0.0.0.0", "--port=8000"]
