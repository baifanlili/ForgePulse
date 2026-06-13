# ForgePulse

ForgePulse is an industrial equipment data platform for semiconductor test scenarios.

The project focuses on equipment telemetry ingestion, real-time status monitoring, alarm lifecycle management, yield analysis, SPC analysis, and AI-assisted industrial knowledge retrieval.

## Positioning

ForgePulse is designed as a transferable industrial data platform rather than a traditional admin system.

Core direction:

- C++ edge gateway for device simulation and telemetry publishing
- Python platform services for data ingestion, processing, analytics, and AI
- React dashboard for industrial monitoring and semiconductor analysis
- MQTT and Kafka for equipment data flow
- PostgreSQL, TimescaleDB, pgvector, and Redis for storage

## Architecture

```text
Semiconductor equipment simulator
        |
        v
C++ Edge Gateway
        |
        v
MQTT / Kafka
        |
        v
Python Platform API + Stream Worker
        |
        v
PostgreSQL / TimescaleDB / pgvector / Redis
        |
        v
React Industrial Dashboard
```

## Modules

```text
edge-gateway/     C++ device simulator and edge gateway
platform-api/     FastAPI platform API
stream-worker/    Python data stream processor
web/              React industrial dashboard
deploy/           Docker, Nginx, PostgreSQL, MQTT configs
docs/             Architecture and project documents
packages/         Shared schemas and contracts
scripts/          Development and deployment scripts
```

## One-Command Deployment

Copy environment variables:

```bash
cp .env.example .env
```

Start all services:

```bash
docker compose up -d --build
```

Or use Make:

```bash
make up
```

## MVP Scope

The first version will focus on a complete industrial data loop:

- Create and manage semiconductor equipment
- Generate equipment heartbeat, telemetry, events, and test data from C++
- Ingest data through MQTT and Kafka
- Update real-time device status
- Generate alarms from rules
- Analyze Lot, Wafer, Yield, Bin, and SPC data
- Provide industrial knowledge base Q&A with LangChain and pgvector
- Show dashboard, device status, alarms, and yield analysis in React

## Documentation

- [Architecture](docs/architecture.md)
- [Technology Stack](docs/technology-stack.md)
- [MVP Scope](docs/mvp-scope.md)
- [Deployment](docs/deployment.md)
- [Project Structure](docs/project-structure.md)
- [GitHub Plan](docs/github-plan.md)
