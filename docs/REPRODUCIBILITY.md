"""
REPRODUCIBILITY.md
Step-by-step guide to reproduce all experiments
"""

# WPP Digital Twin - Complete Reproducibility Guide

This document provides exact steps to reproduce all experiments and results from scratch.

## Prerequisites

- **OS**: Windows 10+, macOS, or Linux
- **Python**: 3.11+ (from python.org)
- **Git**: Latest version
- **Docker**: (Optional) for MongoDB
- **Node.js**: 18+ (Optional, for blockchain contracts)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB minimum

## Step-by-Step Reproduction

### Step 1: Environment Setup (10 minutes)

```bash
# 1.1 Clone repository
cd d:\
git clone https://github.com/[your-username]/WPPDigitalTwin.git
cd WPPDigitalTwin

# 1.2 Create Python virtual environment
python -m venv .venv

# 1.3 Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 1.4 Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Data Acquisition (5-30 minutes, depending on download speed)

```bash
# 2.1 Download dataset manually
# Visit: https://www.kaggle.com/datasets/pythonafroz/wind-turbine-scada-data
# Download CSV file and place it in the following directory:
# d:/WPPDigitalTwin/data/raw/kaggle_scada.csv

# 2.2 Verify dataset integrity
python verify_project_quality.py --check-data
```

### Step 3: Preprocessing Pipeline (5 minutes)

```bash
# 3.1 Run preprocessing pipeline
python preprocessing/run_pipeline.py

# 3.2 Verify preprocessing outputs
python verify_project_quality.py --check-preprocessing
```

### Step 4: Phase 1 - Data Preprocessing (20 minutes)

```bash
# 4.1 Run preprocessing pipeline
cd preprocessing
python run_pipeline.py

# 4.2 Verify output
# Expected: data/processed/scada_preprocessed.csv (with cleaned data)
dir ..\data\processed\

# 4.3 Run tests
cd ..
pytest tests/test_preprocessing.py -v
# Expected: All tests pass (4 test cases)
```

**Output Files:**
- `data/processed/scada_preprocessed.csv` (10K+ cleaned records)

### Step 5: Phase 2 - Digital Twin Validation (15 minutes)

```bash
# 5.1 Run twin validation
cd twin
python validate_twin.py

# 5.2 Verify results
dir ..\experiments\twin_validation_results.csv

# 5.3 Run twin tests
cd ..
pytest tests/test_twin.py -v
# Expected: 5 tests pass
```

**Expected Metrics (from `experiments/twin_validation_results.csv`):**
- MAE: < 500 kW (< 5% of 5000 kW rated)
- RMSE: < 800 kW (< 10% of rated)
- R²: > 0.85 (high fidelity)

### Step 6: Phase 3 - Forecasting Models (15 minutes)

```bash
# 6.1 Train forecasting models
cd forecasting
python train_models.py

# 6.2 Verify models trained
dir models_checkpoint\  # Should show: linear_model.pkl, random_forest_model.pkl
dir ..\experiments\forecast_results.csv

# 6.3 Check results
type ..\experiments\forecast_results.csv
# Expected: MAE, RMSE, MAPE for each model
```

**Expected Results:**
- 2 models trained (Linear Regression + Random Forest)
- CSV with metrics for each model

### Step 7: Phase 4 - Off-Chain Storage Setup (10 minutes)

```bash
# 7.1 Start MongoDB (requires Docker)
cd docker
docker-compose up -d mongodb

# 7.2 Verify MongoDB running
# Check: http://localhost:8081 (Mongo Express should load)

# 7.3 Initialize collections
cd ..
python hashing/batch_hasher.py
# This creates 4 MongoDB collections (simulated locally for research)
```

### Step 8: Phase 5 - Hash Generation (10 minutes)

```bash
# 8.1 Generate hourly hashes
cd hashing
python batch_hasher.py

# 8.2 Verify hashes
type ..\experiments\hourly_hashes.csv
# Expected: ~168 hourly batches (7 days of data)
```

**Output:**
- `experiments/hourly_hashes.csv` (hour, batch_hash, record_count)

### Step 9: Phase 6 - Blockchain Setup (20 minutes)

```bash
# 9.1 Install blockchain dependencies
cd blockchain
npm install

# 9.2 Compile contracts
npx hardhat compile
# Expected: Successfully compiled DataAnchor.sol

# 9.3 Run contract tests
npx hardhat test
# Expected: All contract tests pass

# 9.4 Create local blockchain (in separate terminal)
npx hardhat node
# Keep this running; note the account addresses
```

### Step 10: Phase 7 - Synchronization (10 minutes)

```bash
# 10.1 Run sync engine (main terminal, after blockchain running)
cd sync
python blockchain_sync.py

# 10.2 Verify sync logs
type sync_logs.json
# Expected: JSON with tx IDs for each batch
```

### Step 11: Phase 8 - Dashboard (5 minutes)

```bash
# 11.1 Launch Streamlit
cd dashboard
streamlit run app.py

