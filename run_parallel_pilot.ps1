param(
    [int]$Workers = 6,
    [double]$MaxCostUsd = 25,
    [int]$MaxOutputTokens = 8192,
    [string[]]$Models = @(
        "z-ai/glm-5.3-flash",
        "deepseek/deepseek-v4.1-flash",
        "google/gemini-3.8-flash"
    )
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Project virtual environment not found. Run fix_dgf_python_env.ps1 first."
}

Write-Host "DGF-Bench parallel pilot" -ForegroundColor Cyan
Write-Host "Workers: $Workers"
Write-Host "Models: $($Models -join ', ')"
Write-Host "Cost cap: `$$MaxCostUsd"
Write-Host "The OpenRouter key will be requested by the Python runner if it is not already in the environment." -ForegroundColor Yellow
Write-Host ""

$argsList = @(
    "run_full_experiment.py",
    "--models"
) + $Models + @(
    "--preset", "pilot",
    "--schedule", "round_robin",
    "--workers", "$Workers",
    "--max-workers-per-model", "0",
    "--job-budget-reserve-usd", "0.50",
    "--max-output-tokens", "$MaxOutputTokens",
    "--max-cost-usd", "$MaxCostUsd"
)

& $Python @argsList
exit $LASTEXITCODE
