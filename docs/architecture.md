# Architecture

ForgePulse uses a layered industrial data platform architecture.

## Layers

```text
Device Layer
  Semiconductor equipment simulator

Edge Layer
  C++ Edge Gateway
  Protocol adapters
  MQTT publisher
  Local validation and buffering

Data Flow Layer
  MQTT for device telemetry ingress
  Kafka for internal streaming and decoupling

Platform Layer
  FastAPI platform API
  Stream worker
  Alarm rule engine
  Semiconductor analytics engine

Storage Layer
  PostgreSQL for business data
  TimescaleDB for telemetry time series
  pgvector for knowledge embeddings
  Redis for latest device status and cache

Application Layer
  React industrial dashboard
  Device monitoring
  Alarm center
  Yield and SPC analysis
  Knowledge assistant
```

## Data Flow

```text
C++ simulator
  -> MQTT topics
  -> stream-worker
  -> Kafka topics
  -> processors
  -> PostgreSQL / TimescaleDB / Redis
  -> FastAPI
  -> React dashboard
```

## Extension Points

### Device Protocols

The edge gateway should expose a protocol adapter interface.

Initial adapters:

- MQTT simulator adapter

Future adapters:

- OPC UA adapter
- Modbus adapter
- TCP socket adapter
- SECS/GEM-inspired adapter

### Industry Plugins

The platform keeps semiconductor analysis as the first domain plugin.

Future plugins may include:

- Robotics fleet monitoring
- Battery manufacturing
- Photovoltaic manufacturing
- General production line monitoring

### Rule Engine

Alarm and analytics rules should be registered as independent rule classes.

Initial rules:

- Heartbeat timeout
- Threshold alarm
- Yield drop
- Bin distribution anomaly
- SPC violation

### AI Chains

AI capabilities are auxiliary and should not be coupled with core telemetry processing.

Initial chains:

- Industrial knowledge Q&A
- Alarm analysis
- Yield anomaly explanation