# 11.2 Access dashboard
# Automatically opens: http://localhost:8501
# Check all 5 tabs load successfully

# 11.3 Test "Run Tamper Detection" button
# Expected: ✓ Hash verification results
```

### Step 12: Phase 9&10 - Run All Experiments (30 minutes)

```bash
# 12.1 Execute full experiment suite
cd experiments
python run_all_experiments.py

# 12.2 Verify results
type ..\paper_results\experiment_results.json

# 12.3 Check results files:
dir ..\paper_results\
# Expected files:
# - experiment_results.json
# - Tables 1-6 (scalability, accuracy, etc.)
```

**Experiment Outputs:**
- **Exp A**: Transaction reduction factor (should be ~60x)
- **Exp B**: Twin accuracy metrics (R² > 0.85)
- **Exp C**: Best forecasting model (RMSE comparison)
- **Exp D**: Hash interval trade-offs

### Step 13: CI/CD Verification (5 minutes)

```bash
# 13.1 Run all tests (simulates GitHub Actions)
pytest tests/ -v --cov=preprocessing --cov=twin --cov=forecasting

# 13.2 Expected output
# ✓ test_preprocessing.py: 4 passed
# ✓ test_twin.py: 5 passed
# ✓ code coverage > 80%
```

### Step 14: Generate Complete Report (10 minutes)

```bash
# 14.1 Verify all deliverables exist
ls -R data/processed/              # Cleaned data
ls experiments/                    # All result CSVs & JSON
ls paper_results/                  # Publication files
ls sync/sync_logs.json             # Blockchain logs

# 14.2 Create summary
# All expected files present = Success ✓
```

## Full Execution Timeline

| Phase | Task | Duration | Cumulative |
|-------|------|----------|-----------|
| 1 | Environment | 10 min | 10 min |
| 2 | Data download | 20 min | 30 min |
| 3 | Preprocessing | 20 min | 50 min |
| 4 | Twin validation | 15 min | 65 min |
| 5 | Forecasting | 15 min | 80 min |
| 6 | MongoDB setup | 10 min | 90 min |
| 7 | Hash generation | 10 min | 100 min |
| 8 | Blockchain | 20 min | 120 min |
| 9 | Sync engine | 10 min | 130 min |
| 10 | Dashboard | 5 min | 135 min |
| 11 | Experiments | 30 min | 165 min |
| 12 | CI/CD tests | 5 min | 170 min |

**Total: ~3 hours (automated parallel execution shorter)**

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution**: Ensure virtual environment is activated:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### Issue: "Dataset not found at data/raw/kaggle_scada.csv"
**Solution**: Download from Kaggle and place CSV in correct location

### Issue: "MongoDB connection refused"
**Solution**: Start MongoDB first:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Issue: "Port 8501 already in use"
**Solution**: Use different port:
```bash
streamlit run dashboard/app.py --server.port=8502
```

### Issue: "Out of memory" during preprocessing
**Solution**: Process smaller batches or use machine with more RAM

## Verification Checklist

After full execution, verify:

- [ ] `data/processed/scada_preprocessed.csv` exists
- [ ] `experiments/twin_validation_results.csv` has MAE < 500 kW
- [ ] `experiments/forecast_results.csv` shows 2 models
- [ ] `experiments/hourly_hashes.csv` has 168+ rows
- [ ] `sync/sync_logs.json` contains tx IDs
- [ ] Dashboard loads all 5 tabs
- [ ] `paper_results/experiment_results.json` populated
- [ ] All pytest tests pass (9+ tests)
- [ ] GitHub Actions workflows run successfully (if pushed)

## Publication-Ready Artifacts

The following files are ready for academic submission:

```
paper_results/
├── experiment_results.json          # Main findings
├── Table_1_Twin_Accuracy.csv       # Accuracy metrics
├── Table_2_Forecast_Comparison.csv # ML models
├── Table_3_Scalability.csv         # Hybrid vs full-chain
├── Table_4_Zone_Errors.csv         # Error by operating zone
├── Figure_1_Architecture.png       # System diagram
└── conference_paper_draft.pdf      # 8-10 pages
```

## Performance Benchmarks

Expected performance on reference machine (8GB RAM, SSD):

| Task | Duration | Status |
|------|----------|--------|
| Preprocessing | 5-10 min | ✓ |
| Twin validation | 2-3 min | ✓ |
| Forecasting | 5-10 min | ✓ |
| Hash generation | 1-2 min | ✓ |
| Experiments | 5-10 min | ✓ |
| Dashboard startup | <5 sec | ✓ |

## Next Steps

After successful reproduction:

1. **Submit findings**: Package results for conference/journal
2. **Extend research**: Add more datasets, longer time horizons
3. **Deploy real**: Migrate to Polygon/Optimism for actual production
4. **Scale oracles**: Integrate Chainlink for decentralized attestation

---

**Questions?** Check README.md or open a GitHub issue.

*Last verified: March 2025 | Python 3.11 | All tests passing*
