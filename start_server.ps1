$ErrorActionPreference = "Stop"

$backendPath = Join-Path $PSScriptRoot "backend"
$pidPath = Join-Path $backendPath ".elevate-server.pid"
$stdoutPath = Join-Path $backendPath "elevate-server.out.log"
$stderrPath = Join-Path $backendPath "elevate-server.err.log"
$env:WT_SESSION = "Elevate"

$alreadyListening = Test-NetConnection -ComputerName "127.0.0.1" -Port 8010 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($alreadyListening) {
    Write-Host "Elevate is already responding at http://127.0.0.1:8010/"
    exit 0
}

$pythonCommand = Get-Command python -ErrorAction Stop
$serverProcess = Start-Process `
    -FilePath $pythonCommand.Source `
    -ArgumentList @("manage.py", "runserver", "127.0.0.1:8010", "--noreload", "--no-color") `
    -WorkingDirectory $backendPath `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

Set-Content -LiteralPath $pidPath -Value $serverProcess.Id

for ($attempt = 0; $attempt -lt 12; $attempt++) {
    Start-Sleep -Seconds 1
    $serverProcess.Refresh()

    if ($serverProcess.HasExited) {
        Remove-Item -LiteralPath $pidPath -ErrorAction SilentlyContinue
        Write-Host "Django stopped before port 8010 opened. Server output:"
        if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Tail 30 }
        if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Tail 30 }
        exit 1
    }

    $isListening = Test-NetConnection -ComputerName "127.0.0.1" -Port 8010 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($isListening) {
        Write-Host "Elevate is running at http://127.0.0.1:8010/ (PID $($serverProcess.Id))."
        Write-Host "You can close this launcher window. Use stop_server.bat to stop Elevate."
        exit 0
    }
}

Write-Host "Django is running but port 8010 did not respond. Server output:"
if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Tail 30 }
if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Tail 30 }
exit 1
