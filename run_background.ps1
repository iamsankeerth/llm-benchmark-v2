$ErrorActionPreference = "Continue"

$baseDir = "C:\Users\lenovo\Desktop\San\Fun_Projects\LLM Bench Test"
$pythonExe = "$baseDir\venv\Scripts\python.exe"
$script = "$baseDir\scripts\run_benchmarks.py"
$logFile = "$baseDir\logs\benchmarks.log"

New-Item -ItemType Directory -Path "$baseDir\logs" -Force | Out-Null

Write-Host "Starting LLM Benchmark Pipeline..."
Write-Host "Log file: $logFile"

$env:PYTHONIOENCODING = "utf-8"

$process = Start-Process -FilePath $pythonExe -ArgumentList $script -WorkingDirectory $baseDir -NoNewWindow -PassThru -RedirectStandardOutput $logFile -RedirectStandardError "$baseDir\logs\benchmarks_err.log"

Write-Host "Process ID: $($process.Id)"
Write-Host "Monitor with: Get-Content $logFile -Wait -Tail 50"
Write-Host "Stop with: Stop-Process -Id $($process.Id)"
