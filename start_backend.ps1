# VeriPark Backend Launch Script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (Test-Path "$ScriptDir\backend\src") {
    Set-Location "$ScriptDir"
} elseif (Test-Path "$ScriptDir\src\veripark") {
    Set-Location (Split-Path -Parent "$ScriptDir")
}

Write-Host "Starting VeriPark FastAPI Backend from $(Get-Location)..." -ForegroundColor Cyan
$env:PYTHONPATH = "backend\src"
.\backend\.venv\Scripts\uvicorn veripark.api.main:app --host 127.0.0.1 --port 8000 --reload
