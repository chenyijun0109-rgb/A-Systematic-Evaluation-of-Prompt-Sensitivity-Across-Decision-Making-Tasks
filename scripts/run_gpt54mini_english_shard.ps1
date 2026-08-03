param(
    [Parameter(Mandatory = $true)][string]$ShardName,
    [Parameter(Mandatory = $true)][string]$Seeds,
    [switch]$Repair
)

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$outputDir = "outputs/model_comparison_en_v01/gpt-5.4-mini-formal-v01/$ShardName"
$logDir = Join-Path $projectRoot "outputs\model_comparison_en_v01\logs\gpt-5.4-mini-formal-v01"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$suffix = if ($Repair) { "-repair" } else { "" }

$arguments = @(
    "-m", "src.run_multilingual_experiment",
    "--languages", "en",
    "--seeds", $Seeds,
    "--model", "gpt-5.4-mini",
    "--temperature", "0.7",
    "--top-p", "1.0",
    "--output-dir", $outputDir
)
if (-not $Repair) {
    $arguments += "--skip-recorded-failures"
}

& "$projectRoot\.venv\Scripts\python.exe" @arguments `
    1>> (Join-Path $logDir "$ShardName$suffix.stdout.log") `
    2>> (Join-Path $logDir "$ShardName$suffix.stderr.log")

