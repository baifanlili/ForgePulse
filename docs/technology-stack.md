# 技术栈

## 边缘网关

- C++20
- CMake
- paho-mqtt-cpp
- Boost.Asio
- nlohmann/json
- spdlog
- yaml-cpp
- GoogleTest

职责：

- 设备仿真
- 心跳与遥测生成
- 半导体测试数据生成
- MQTT 发布
- 本地校验
- 重连与重试逻辑

## 平台 API

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Redis client
- OpenAPI

职责：

- 设备管理
- 告警中心
- 半导体业务 API
- 仪表盘 API
- 知识库 API

## 流处理 Worker

- Python 3.11+
- paho-mqtt
- aiokafka 或 confluent-kafka
- pandas
- numpy
- scipy

职责：

- MQTT 消费
- Kafka 发布与消费
- 遥测处理
- 状态聚合
- 告警规则评估
- Yield、Bin 和 SPC 计算

## AI 知识层

- LangChain
- pgvector
- OpenAI 兼容模型 API
- 文档加载器
- RAG 链

职责：

- 工业知识库索引
- 知识问答
- 告警解释
- 良率异常解释

## 前端

- React
- TypeScript
- Vite
- Ant Design
- TanStack Query
- Zustand
- ECharts
- React Router

职责：

- 工业仪表盘
- 设备状态监控
- 告警中心
- 半导体分析页面
- 知识助手界面

## 基础设施

- Docker Compose
- PostgreSQL
- TimescaleDB
- pgvector
- Redis
- Mosquitto MQTT
- Kafka KRaft mode
- Nginx
