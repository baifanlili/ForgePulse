# MVP Scope

The MVP should prove a complete industrial data loop while keeping implementation controlled.

## In Scope

### Edge Gateway

- Generate semiconductor equipment heartbeat
- Generate telemetry values such as temperature, voltage, pressure, and run state
- Generate Lot, Wafer, Die, Bin, and Pass/Fail test data
- Publish data to MQTT topics

### Data Platform

- Device list and device detail APIs
- Telemetry ingestion pipeline
- Event records
- Alarm rule evaluation
- Latest device status cache
- Historical telemetry storage

### Semiconductor Analytics

- Lot list and detail
- Wafer list and detail
- Yield summary
- Yield trend
- Bin distribution
- Basic SPC control chart
- Abnormal Lot identification

### AI Knowledge

- Upload or seed industrial knowledge documents
- Chunk and embed documents
- Store embeddings in pgvector
- Knowledge Q&A
- Alarm explanation
- Yield anomaly summary

### Frontend

- Dashboard overview
- Device list and detail
- Alarm list and detail
- Yield analysis page
- Bin distribution page
- SPC page
- Knowledge assistant page

## Out of Scope for MVP

- Real OPC UA or Modbus device integration
- Complex permission system
- Multi-tenant architecture
- Kubernetes deployment
- Full agent workflow automation
- Robotics module
- Production-grade high availability

## Success Criteria

- The project starts with one command
- The C++ gateway publishes simulated device data
- The platform consumes and stores telemetry
- The dashboard shows live status and alarms
- Semiconductor analytics pages show meaningful data
- AI knowledge Q&A returns source-grounded answers
