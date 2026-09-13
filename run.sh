#!/usr/bin/env bash
# Run the whole Game Item Store (PostgreSQL + API + Angular) with Docker.
# Usage:
#   ./run.sh          start (build if needed)
#   ./run.sh fresh    wipe the database and start completely from scratch
#   ./run.sh stop     stop everything
set -e

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but was not found. Install Docker Desktop first."
  exit 1
fi

case "${1:-start}" in
  stop)
    docker compose down
    echo "Stopped."
    exit 0
    ;;
  fresh)
    echo "Wiping database and rebuilding from scratch..."
    docker compose down -v
    ;;
esac

echo "Building and starting containers..."
docker compose up --build -d

echo "Waiting for the API to be ready..."
for _ in $(seq 1 60); do
  if curl -fs http://localhost:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo ""
echo "Game Item Store is up:"
echo "  Frontend : http://localhost:4200"
echo "  API docs : http://localhost:8000/docs"
echo ""
echo "Logins:"
echo "  admin / Admin@12345   (admin)"
echo "  demo  / Demo@12345    (regular user)"
echo ""
echo "Stop with: ./run.sh stop     Reset data with: ./run.sh fresh"
