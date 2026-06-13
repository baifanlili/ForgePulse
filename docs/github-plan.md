# GitHub 计划

## 仓库

推荐仓库名：

```text
ForgePulse
```

草稿阶段推荐可见性：

```text
Private
```

当 MVP 可以端到端运行后，可以将仓库设为公开。

## 初始提交

建议提交信息：

```text
Initialize ForgePulse project structure
```

## 建议仓库描述

```text
Industrial equipment telemetry and AI-assisted semiconductor yield analytics platform.
```

## 建议 Topics

```text
industrial-iot
semiconductor
telemetry
mqtt
kafka
fastapi
cpp
react
langchain
pgvector
timescaledb
spc
yield-analysis
```

## 发布命令

安装并登录 Git 和 GitHub CLI 后：

```bash
cd /d D:\ForgePulse
git init
git add .
git commit -m "Initialize ForgePulse project structure"
gh repo create ForgePulse --private --source=. --remote=origin --push
```

或者运行：

```powershell
.\scripts\publish-github.ps1
```

如果仓库已经存在：

```bash
cd /d D:\ForgePulse
git init
git remote add origin https://github.com/<your-user>/ForgePulse.git
git add .
git commit -m "Initialize ForgePulse project structure"
git branch -M main
git push -u origin main
```
