param(
    [Parameter(Mandatory = $true)]
    [int]$FormalMasterPid
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Wait-Process -Id $FormalMasterPid -ErrorAction SilentlyContinue

& (Join-Path $PSScriptRoot "repair_gpt54_english_until_complete.ps1")
