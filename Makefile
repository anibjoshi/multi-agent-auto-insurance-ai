.PHONY: help install install-dev test demo api clean format lint typecheck build benchmark quick-benchmark process-datasets

help: ## Show this help message
	@echo "Multi-Agent Auto Insurance Claim Processing System"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package and dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run the test system
	python3 -m pytest tests/ -v
	python3 tests/test_system.py

demo: ## Run the interactive demo
	python3 scripts/demo_react.py

api: ## Start the API server
	python3 api/main.py

process-datasets: ## Consolidate all labeled datasets into unified benchmark
	PYTHONPATH=. python3 benchmarks/scripts/dataset_processor.py

quick-benchmark: ## Run quick accuracy test (5 claims from consolidated dataset)
	PYTHONPATH=. python3 benchmarks/scripts/quick_test.py consolidated 5

benchmark: ## Run scalable benchmark on consolidated dataset
	PYTHONPATH=. python3 benchmarks/scripts/benchmark_runner.py consolidated

benchmark-train: ## Run benchmark on training split (490 claims)
	PYTHONPATH=. python3 benchmarks/scripts/benchmark_runner.py consolidated_train

benchmark-val: ## Run benchmark on validation split (105 claims)
	PYTHONPATH=. python3 benchmarks/scripts/benchmark_runner.py consolidated_val

benchmark-test: ## Run benchmark on test split (105 claims)
	PYTHONPATH=. python3 benchmarks/scripts/benchmark_runner.py consolidated_test

benchmark-full: ## Run full benchmark on all consolidated claims (700 claims)
	@echo "📊 Running full benchmark on consolidated dataset (700 claims)..."
	PYTHONPATH=. python3 benchmarks/scripts/benchmark_runner.py consolidated

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf benchmarks/results/*.log benchmarks/results/*.json

format: ## Format code with black
	black src/ api/ tests/ scripts/ benchmarks/ --line-length 100

lint: ## Lint code with flake8
	flake8 src/ api/ tests/ scripts/ benchmarks/ --max-line-length 100 --ignore E203,W503

typecheck: ## Type check with mypy
	mypy src/ --ignore-missing-imports

build: ## Build the package
	python3 setup.py sdist bdist_wheel

# Docker commands (if needed in the future)
docker-build: ## Build Docker image
	docker build -t multi-agent-claim-processor .

docker-run: ## Run Docker container
	docker run -p 8000:8000 multi-agent-claim-processor

# Environment setup
env-setup: ## Set up development environment
	python3 -m venv venv
	@echo "Activate the virtual environment with: source venv/bin/activate"
	@echo "Then run: make install-dev" 