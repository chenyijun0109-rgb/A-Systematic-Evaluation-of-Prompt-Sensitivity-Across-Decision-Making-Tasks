$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$logDir = Join-Path $projectRoot "outputs\model_comparison_en_v01\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

& "$projectRoot\.venv\Scripts\python.exe" `
    -m src.run_llm_pilot `
    --tasks horizon `
    --condition baseline `
    --seed 20260709 `
    --model gpt-5.4 `
    --temperature 0.7 `
    --top-p 1.0 `
    --language en `
    --output-dir outputs/model_comparison_en_v01/gpt-5.4/wave-01-a/en `
    1>> (Join-Path $logDir "wave-01-a-horizon-baseline-retry4.stdout.log") `
    2>> (Join-Path $logDir "wave-01-a-horizon-baseline-retry4.stderr.log")

& "$projectRoot\.venv\Scripts\python.exe" `
    -m src.run_llm_pilot `
    --tasks bart `
    --condition baseline `
    --seed 20260710 `
    --model gpt-5.4 `
    --temperature 0.7 `
    --top-p 1.0 `
    --language en `
    --output-dir outputs/model_comparison_en_v01/gpt-5.4/wave-01-b/en `
    1>> (Join-Path $logDir "wave-01-b-bart-baseline-retry4.stdout.log") `
    2>> (Join-Path $logDir "wave-01-b-bart-baseline-retry4.stderr.log")
