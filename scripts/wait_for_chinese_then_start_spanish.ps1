$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$chineseRoot = Join-Path $projectRoot "outputs\formal_multilingual_v01\gpt-4.1-zh-CN-20run-v01"
$handoffLog = Join-Path $projectRoot "outputs\formal_multilingual_v01\logs\gpt-4.1-es-20run-v01\handoff.log"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $handoffLog) | Out-Null

function Get-ChineseValidCount {
    $count = 0
    Get-ChildItem $chineseRoot -Recurse -Filter "*.json" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "multilingual_run_status.json" -and $_.Name -notlike "*_failed.json" } |
        ForEach-Object {
            try {
                $payload = Get-Content -Raw $_.FullName | ConvertFrom-Json
                if ($payload.done -eq $true -and $payload.prompt_language -eq "zh-CN" -and $payload.requested_model -eq "gpt-4.1-2025-04-14") { $count++ }
            } catch {}
        }
    return $count
}

while ((Get-ChineseValidCount) -lt 240) { Start-Sleep -Seconds 60 }
"$(Get-Date -Format o) Chinese 240/240 complete; starting Spanish." | Add-Content $handoffLog
& (Join-Path $PSScriptRoot "start_gpt41_spanish_20run_five_waves.ps1")
"$(Get-Date -Format o) Spanish scheduler finished." | Add-Content $handoffLog

