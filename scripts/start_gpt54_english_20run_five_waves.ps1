$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

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

foreach ($wave in $waves) {
    $workers = foreach ($shard in $wave) {
        Start-Process `
            -FilePath powershell.exe `
            -ArgumentList @(
                "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", (Join-Path $PSScriptRoot "run_gpt54_english_shard.ps1"),
                "-ShardName", $shard.Name,
                "-Seeds", $shard.Seeds
            ) `
            -WorkingDirectory $projectRoot `
            -WindowStyle Hidden `
            -PassThru
    }
    $workers | Wait-Process
}
