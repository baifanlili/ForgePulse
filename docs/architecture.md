# 架构

ForgePulse 使用分层的工业数据平台架构。

## 分层

```text
设备层
  半导体设备模拟器

边缘层
  C++ 边缘网关
  协议适配器
  MQTT 发布器
  本地校验与缓冲

数据流层
  MQTT 用于设备遥测接入
  Kafka 用于内部流式处理与解耦

平台层
  FastAPI 平台 API
  流处理 Worker
  告警规则引擎
  半导体分析引擎

存储层
  PostgreSQL 用于业务数据
  TimescaleDB 用于遥测时间序列
  pgvector 用于知识 embedding
  Redis 用于最新设备状态和缓存

应用层
  React 工业仪表盘
  设备监控
  告警中心
  良率与 SPC 分析
  知识助手
```

## 数据流

```text
C++ 模拟器
  -> MQTT topics
  -> stream-worker
  -> Kafka topics
  -> processors
  -> PostgreSQL / TimescaleDB / Redis
  -> FastAPI
  -> React 仪表盘
```

## 扩展点

### 设备协议

边缘网关应暴露协议适配器接口。

初始适配器：

- MQTT 模拟器适配器

未来适配器：

- OPC UA 适配器
- Modbus 适配器
- TCP socket 适配器
- 受 SECS/GEM 启发的适配器

### 行业插件

平台将半导体分析作为第一个领域插件。

未来插件可以包括：

- 机器人车队监控
- 电池制造
- 光伏制造
- 通用产线监控

### 规则引擎

告警和分析规则应注册为独立的规则类。

初始规则：

- 心跳超时
- 阈值告警
- 良率下降
- Bin 分布异常
- SPC 违规

### AI 链

AI 能力是辅助能力，不应与核心遥测处理强耦合。

初始链：

- 工业知识问答
- 告警分析
- 良率异常解释
