$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$resultRoot = Join-Path $projectRoot "outputs\model_comparison_en_v01\gpt-5.4-mini-formal-v01"

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

function Get-ValidCount([string]$Path) {
    $count = 0
    Get-ChildItem $Path -Recurse -Filter "*.json" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "multilingual_run_status.json" -and $_.Name -notlike "*_failed.json" } |
        ForEach-Object {
            try {
                $run = Get-Content -Raw $_.FullName | ConvertFrom-Json
                if ($run.done -eq $true -and $run.prompt_language -eq "en" -and $run.requested_model -eq "gpt-5.4-mini") {
                    $count++
                }
            } catch {}
        }
    return $count
}

while ((Get-ValidCount $resultRoot) -lt 240) {
    for ($index = 0; $index -lt $shards.Count; $index += 2) {
        $workers = @()
        foreach ($shard in $shards[$index..($index + 1)]) {
            $shardPath = Join-Path $resultRoot $shard.Name
            if ((Get-ValidCount $shardPath) -lt 24) {
                $workers += Start-Process -FilePath powershell.exe -ArgumentList @(
                    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    (Join-Path $PSScriptRoot "run_gpt54mini_english_shard.ps1"),
                    "-ShardName", $shard.Name, "-Seeds", $shard.Seeds, "-Repair"
                ) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
            }
        }
        if ($workers.Count -gt 0) { $workers | Wait-Process }
    }
}

