param([Parameter(Mandatory=$true)][string]$Model)
python run_openrouter_benchmark.py --dataset openrouter_smoke_dataset --models $Model --max-cases 1 --max-cost-usd 1.00 --output-dir openrouter_results/smoke
