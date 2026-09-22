param(
    [switch]$RunPilot = $false,
    [double]$MaxCostUsd = 25,
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

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " DGF-BENCH - VERIFY PYTHON ENVIRONMENT" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

if (-not (Test-Path $VenvPython)) {
    throw ".venv not found. Run fix_dgf_python_env.ps1 first."
}

Write-Host "[1/3] Python environment" -ForegroundColor Yellow
& $VenvPython -c "import sys; print(sys.executable)"
if ($LASTEXITCODE -ne 0) { throw "Python environment failed." }

Write-Host ""
Write-Host "[2/3] Import check" -ForegroundColor Yellow
& $VenvPython -c "import docx, PIL, cffi, cairocffi, cairosvg; print('Imports OK - CairoSVG', cairosvg.__version__)"
if ($LASTEXITCODE -ne 0) { throw "Dependency import check failed." }

Write-Host ""
Write-Host "[3/3] Real SVG -> PNG test" -ForegroundColor Yellow

# Use a temporary Python file rather than python -c.
# This completely avoids PowerShell/Python nested-quote problems.
$TestFile = Join-Path $env:TEMP "dgf_cairo_render_test.py"

@'
import cairosvg

svg = b"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20">
<rect width="20" height="20" fill="white"/>
</svg>"""

png = cairosvg.svg2png(bytestring=svg)

if len(png) <= 50:
    raise RuntimeError("PNG output was unexpectedly small")

print(f"CairoSVG SVG->PNG render test: OK ({len(png)} bytes)")
'@ | Set-Content -Path $TestFile -Encoding UTF8

try {
    & $VenvPython $TestFile
    if ($LASTEXITCODE -ne 0) {
        throw "CairoSVG rendering test failed."
    }
}
finally {
    Remove-Item $TestFile -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host " ENVIRONMENT IS READY" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Use this Python for DGF-Bench:" -ForegroundColor Cyan
Write-Host "  $VenvPython"
Write-Host ""

if ($RunPilot) {
    $RunnerCandidates = @(
        (Join-Path $RepoRoot "run_full_experiment.py"),
        (Join-Path $RepoRoot "run_dgf_experiment_v7_3.py"),
        (Join-Path $RepoRoot "run_dgf_experiment.py")
    )
    $Runner = $RunnerCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $Runner) {
        throw "No DGF-Bench experiment runner found."
    }

    Write-Host "Starting pilot..." -ForegroundColor Green
    Write-Host "The OpenRouter key should be entered when the Python runner asks for it." -ForegroundColor Yellow
    Write-Host ""

    $ArgsList = @($Runner, "--models") + $Models + @(
        "--preset", "pilot",
        "--max-cost-usd", "$MaxCostUsd"
    )

    & $VenvPython @ArgsList
    exit $LASTEXITCODE
}
else {
    Write-Host "To launch the pilot now:" -ForegroundColor Cyan
    Write-Host '  powershell -ExecutionPolicy Bypass -File .\verify_dgf_env.ps1 -RunPilot'
    Write-Host ""
}
