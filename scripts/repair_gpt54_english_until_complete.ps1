$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$resultRoot = Join-Path $projectRoot "outputs\model_comparison_en_v01\gpt-5.4"

$waves = @(
    @(
        @{ Name = "wave-01-a"; Seeds = "20260708,20260709" },
        @{ Name = "wave-01-b"; Seeds = "20260710,20260711" }
    ),
    @(
        @{ Name = "wave-02-a"; Seeds = "20260712,20260713" },
        @{ Name = "wave-02-b"; Seeds = "20260714,20260715" }
    ),
    @(
        @{ Name = "wave-03-a"; Seeds = "20260716,20260717" },
        @{ Name = "wave-03-b"; Seeds = "20260718,20260719" }
    ),
    @(
        @{ Name = "wave-04-a"; Seeds = "20260720,20260721" },
        @{ Name = "wave-04-b"; Seeds = "20260722,20260723" }
    ),
    @(
        @{ Name = "wave-05-a"; Seeds = "20260724,20260725" },
        @{ Name = "wave-05-b"; Seeds = "20260726,20260727" }
    )
)

function Get-ValidRunCount {
    $count = 0
    Get-ChildItem $resultRoot -Recurse -Filter "*.json" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -ne "multilingual_run_status.json" -and
            $_.Name -notlike "*_failed.json"
        } |
        ForEach-Object {
            try {
                $payload = Get-Content -Raw $_.FullName | ConvertFrom-Json
                if (
                    $payload.done -eq $true -and
                    $payload.prompt_language -eq "en" -and
                    $payload.requested_model -eq "gpt-5.4"
                ) {
                    $count++
                }
            } catch {
                # Ignore non-run or partially written JSON and retry later.
            }
        }
    return $count
}

while ((Get-ValidRunCount) -lt 240) {
    foreach ($wave in $waves) {
        $workers = @()
        foreach ($shard in $wave) {
            $shardPath = Join-Path $resultRoot $shard.Name
            $shardValid = 0
            if (Test-Path $shardPath) {
                Get-ChildItem $shardPath -Recurse -Filter "*.json" |
                    Where-Object {
                        $_.Name -ne "multilingual_run_status.json" -and
                        $_.Name -notlike "*_failed.json"
                    } |
                    ForEach-Object {
                        try {
                            $payload = Get-Content -Raw $_.FullName | ConvertFrom-Json
                            if ($payload.done -eq $true) {
                                $shardValid++
                            }
                        } catch {
                        }
                    }
            }
            if ($shardValid -lt 24) {
                $workers += Start-Process `
                    -FilePath powershell.exe `
                    -ArgumentList @(
                        "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", (Join-Path $PSScriptRoot "run_gpt54_english_repair_shard.ps1"),
                        "-ShardName", $shard.Name,
                        "-Seeds", $shard.Seeds
                    ) `
                    -WorkingDirectory $projectRoot `
                    -WindowStyle Hidden `
                    -PassThru
            }
        }
        if ($workers.Count -gt 0) {
            $workers | Wait-Process
        }
    }
}
