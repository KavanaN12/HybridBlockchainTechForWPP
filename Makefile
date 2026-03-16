.PHONY: help setup install test run-preprocessing run-twin run-forecast run-mongo run-blockchain run-sync run-dashboard run-experiments run-all clean docs

help:
	@echo "====== WPP Digital Twin - Rapid Execution Commands ======"
	@echo "make setup          - Initialize project (first time only)"
	@echo "make install        - Install all dependencies"
	@echo "make download       - Download dataset from Kaggle (automated)"
	@echo "make test           - Run all unit tests"
	@echo "make run-preprocessing - Execute data preprocessing pipeline"
	@echo "make run-twin       - Run digital twin validation"
	@echo "make run-forecast   - Train & validate forecasting models"
	@echo "make run-mongo      - Start MongoDB (docker)"
	@echo "make run-blockchain - Deploy smart contracts to Ganache"
	@echo "make run-sync       - Execute sync engine"
	@echo "make run-dashboard  - Launch Streamlit dashboard"
	@echo "make run-experiments - Run all 4 experiments (A-D)"
	@echo "make run-all        - Full pipeline (preprocessing -> experiments)"
	@echo "make clean          - Remove generated files & cache"
	@echo "make docs           - Generate documentation"

setup:
	@echo "Setting up WPP Digital Twin project..."
	copy .env.example .env
	@echo "✓ .env created from .env.example (edit with your credentials)"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ All dependencies installed"

download:
	python download_dataset.py

test:
	pytest tests/ -v --cov=preprocessing --cov=twin --cov=forecasting --cov-report=html

run-preprocessing:
	python preprocessing/run_pipeline.py

run-twin:
	python twin/validate_twin.py

run-forecast:
	python forecasting/train_models.py

run-mongo:
	docker-compose -f docker/docker-compose.yml up -d mongodb

run-blockchain:
	cd blockchain && npx hardhat run scripts/deploy.js --network localhost

run-sync:
	python sync/blockchain_sync.py

run-dashboard:
	streamlit run dashboard/app.py

run-experiments:
	python experiments/run_all_experiments.py

run-all: install test run-preprocessing run-twin run-forecast run-blockchain run-sync run-experiments
	@echo "✓ Pipeline complete! Results in experiments/ and paper_results/"

clean:
	cd . & for /d /r . %f in (__pycache__) do @if exist "%f" rmdir /s /q "%f"
	for /r . %f in (*.pyc) do @if exist "%f" del "%f"
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q htmlcov 2>nul || true

docs:
	@echo "✓ Documentation available in docs/ folder"
