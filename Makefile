PYTHON ?= python

.PHONY: install test paper clean models smoke preflight

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) self_test_v6.py
	$(PYTHON) smoke_test_openrouter_harness.py
	$(PYTHON) self_test_uniqueness.py
	$(PYTHON) self_test_multimodel_protocol.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
	cp paper/main.pdf paper/The_Last_Human_Gate.pdf

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.aux' -o -name '*.log' -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.out' \) -delete

models:
	$(PYTHON) discover_openrouter_models.py --search 'gpt|claude|gemini|glm|deepseek|qwen'

smoke:
	@test -n "$(MODEL)" || (echo "Usage: make smoke MODEL=<openrouter-model-id>" && exit 1)
	$(PYTHON) run_openrouter_benchmark.py --dataset openrouter_smoke_dataset --models $(MODEL) --max-cases 1 --max-cost-usd 1 --output-dir openrouter_results/smoke

preflight:
	@echo "Checking for secrets and generated junk..."
	@test ! -f .env || (echo "WARNING: .env exists locally; it is gitignored"; true)
	@! grep -R --exclude-dir=.git --exclude='*.pdf' --exclude='*.png' --exclude='*.svg' -nE 'sk-or-v1-[A-Za-z0-9_-]{20,}' . | grep -v '.env.example' || (echo "Potential OpenRouter key found" && exit 1)
	@find . -type d -name __pycache__ -print
	@echo "Preflight complete."
