$ErrorActionPreference = "Stop"

$pidPath = Join-Path $PSScriptRoot "backend\.elevate-server.pid"
if (-not (Test-Path -LiteralPath $pidPath)) {
    Write-Host "No Elevate background server PID file was found."
    exit 0
}

$serverId = [int](Get-Content -LiteralPath $pidPath -Raw)
$serverProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $serverId"
if ($null -eq $serverProcess) {
    Remove-Item -LiteralPath $pidPath -ErrorAction SilentlyContinue
    Write-Host "The Elevate server was already stopped."
    exit 0
}

if ($serverProcess.CommandLine -notmatch "manage.py.*runserver.*127\.0\.0\.1:8010") {
    throw "PID $serverId is not the expected Elevate development server; it was left running."
}

Stop-Process -Id $serverId
Remove-Item -LiteralPath $pidPath -ErrorAction SilentlyContinue
Write-Host "Elevate server stopped."
