# 开发进度

本文档用于记录 ForgePulse 当前开发状态。后续协作时，优先阅读本文件，再按需打开具体模块代码或专题文档。

## 当前状态

- 项目已完成基础目录结构。
- Docker Compose 已包含 PostgreSQL、pgAdmin、Redis、MQTT、Kafka、platform-api、stream-worker、edge-gateway 和 web 服务。
- Kafka 目前放在 `streaming` profile 下，默认启动轻量级 MVP 服务。
- Markdown 文档已中文化。
- 已新增 `AGENTS.md`，约定文档和 commit message 默认使用简体中文。
- 已完成第一版“数据库演示数据 -> Platform API -> React 仪表盘”的可视化闭环。
- 已完成第一版“C++ edge-gateway -> MQTT -> stream-worker -> PostgreSQL”的实时遥测闭环。
- 已开始按企业级真实项目结构拆分前后端模块，新增 `docs/engineering-architecture.md`。
- 已新增系统运营总览，开始覆盖服务健康、数据摄取延迟和核心表数据量。
- 已开始整理 C++ 边缘网关工程结构，将配置、遥测生成和 MQTT 发布从 `main.cpp` 拆出。
- C++ 边缘网关已补充消息序列号、网关/产线标识、采样周期、质量标记、发布重试和失败落盘缓存。
- 已新增边缘网关交互闭环：前端 `/edge` 页面可通过 API 下发 MQTT command，C++ 网关可响应暂停、恢复、改采样周期和注入故障。
- stream-worker 已支持设备心跳超时自动离线检测和告警阈值规则配置化。
- stream-worker 已新增 Worker 健康上报（`worker_heartbeats` 表），每 10 秒写入处理统计，系统运营页可查看真实 Worker 运行状态。
- 已补齐 Worker 心跳表的旧库兜底创建、心跳超时 SQL 参数写法和设备恢复后的心跳告警自动关闭逻辑。

## 已完成

- 初始化项目结构。
- 补充中文 README 和 docs 文档。
- 补充本地 Docker Compose 部署说明。
- 新增 PostgreSQL 初始化表和演示数据：
  - `devices`
  - `telemetry_points`
  - `alarms`
  - `lots`
  - `wafer_yields`
  - `bin_counts`
  - `spc_points`
- 新增 FastAPI 接口：
  - `GET /health`
  - `GET /api/dashboard`
  - `GET /api/devices`
  - `GET /api/alarms`
  - `GET /api/analytics/yield`
  - `GET /api/analytics/spc`
  - `GET /api/devices/{device_code}`
  - `GET /api/devices/{device_code}/telemetry`
  - `GET /api/system/overview`
  - `GET /api/edge/gateways`
  - `GET /api/edge/gateways/{gateway_id}/commands`
  - `POST /api/edge/gateways/{gateway_id}/commands`
