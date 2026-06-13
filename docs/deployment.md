# 部署

ForgePulse 设计为基于 Docker Compose 的本地一键部署项目。

## 前置条件

- Docker Desktop
- Docker Compose
- 可选：用于发布的 Git 和 GitHub CLI

## 启动

```bash
cp .env.example .env
docker compose up -d --build
```

默认本地技术栈会启动轻量级 MVP 服务：

- Web
- Platform API
- Stream worker
- Edge gateway
- PostgreSQL
- pgAdmin
- Redis
- MQTT

Kafka 暂时放在 `streaming` profile 下，供后续数据流工作使用：

```bash
docker compose --profile streaming up -d --build
```

首个可运行版本使用 `postgres:16-alpine`，以保证本地启动更稳定。TimescaleDB 和 pgvector 仍作为分析与 AI 知识库阶段的计划存储扩展。

## 停止

```bash
docker compose down
```

## 重置数据

```bash
docker compose down -v
docker compose up -d --build
```

## 服务端口

| 服务 | 端口 |
| --- | --- |
| Web | 3000 |
| API | 8000 |
| PostgreSQL | 5432 |
| pgAdmin | 5050 |
| Redis | 6379 |
| MQTT | 1883 |
| Kafka | 9092，启用 `streaming` profile 时可用 |

## 数据库访问

PostgreSQL 在 Docker 中运行，并暴露到本机：

```text
Host: localhost
Port: 5432
Database: forgepulse
User: forgepulse
Password: forgepulse
```

pgAdmin 可通过以下地址访问：

```text
http://localhost:5050
```

默认 pgAdmin 登录信息：

```text
Email: admin@forgepulse.dev
Password: forgepulse
```

在 pgAdmin 内注册数据库服务器时，使用 Docker 服务名作为主机：

```text
Host: postgres
Port: 5432
Database: forgepulse
User: forgepulse
Password: forgepulse
```

## 部署说明

初始部署使用 Docker Compose，因为它更容易运行和演示。

服务边界兼容后续迁移到 Kubernetes：

- `edge-gateway` 可以变成设备侧或边缘节点工作负载
- `platform-api` 可以水平扩展
- `stream-worker` 可以通过 Kafka consumer group 扩展
- `web` 可以由 Nginx 或对象存储 CDN 提供服务
- PostgreSQL、Redis、Kafka 和 MQTT 可以替换为托管服务
