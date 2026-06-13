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

The default local stack starts the lightweight MVP services:

- Web
- Platform API
- Stream worker
- Edge gateway
- PostgreSQL
- Redis
- MQTT

Kafka is kept behind the `streaming` profile for later data-streaming work:

```bash
docker compose --profile streaming up -d --build
```

The first runnable version uses `postgres:16-alpine` to keep local startup reliable. TimescaleDB and pgvector remain planned storage extensions for the analytics and AI knowledge-base phases.

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
| Kafka | 9092, when `streaming` profile is enabled |

## Deployment Notes

The initial deployment uses Docker Compose because it is easier to run and demo.

The service boundaries are compatible with a later Kubernetes migration:

- `edge-gateway` can become a device-side or edge-node workload
- `platform-api` can scale horizontally
- `stream-worker` can scale by Kafka consumer group
- `web` can be served by Nginx or object storage CDN
- PostgreSQL, Redis, Kafka, and MQTT can be replaced by managed services