- 新增 stream worker 占位入口。
- 新增 React/Vite 工业仪表盘页面，展示设备状态、活动告警、良率趋势、Bin 分布、SPC 控制图和最新遥测。
- 新增 `web/package-lock.json`，用于锁定前端依赖版本。
- `edge-gateway` 已可生成多设备模拟遥测 JSON，并发布到 MQTT topic `forgepulse/telemetry`。
- `edge-gateway` 已拆分为配置、遥测模型和 MQTT 发布器模块，保留轻量 `mosquitto_pub` 发布方案。
- `edge-gateway` 发布的 `payload` 已包含 `schema_version`、`gateway_id`、`line_id`、`sequence`、`quality`、`status_reason` 和 `sample_period_ms`，便于后续做数据质量、补发和边缘审计。
- `edge-gateway` 已监听 `forgepulse/commands/{gateway_id}` 命令 topic，可响应平台下发的运行控制命令。
- `stream-worker` 已可订阅 MQTT、写入 `telemetry_points`、更新 `devices.last_heartbeat_at`，并根据温度/压力阈值维护实时告警。
- 前端仪表盘已增加 10 秒自动刷新。
- 为 `web`、`edge-gateway`、`stream-worker` 补充 `.dockerignore`，减少 Docker 构建上下文。
- 前端已支持 `VITE_DEMO_MODE=true` 静态演示模式，并新增 GitHub Pages 自动部署 workflow。
- 项目准备改为公开开源仓库，已补充 MIT License、README 在线 Demo 入口和敏感配置提示。
- 已为 `main` 分支准备保护规则：PR 至少 1 个批准、`build` 检查通过、禁止强推和删除。
- `platform-api` 已增加设备详情接口和设备遥测时间序列查询接口，为前端设备详情页做准备。
- 已新增 `docs/data-sources.md`，记录 SECOM、AI4I 2020、WM-811K 等候选公开数据集及许可证注意事项。
- 已新增 `scripts/import-secom-demo.py`，可下载 UCI SECOM 真实半导体制造数据并导入 PostgreSQL。
- 设备遥测接口已支持 `all_history=true`，便于查询 SECOM 等历史公开数据集。
- `platform-api` 已拆分为 `core`、`api/router.py` 和多个 `api/routers/*` 模块，`main.py` 只保留应用工厂与路由挂载。
- `web` 已拆分为 `app`、`features`、`shared` 三层，并接入页面路由。
- 前端已新增设备详情页，可从仪表盘点击设备进入详情，查看设备画像、遥测趋势和设备告警。
- 已新增根目录 `DESIGN.md`，约定 ForgePulse 的工业数据平台视觉语言、布局模式、组件规范和 AI 协作提示。
- 已新增企业级告警中心：支持告警列表过滤、详情抽屉、确认、关闭和处理轨迹。
- 已新增系统运营总览页面：展示 API、PostgreSQL、stream-worker、edge-gateway 的运行推断状态，以及遥测摄取、指标分布和核心表数据量。
- 已新增心跳超时规则：stream-worker 每 30 秒检查设备心跳，超过 120 秒未上报自动置为 `offline` 并生成告警。
- 已将 stream-worker 阈值规则抽成 `worker/rules.py` 模块，支持通过 `ALARM_RULES_JSON` 环境变量覆盖默认规则。
- 已新增完整 Pydantic schema 层（`app/schemas/`），覆盖 health/device/alarm/analytics/dashboard/system/edge 全部 API 响应类型，所有路由已使用 `response_model`。
- 前端 TypeScript 类型已与后端 Pydantic schema 对齐，消除隐式 `Record<string, unknown>` 结构。
- 已新增 `worker_heartbeats` 表和 Worker 健康上报机制：stream-worker 每 10 秒写入心跳和处理统计，系统运营页改用真实探针判断 Worker 状态。
- 已修复 Worker 心跳相关运行时风险：`worker_heartbeats` 在旧数据库卷中可自动创建，心跳超时查询使用安全参数绑定，设备恢复遥测后会自动关闭对应 `HB-*-TIMEOUT` 告警。

## 当前代码状态

### platform-api

- 入口文件：`platform-api/app/main.py`
- 当前使用 `psycopg` 直接连接 PostgreSQL，提供只读仪表盘和分析接口。
- 已启用本地前端访问所需 CORS。
- 已提供设备详情与设备级遥测时间序列查询，支持按指标、时间窗口、全历史模式和返回条数过滤。
- 当前已完成 router 级拆分；已新增 `app/schemas/` Pydantic schema 层，所有路由已挂载 `response_model`，确保 API 响应类型严格约束。
- 后续可在业务模型稳定后继续增加 repository、service 和测试层。
- 告警 API 已支持列表过滤、详情查询、确认和关闭动作，并记录 `alarm_events` 审计轨迹。
- 系统运营 API 已提供 `/api/system/overview`，用于汇总服务状态、设备/告警统计、最新遥测延迟、近 15 分钟摄取分布和核心表数据量。
- 边缘网关 API 已提供 `/api/edge/gateways` 和命令下发接口，命令会发布到 MQTT command topic 并记录到 `edge_commands`。

### stream-worker

- 入口文件：`stream-worker/worker/main.py`
- 当前使用 `paho-mqtt` 消费 `forgepulse/telemetry`。
- 每条消息会写入 `telemetry_points`，并更新对应设备状态与最近心跳。
- 告警阈值规则已抽成 `worker/rules.py` 模块，支持 `AlarmRule` 数据类，默认规则覆盖 temperature/pressure，可通过 `ALARM_RULES_JSON` 环境变量扩展。
- 心跳监控线程独立运行（默认每 30 秒检查），超时阈值通过 `HEARTBEAT_TIMEOUT_SECONDS` 配置（默认 120 秒），超时设备自动置为 `offline` 并生成心跳超时告警。
- 健康上报线程独立运行（默认每 10 秒），向 `worker_heartbeats` 写入 worker_id、已处理遥测数、已触发告警数和心跳时间。
- 当前包含简单阈值告警规则：
  - `temperature >= 76.0`
  - `pressure >= 2.85`

### edge-gateway

