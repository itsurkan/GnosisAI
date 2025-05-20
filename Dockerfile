FROM python:3.13-alpine

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY .env /app/.env
WORKDIR /app

COPY requirements.txt /app/
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY . /app


RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
