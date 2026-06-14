# 项目结构

```text
ForgePulse/
|-- README.md
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- Makefile
|-- deploy/
|   |-- mqtt/
|   |   `-- mosquitto.conf
|   |-- nginx/
|   |   `-- nginx.conf
|   `-- postgres/
|       `-- init.sql
|-- docs/
|   |-- architecture.md
|   |-- data-sources.md
|   |-- deployment.md
|   |-- engineering-architecture.md
|   |-- enterprise-roadmap.md
|   |-- github-plan.md
|   |-- mvp-scope.md
|   |-- progress.md
|   |-- project-structure.md
|   `-- technology-stack.md
|-- edge-gateway/
|   |-- CMakeLists.txt
|   |-- Dockerfile
|   `-- src/
|       `-- main.cpp
|-- packages/
|   `-- schemas/
|       `-- telemetry.schema.json
|-- platform-api/
|   |-- Dockerfile
|   |-- pyproject.toml
|   |-- requirements.txt
|   `-- app/
|       |-- api/
|       |-- core/
|       |-- __init__.py
|       `-- main.py
|-- scripts/
|   |-- import-secom-demo.py
|   `-- publish-github.ps1
|-- stream-worker/
|   |-- Dockerfile
|   |-- pyproject.toml
|   |-- requirements.txt
|   `-- worker/
|       |-- __init__.py
|       `-- main.py
`-- web/
    |-- Dockerfile
    |-- index.html
    |-- package.json
    |-- tsconfig.json
    |-- vite.config.ts
    `-- src/
        |-- app/
        |-- features/
        |-- shared/
        |-- demoData.ts
        |-- main.tsx
        |-- styles.css
        `-- vite-env.d.ts
```

## 设计原则

- 保持 C++ 边缘代码独立于平台服务。
- 保持 Python API 和流处理 Worker 可作为独立服务部署。
- 将消息 schema 放在 `packages/schemas` 中，让生产者和消费者共享契约。
- 使用 Markdown 保存文档，便于 GitHub 阅读和后续项目打包。
- 将 Docker Compose 作为默认的本地部署路径。
