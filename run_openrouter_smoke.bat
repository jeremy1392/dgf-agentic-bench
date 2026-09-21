@echo off
setlocal
if "%~1"=="" (
  echo Usage: run_openrouter_smoke.bat MODEL_ID
  echo Example: run_openrouter_smoke.bat z-ai/glm-5.3-flashx
  exit /b 1
)
python run_openrouter_benchmark.py --dataset openrouter_smoke_dataset --models %1 --max-cases 1 --max-cost-usd 1.00 --output-dir openrouter_results\smoke
endlocal
