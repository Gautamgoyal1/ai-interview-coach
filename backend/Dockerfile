FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements-linux.lock .
RUN python -m pip install --no-cache-dir --upgrade "pip>=26.2.0" && python -m pip install --no-cache-dir -r requirements-linux.lock
COPY . .
RUN useradd --create-home --uid 10001 prepmate
USER prepmate
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --forwarded-allow-ips \"${FORWARDED_ALLOW_IPS:-}\""]
