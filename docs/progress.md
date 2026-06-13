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
- 新增 stream worker 占位入口。
- 新增 React/Vite 工业仪表盘页面，展示设备状态、活动告警、良率趋势、Bin 分布、SPC 控制图和最新遥测。
- 新增 `web/package-lock.json`，用于锁定前端依赖版本。
- `edge-gateway` 已可生成多设备模拟遥测 JSON，并发布到 MQTT topic `forgepulse/telemetry`。
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

## 当前代码状态

### platform-api

- 入口文件：`platform-api/app/main.py`
- 当前使用 `psycopg` 直接连接 PostgreSQL，提供只读仪表盘和分析接口。
- 已启用本地前端访问所需 CORS。
- 已提供设备详情与设备级遥测时间序列查询，支持按指标、时间窗口、全历史模式和返回条数过滤。
- 后续可在业务模型稳定后再拆分路由、服务层和 SQLAlchemy 模型。

### stream-worker

- 入口文件：`stream-worker/worker/main.py`
- 当前使用 `paho-mqtt` 消费 `forgepulse/telemetry`。
- 每条消息会写入 `telemetry_points`，并更新对应设备状态与最近心跳。
- 当前包含简单阈值告警规则：
  - `temperature >= 76.0`
  - `pressure >= 2.85`

### edge-gateway

- 入口文件：`edge-gateway/src/main.cpp`
- 当前生成 `ETCH-01`、`CVD-02`、`PHOTO-03`、`TEST-04` 的模拟遥测。
- 运行容器中使用 `mosquitto_pub` 发布 MQTT 消息。
- MQTT 地址通过 `MQTT_HOST`、`MQTT_PORT`、`MQTT_TELEMETRY_TOPIC` 环境变量配置。

### web

- 入口文件：`web/src/main.tsx`
- 当前为工业仪表盘首页，使用 Ant Design 和 ECharts。
- 默认从 `http://localhost:8000` 读取 API，可通过 `VITE_API_BASE_URL` 覆盖。
- 每 10 秒自动刷新仪表盘、设备状态和 SPC 数据。

### 数据库

- 初始化脚本：`deploy/postgres/init.sql`
- 当前包含设备、遥测、告警、Lot、Wafer 良率、Bin 分布和 SPC 演示表。
- 演示数据为合成数据，不依赖外部数据集。
- 后续需要补充知识库、文档 chunk、embedding 等 AI 相关表。

## 下一步建议

下一阶段优先增强实时闭环的可用性：

1. 为 `web` 增加设备详情页，接入设备详情接口和时间序列查询接口。
2. 为 `web` 增加告警详情页和手动刷新按钮。
3. 增加心跳超时规则，把长时间未上报的设备自动置为 `offline`。
4. 将 worker 中的阈值规则抽成配置或独立规则类。
5. 补充测试脚本，验证 API 查询、MQTT 消费和数据库写入。

## 数据来源约定

- 可以使用公开数据或开源样例数据辅助构造演示数据，但必须记录来源和用途。
- 对半导体制造数据，优先使用合成数据或公开可用数据集，避免引入来源不清的数据。
- 如使用外部数据，应在相关文档中注明链接、许可证或使用条件。
- 原始大文件不提交到 Git，优先通过导入脚本从本地文件或官方下载源导入。

## 当前关键决策

- 默认文档语言：简体中文。
- 默认 commit message：简体中文。
- 本地部署优先使用 Docker Compose。
- MVP 先追求端到端可运行，再逐步增强真实流处理、分析和 AI 知识库能力。
- 第一版演示数据使用合成数据，不引入外部开源数据集。
- 实时遥测 topic 默认使用 `forgepulse/telemetry`。

## 待确认

- 是否引入 TimescaleDB 和 pgvector 镜像，还是先用普通 PostgreSQL 表完成 MVP。
- 外部开源数据集的首个接入对象：AI4I 2020、SECOM 或 WM-811K 抽样数据。
- 前端是否需要按页面拆分路由，还是短期继续保持单页仪表盘。
- C++ edge 是否后续引入正式 MQTT C/C++ SDK，替换当前 `mosquitto_pub` 轻量发布方案。
