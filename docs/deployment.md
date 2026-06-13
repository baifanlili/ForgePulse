# Deployment

ForgePulse is designed for local one-command deployment with Docker Compose.

## Prerequisites

- Docker Desktop
- Docker Compose
- Optional: Git and GitHub CLI for publishing

## Start

```bash
cp .env.example .env
docker compose up -d --build
```

## Stop

```bash
docker compose down
```

## Reset Data

```bash
docker compose down -v
docker compose up -d --build
```

## Service Ports

| Service | Port |
| --- | --- |
| Web | 3000 |
| API | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| MQTT | 1883 |
| Kafka | 9092 |

## Deployment Notes

The initial deployment uses Docker Compose because it is easier to run and demo.

The service boundaries are compatible with a later Kubernetes migration:

- `edge-gateway` can become a device-side or edge-node workload
- `platform-api` can scale horizontally
- `stream-worker` can scale by Kafka consumer group
- `web` can be served by Nginx or object storage CDN
- PostgreSQL, Redis, Kafka, and MQTT can be replaced by managed services
