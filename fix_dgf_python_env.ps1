
param(
    [string]$BasePython = "C:\Python311\python.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " FIX DGF-BENCH PYTHON ENVIRONMENT" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot"
Write-Host ""

if (-not (Test-Path $BasePython)) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        throw "Python not found. Install Python 3.11+ or pass -BasePython."
    }
    $BasePython = $py.Source
}

Write-Host "[1/6] Base Python: $BasePython" -ForegroundColor Yellow

$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (Test-Path $VenvDir) {
    Write-Host "[2/6] Removing old project .venv..." -ForegroundColor Yellow
    try {
        Remove-Item -Recurse -Force $VenvDir
    }
    catch {
        Write-Host "Could not remove .venv. Close any Python process using it, then rerun this script." -ForegroundColor Red
        throw
    }
}
else {
    Write-Host "[2/6] No old .venv found." -ForegroundColor Green
}

Write-Host "[3/6] Creating fresh .venv..." -ForegroundColor Yellow
& $BasePython -m venv $VenvDir
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
    throw "Failed to create .venv"
}

Write-Host "      Venv Python: $VenvPython" -ForegroundColor Green

Write-Host "[4/6] Updating pip/setuptools/wheel INSIDE .venv..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade --no-cache-dir pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    throw "Could not bootstrap pip inside .venv"
}

$Requirements = Join-Path $RepoRoot "requirements.txt"
if (-not (Test-Path $Requirements)) {
    throw "requirements.txt not found in $RepoRoot"
}

Write-Host "[5/6] Installing requirements INSIDE .venv..." -ForegroundColor Yellow
& $VenvPython -m pip install --no-cache-dir -r $Requirements
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed inside .venv"
}

Write-Host "[6/6] Verifying dependencies..." -ForegroundColor Yellow
& $VenvPython -c "import sys; print('Python executable:', sys.executable)"
if ($LASTEXITCODE -ne 0) { throw "Python verification failed" }

& $VenvPython -c "import docx, PIL, cffi, cairocffi, cairosvg; print('Imports OK'); print('CairoSVG', cairosvg.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw "One or more dependencies cannot be imported"
}

& $VenvPython -c 'import cairosvg; svg=b"<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'20\' height=\'20\'><rect width=\'20\' height=\'20\' fill=\'white\'/></svg>"; png=cairosvg.svg2png(bytestring=svg); assert len(png)>50; print("CairoSVG SVG->PNG render test: OK")'
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "CairoSVG imported but rendering failed. Send me the exact error shown above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host " SUCCESS" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Do NOT run this anymore:" -ForegroundColor Yellow
Write-Host "  C:\Python311\python.exe -m pip install -r requirements.txt"
Write-Host ""
Write-Host "Run DGF-Bench with the project Python:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe run_full_experiment.py ..."
Write-Host ""
Write-Host "Example:" -ForegroundColor Cyan
Write-Host '  .\.venv\Scripts\python.exe run_full_experiment.py --models z-ai/glm-5.3-flash deepseek/deepseek-v4.1-flash google/gemini-3.8-flash --preset pilot --max-cost-usd 25'
Write-Host ""
