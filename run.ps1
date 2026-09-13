# Run the whole Game Item Store (PostgreSQL + API + Angular) with Docker.
# Usage:
#   .\run.ps1          start (build if needed)
#   .\run.ps1 fresh    wipe the database and start completely from scratch
#   .\run.ps1 stop     stop everything
param([string]$command = "start")

# Note: we do NOT set $ErrorActionPreference = "Stop" because Docker writes normal
# progress to stderr, which PowerShell would otherwise treat as a fatal error.
Set-Location $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is required but was not found. Install Docker Desktop first."
    exit 1
}

if ($command -eq "stop") {
    docker compose down
    Write-Host "Stopped."
    exit 0
}

if ($command -eq "fresh") {
    Write-Host "Wiping database and rebuilding from scratch..."
    docker compose down -v
}

Write-Host "Building and starting containers..."
docker compose up --build -d

Write-Host "Waiting for the API to be ready..."
for ($i = 0; $i -lt 60; $i++) {
    try {
        if ((Invoke-RestMethod "http://localhost:8000/health" -TimeoutSec 2).status -eq "ok") { break }
    } catch {}
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Game Item Store is up:"
Write-Host "  Frontend : http://localhost:4200"
Write-Host "  API docs : http://localhost:8000/docs"
Write-Host ""
Write-Host "Logins:"
Write-Host "  admin / Admin@12345   (admin)"
Write-Host "  demo  / Demo@12345    (regular user)"
Write-Host ""
Write-Host "Stop with: .\run.ps1 stop     Reset data with: .\run.ps1 fresh"
