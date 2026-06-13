# Technology Stack

## Edge Gateway

- C++20
- CMake
- paho-mqtt-cpp
- Boost.Asio
- nlohmann/json
- spdlog
- yaml-cpp
- GoogleTest

Responsibilities:

- Device simulation
- Heartbeat and telemetry generation
- Semiconductor test data generation
- MQTT publishing
- Local validation
- Reconnect and retry logic

## Platform API

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Redis client
- OpenAPI

Responsibilities:

- Device management
- Alarm center
- Semiconductor business APIs
- Dashboard APIs
- Knowledge base APIs

## Stream Worker

- Python 3.11+
- paho-mqtt
- aiokafka or confluent-kafka
- pandas
- numpy
- scipy

Responsibilities:

- MQTT consumption
- Kafka publishing and consumption
- Telemetry processing
- Status aggregation
- Alarm rule evaluation
- Yield, Bin, and SPC calculations

## AI Knowledge Layer

- LangChain
- pgvector
- OpenAI-compatible model API
- Document loaders
- RAG chains

Responsibilities:

- Industrial knowledge base indexing
- Knowledge Q&A
- Alarm explanation
- Yield anomaly explanation

## Frontend

- React
- TypeScript
- Vite
- Ant Design
- TanStack Query
- Zustand
- ECharts
- React Router

Responsibilities:

- Industrial dashboard
- Device status monitoring
- Alarm center
- Semiconductor analytics pages
- Knowledge assistant UI

## Infrastructure

- Docker Compose
- PostgreSQL
- TimescaleDB
- pgvector
- Redis
- Mosquitto MQTT
- Kafka KRaft mode
- Nginx