- 入口文件：`edge-gateway/src/main.cpp`
- 配置模块：`edge-gateway/src/config.cpp`
- 遥测模块：`edge-gateway/src/telemetry.cpp`
- MQTT 发布模块：`edge-gateway/src/mqtt_publisher.cpp`
- 命令监听模块：`edge-gateway/src/command_listener.cpp`
- 当前生成 `ETCH-01`、`CVD-02`、`PHOTO-03`、`TEST-04` 的模拟遥测。
- 运行容器中使用 `mosquitto_pub` 发布 MQTT 消息。
- MQTT 地址通过 `MQTT_HOST`、`MQTT_PORT`、`MQTT_TELEMETRY_TOPIC` 环境变量配置。
- 发布间隔可通过 `EDGE_PUBLISH_INTERVAL_SECONDS` 配置，默认 5 秒。
- 网关标识通过 `EDGE_GATEWAY_ID`、`EDGE_LINE_ID` 配置。
- 发布失败会按 `EDGE_PUBLISH_RETRY_COUNT` 重试；仍失败时写入 `EDGE_SPOOL_DIR`，后续循环按 `EDGE_SPOOL_FLUSH_LIMIT` 补发。
- 命令 topic 通过 `MQTT_COMMAND_TOPIC` 配置，默认 `forgepulse/commands/EDGE-GW-01`。
- 当前支持命令：`pause`、`resume`、`set_interval`、`inject_fault`。

### web

- 入口文件：`web/src/main.tsx`
- 当前使用 `HashRouter`，包含运行总览、设备详情、告警中心、边缘网关和系统运营页面。
- 已新增告警中心页面，侧边栏可进入 `/alarms`。
- 已新增系统运营页面，侧边栏可进入 `/system`。
- 已新增边缘网关页面，侧边栏可进入 `/edge`。
- 工程结构已拆分为：
  - `app/`：应用壳与路由
  - `features/`：业务页面
  - `shared/`：API 客户端、共享类型（已与后端 Pydantic schema 对齐）、图表、状态标签和格式化工具
- 默认从 `http://localhost:8000` 读取 API，可通过 `VITE_API_BASE_URL` 覆盖。
- 每 10 秒自动刷新仪表盘、设备状态和 SPC 数据。
- 系统运营页面每 15 秒自动刷新服务状态和摄取概览。

### 数据库

- 初始化脚本：`deploy/postgres/init.sql`
- 当前包含设备、遥测、告警、Lot、Wafer 良率、Bin 分布、SPC 演示、边缘命令和 Worker 心跳表。
- 告警表已扩展确认人与关闭人字段，并新增 `alarm_events` 记录处理轨迹。
- 演示数据为合成数据，不依赖外部数据集。
- 后续需要补充知识库、文档 chunk、embedding 等 AI 相关表。

## 下一步建议

下一阶段优先增强实时闭环的可用性：

1. ~~为前后端补充 Pydantic/TypeScript API schema 约束，减少隐式结构。~~ ✅
2. 增加用户、角色、权限和操作审计，为告警动作接入真实身份。
3. ~~增加心跳超时规则，把长时间未上报的设备自动置为 `offline`。~~ ✅
4. ~~将 worker 中的阈值规则抽成配置或独立规则类。~~ ✅
5. ~~将系统运营页的服务状态从"数据推断"升级为真实健康探针和 worker 心跳表。~~ ✅
6. 将边缘命令从"已发布"升级为 C++ ack 回执闭环，并在平台侧记录 executed/failed 状态。
7. 为 C++ 网关补充单元测试，覆盖遥测生成、质量标记、命令解析、重试和 spool 补发逻辑。
8. 补充测试脚本，验证 API 查询、MQTT 消费和数据库写入。

## 数据来源约定

- 可以使用公开数据或开源样例数据辅助构造演示数据，但必须记录来源和用途。
- 对半导体制造数据，优先使用合成数据或公开可用数据集，避免引入来源不清的数据。
- 如使用外部数据，应在相关文档中注明链接、许可证或使用条件。
- 原始大文件不提交到 Git，优先通过导入脚本从本地文件或官方下载源导入。

## 当前关键决策

- 默认文档语言：简体中文。
- 默认 commit message：简体中文。
- 默认界面设计规范：遵循根目录 `DESIGN.md`，保持工业监控、数据密集、克制专业的产品气质。
- 本地部署优先使用 Docker Compose。
- MVP 先追求端到端可运行，再逐步增强真实流处理、分析和 AI 知识库能力。
- 第一版演示数据使用合成数据，不引入外部开源数据集。
- 实时遥测 topic 默认使用 `forgepulse/telemetry`。
- 前端使用 `HashRouter`，优先兼容 GitHub Pages 和普通静态托管。

## 待确认

- 是否引入 TimescaleDB 和 pgvector 镜像，还是先用普通 PostgreSQL 表完成 MVP。
- 外部开源数据集的首个接入对象：AI4I 2020、SECOM 或 WM-811K 抽样数据。
- C++ edge 是否后续引入正式 MQTT C/C++ SDK，替换当前 `mosquitto_pub` 轻量发布方案。
- 后端何时引入正式迁移体系 Alembic，以及是否把 `init.sql` 仅保留为本地 demo seed。
