FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (see .dockerignore for what's excluded)
COPY . .

# Normalize line endings (in case the script was checked out with CRLF on Windows)
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

# The entrypoint waits for the DB, runs migrations, seeds data, then starts the API
ENTRYPOINT ["/app/docker-entrypoint.sh"]
