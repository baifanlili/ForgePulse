# GitHub Plan

## Repository

Recommended repository name:

```text
ForgePulse
```

Recommended visibility while drafting:

```text
Private
```

After the MVP can run end to end, the repository can be made public.

## Initial Commit

Suggested commit message:

```text
Initialize ForgePulse project structure
```

## Suggested Repository Description

```text
Industrial equipment telemetry and AI-assisted semiconductor yield analytics platform.
```

## Suggested Topics

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

## Publish Commands

After Git and GitHub CLI are installed and authenticated:

```bash
cd /d D:\ForgePulse
git init
git add .
git commit -m "Initialize ForgePulse project structure"
gh repo create ForgePulse --private --source=. --remote=origin --push
```

Or run:

```powershell
.\scripts\publish-github.ps1
```

If the repository already exists:

```bash
cd /d D:\ForgePulse
git init
git remote add origin https://github.com/<your-user>/ForgePulse.git
git add .
git commit -m "Initialize ForgePulse project structure"
git branch -M main
git push -u origin main
```
