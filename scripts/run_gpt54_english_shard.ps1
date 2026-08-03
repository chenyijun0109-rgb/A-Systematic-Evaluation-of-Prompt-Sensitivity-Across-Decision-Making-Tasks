param(
    [Parameter(Mandatory = $true)]
    [string]$ShardName,
    [Parameter(Mandatory = $true)]
    [string]$Seeds
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$outputDir = "outputs/model_comparison_en_v01/gpt-5.4/$ShardName"
$logDir = Join-Path $projectRoot "outputs\model_comparison_en_v01\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

& "$projectRoot\.venv\Scripts\python.exe" `
    -m src.run_multilingual_experiment `
    --languages en `
    --seeds $Seeds `
    --model gpt-5.4 `
    --temperature 0.7 `
    --top-p 1.0 `
    --skip-recorded-failures `
    --output-dir $outputDir `
    1>> (Join-Path $logDir "$ShardName.stdout.log") `
    2>> (Join-Path $logDir "$ShardName.stderr.log")
