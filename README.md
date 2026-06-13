# ForgePulse

[![在线 Demo](https://img.shields.io/badge/在线%20Demo-GitHub%20Pages-2ea44f?logo=github)](https://baifanlili.github.io/ForgePulse/)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

ForgePulse 是一个面向半导体测试场景的工业设备数据平台。

项目聚焦设备遥测接入、实时状态监控、告警生命周期管理、良率分析、SPC 分析，以及 AI 辅助的工业知识检索。

## 在线 Demo

前端静态演示版使用内置模拟数据，不依赖后端 API 或数据库：

[打开 ForgePulse 在线 Demo](https://baifanlili.github.io/ForgePulse/)

完整本地闭环请使用 Docker Compose 启动。

## 定位

ForgePulse 的目标是成为可迁移的工业数据平台，而不是传统后台管理系统。

核心方向：

- 使用 C++ 边缘网关进行设备仿真与遥测发布
- 使用 Python 平台服务完成数据接入、处理、分析与 AI 能力
- 使用 React 仪表盘呈现工业监控与半导体分析
- 使用 MQTT 和 Kafka 承载设备数据流
- 使用 PostgreSQL、TimescaleDB、pgvector 和 Redis 进行存储

## 架构

```text
半导体设备模拟器
        |
        v
C++ 边缘网关
        |
        v
MQTT / Kafka
        |
        v
Python 平台 API + 流处理 Worker
        |
        v
PostgreSQL / TimescaleDB / pgvector / Redis
        |
        v
React 工业仪表盘
```

## 模块

```text
edge-gateway/     C++ 设备模拟器与边缘网关
platform-api/     FastAPI 平台 API
stream-worker/    Python 数据流处理器
web/              React 工业仪表盘
deploy/           Docker、Nginx、PostgreSQL、MQTT 配置
docs/             架构与项目文档
packages/         共享 schema 与契约
scripts/          开发与部署脚本
```

## 一键部署

复制环境变量：

```bash
cp .env.example .env
```

启动所有服务：

```bash
docker compose up -d --build
```

也可以使用 Make：

```bash
make up
```

`.env.example` 仅包含本地开发和演示用默认配置。公开部署时请复制为 `.env` 并替换数据库密码、API Key 等敏感配置，且不要提交 `.env`。

## MVP 范围

首个版本将聚焦一条完整的工业数据闭环：

- 创建和管理半导体设备
- 由 C++ 生成设备心跳、遥测、事件和测试数据
- 通过 MQTT 和 Kafka 接入数据
- 更新实时设备状态
- 根据规则生成告警
- 分析 Lot、Wafer、Yield、Bin 和 SPC 数据
- 使用 LangChain 与 pgvector 提供工业知识库问答
- 在 React 中展示仪表盘、设备状态、告警和良率分析

## 文档

- [架构](docs/architecture.md)
- [技术栈](docs/technology-stack.md)
- [MVP 范围](docs/mvp-scope.md)
- [部署](docs/deployment.md)
- [数据来源](docs/data-sources.md)
- [项目结构](docs/project-structure.md)
- [工程架构](docs/engineering-architecture.md)
- [开发进度](docs/progress.md)
- [GitHub 计划](docs/github-plan.md)

## 开源许可

本项目使用 [MIT License](LICENSE) 开源。
