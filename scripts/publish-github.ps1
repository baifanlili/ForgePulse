$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not available in PATH. Install Git for Windows first."
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI is not available in PATH. Install gh and run 'gh auth login' first."
}

gh auth status

if (-not (Test-Path ".git")) {
    git init
}

git add .
git commit -m "Initialize ForgePulse project structure"

$repoName = "ForgePulse"
$existingRemote = git remote get-url origin 2>$null

if (-not $existingRemote) {
    gh repo create $repoName --private --source=. --remote=origin --push
} else {
    git branch -M main
    git push -u origin main
}

Write-Host "ForgePulse has been published to GitHub."
