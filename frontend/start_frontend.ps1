# VeriPark Frontend Launch Script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (Test-Path "$ScriptDir\package.json") {
    Set-Location "$ScriptDir"
} elseif (Test-Path "$ScriptDir\frontend\package.json") {
    Set-Location "$ScriptDir\frontend"
}

Write-Host "Starting VeriPark Next.js Frontend from $(Get-Location)..." -ForegroundColor Green
npm run dev
