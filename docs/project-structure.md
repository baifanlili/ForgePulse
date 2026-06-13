# Project Structure

```text
ForgePulse/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── deploy/
│   ├── mqtt/
│   │   └── mosquitto.conf
│   ├── nginx/
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── github-plan.md
│   ├── mvp-scope.md
│   ├── project-structure.md
│   └── technology-stack.md
├── edge-gateway/
│   ├── CMakeLists.txt
│   ├── Dockerfile
│   └── src/
│       └── main.cpp
├── packages/
│   └── schemas/
│       └── telemetry.schema.json
├── platform-api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       └── main.py
├── scripts/
│   └── publish-github.ps1
├── stream-worker/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── worker/
│       ├── __init__.py
│       └── main.py
└── web/
    ├── Dockerfile
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── styles.css
        └── vite-env.d.ts
```

## Design Principles

- Keep C++ edge code independent from platform services.
- Keep Python API and stream worker deployable as separate services.
- Keep message schemas in `packages/schemas` so producers and consumers share contracts.
- Keep documents in Markdown for GitHub readability and future project packaging.
- Keep Docker Compose as the default local deployment path.
