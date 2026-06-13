# 项目协作规范

## 文档语言

- 本项目所有 Markdown 文档默认使用简体中文编写。
- README、`docs/` 目录、部署说明、设计文档、开发说明等 `.md` 文件都应优先使用中文。
- 命令、代码、配置项、路径、API 名称、库名、协议名和必要的技术术语可以保留英文。
- 如需英文文档，应显式创建独立英文版本，例如 `README.en.md`，不要把中英文说明混写在同一个主文档中。

## Commit 信息

- 本项目的 commit message 默认使用简体中文。
- commit 标题应简短明确，优先说明本次变更做了什么。
- 可以保留必要的英文技术名词、模块名、文件名、命令和 issue/PR 编号。
- 推荐格式：

```text
初始化项目结构
补充 Docker Compose 部署说明
修复 API 健康检查路径
更新 README 和架构文档
```

- 如需使用 Conventional Commits，也使用中文描述：

```text
feat: 添加设备列表接口
fix: 修复 MQTT 重连逻辑
docs: 更新部署文档
chore: 调整 Docker 配置
```
