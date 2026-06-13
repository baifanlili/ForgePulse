# 工程架构

本文档记录 ForgePulse 面向真实项目演进的代码组织方式。目标是让功能增长时仍然保持边界清晰、可测试、可部署。

## 后端分层

`platform-api` 采用 FastAPI 模块化结构：

```text
platform-api/app/
|-- main.py                 应用工厂与中间件挂载
|-- core/
|   |-- config.py           环境配置与 Settings
|   `-- db.py               数据库连接基础设施
`-- api/
    |-- router.py           聚合所有 API router
    `-- routers/
        |-- health.py       健康检查
        |-- dashboard.py    运行总览
        |-- devices.py      设备与遥测查询
        |-- alarms.py       告警查询
        `-- analytics.py    良率与 SPC 分析
```

当前阶段仍使用 `psycopg` 直接查询，原因是表结构和业务边界还在快速迭代。后续当模型稳定后，可以增加：

- `schemas/`：Pydantic 请求与响应模型
- `repositories/`：数据库访问封装
- `services/`：业务用例与规则编排
- `dependencies.py`：认证、租户、审计等请求依赖
- `tests/`：接口测试和服务层测试

## 前端分层

`web` 采用应用层、特性层、共享层分离：

```text
web/src/
|-- main.tsx                React 挂载入口
|-- app/
|   |-- App.tsx             路由定义
|   `-- AppShell.tsx        应用布局与导航
|-- features/
|   |-- dashboard/          运行总览页面
|   `-- devices/            设备详情页面
|-- shared/
|   |-- api/                API 客户端
|   |-- charts/             通用图表组件
|   |-- format.ts           格式化工具
|   |-- status.tsx          状态标签与颜色
|   `-- types.ts            前端共享类型
|-- demoData.ts             GitHub Pages 静态 Demo 数据
`-- styles.css              全局样式
```

前端路由使用 `HashRouter`，优先保证 GitHub Pages 和普通静态托管环境可直接访问。企业内网部署到 Nginx 时，如果配置了 `try_files` fallback，可以切换为 `BrowserRouter`。

## 数据流

当前实时链路：

```text
edge-gateway
  -> MQTT topic: forgepulse/telemetry
  -> stream-worker
  -> PostgreSQL
  -> platform-api
  -> web
```

当前分析链路：

```text
PostgreSQL seed / import scripts
  -> platform-api analytics endpoints
  -> ECharts dashboard
```

## 近期演进原则

- API 路径保持稳定，内部模块可以继续拆分。
- 前端页面只组合数据和交互，通用图表、状态、格式化放入 `shared/`。
- 新增领域功能优先放入独立 `features/` 子目录。
- 外部数据集通过脚本导入，不提交原始大文件。
- 每次完成较大功能后更新 `docs/progress.md`。
