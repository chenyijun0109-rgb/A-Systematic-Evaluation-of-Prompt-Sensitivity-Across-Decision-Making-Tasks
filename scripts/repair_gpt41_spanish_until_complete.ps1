$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$resultRoot = Join-Path $projectRoot "outputs\formal_multilingual_v01\gpt-4.1-es-20run-v01"
$shards = @(
    @{ Name = "wave-01-a"; Seeds = "20260708,20260709" },
    @{ Name = "wave-01-b"; Seeds = "20260710,20260711" },
    @{ Name = "wave-02-a"; Seeds = "20260712,20260713" },
    @{ Name = "wave-02-b"; Seeds = "20260714,20260715" },
    @{ Name = "wave-03-a"; Seeds = "20260716,20260717" },
    @{ Name = "wave-03-b"; Seeds = "20260718,20260719" },
    @{ Name = "wave-04-a"; Seeds = "20260720,20260721" },
    @{ Name = "wave-04-b"; Seeds = "20260722,20260723" },
    @{ Name = "wave-05-a"; Seeds = "20260724,20260725" },
    @{ Name = "wave-05-b"; Seeds = "20260726,20260727" }
)

function Get-ShardValidCount([string]$shardName) {
    $shardPath = Join-Path $resultRoot $shardName
    if (-not (Test-Path $shardPath)) { return 0 }
    $count = 0
    Get-ChildItem $shardPath -Recurse -Filter "*.json" |
        Where-Object { $_.Name -ne "multilingual_run_status.json" -and $_.Name -notlike "*_failed.json" } |
        ForEach-Object {
            try {
                $payload = Get-Content -Raw $_.FullName | ConvertFrom-Json
                if ($payload.done -eq $true -and $payload.prompt_language -eq "es" -and $payload.requested_model -eq "gpt-4.1-2025-04-14") { $count++ }
            } catch {}
        }
    return $count
}

while ($true) {
    $incomplete = @($shards | Where-Object { (Get-ShardValidCount $_.Name) -lt 24 })
    if ($incomplete.Count -eq 0) { break }
    for ($index = 0; $index -lt $incomplete.Count; $index += 2) {
        $last = [Math]::Min($index + 1, $incomplete.Count - 1)
        $pair = @($incomplete[$index..$last])
        $workers = foreach ($shard in $pair) {
            Start-Process -FilePath powershell.exe `
                -ArgumentList @(
                    "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", (Join-Path $PSScriptRoot "run_gpt41_spanish_shard.ps1"),
                    "-ShardName", $shard.Name, "-Seeds", $shard.Seeds, "-Repair"
                ) `
                -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
        }
        $workers | Wait-Process
    }
}

