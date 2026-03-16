"""
QUICK START GUIDE - Run This First!
"""

# 🚀 RAPID STARTUP CHECKLIST (2-3 Weeks to Delivery)

## ✅ Step 1: Verify Project Structure (2 minutes)

Open Windows Explorer and verify these folders exist:
```
d:\WPPDigitalTwin\
├── data\raw\              ✓
├── data\processed\        ✓
├── preprocessing\         ✓
├── twin\                  ✓
├── forecasting\           ✓
├── blockchain\            ✓
├── hashing\               ✓
├── sync\                  ✓
├── dashboard\             ✓
├── experiments\           ✓
├── paper_results\         ✓
├── tests\                 ✓
├── docs\                  ✓
├── docker\                ✓
└── .github\workflows\     ✓
```

**Status**: ✓ COMPLETE (All 16 folders present)

---

## ✅ Step 2: Install Python Dependencies (5-10 minutes)

```powershell
# Windows PowerShell
cd d:\WPPDigitalTwin

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies (includes kagglehub for auto-download)
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import pandas; import kagglehub; print('✓ All dependencies installed')"
```

**Expected Output**: `✓ All dependencies installed`

---

## ✅ Step 3: Download Dataset (Automatic - 2 minutes)

### Option A: Automated Download (RECOMMENDED ⭐)
```powershell
# Automatically downloads dataset from Kaggle to correct location
make download
```

**Benefits:**
- ✅ Automatic and fast
- ✅ Places data in correct location (`data/raw/`)
- ✅ No manual file moving required
- ✅ Works on Windows, Mac, Linux

### Option B: Manual Download (If automatic fails)
1. Visit: https://www.kaggle.com/datasets/pythonafroz/wind-turbine-scada-data
2. Download CSV file
3. Save to: `data/raw/kaggle_scada.csv`

**Verify**: 
```powershell
dir data\raw\  # Should show kaggle_scada.csv
```

---

## ✅ Step 4: Copy Configuration Template (2 minutes)

```powershell
copy .env.example .env
```

Edit `.env` with your settings (optional for research):
- `MONGODB_URI=mongodb://localhost:27017`
- `GANACHE_RPC_URL=http://localhost:8545`

---

## ✅ Step 5: Run Full Pipeline (3-4 hours)

### Option A: Run All at Once (FAST - Recommended)
```powershell
make run-all
```
This executes all phases in order:
- Preprocessing → Twin validation → Forecasting → Blockchain → Experiments

### Option B: Run Individual Phases (FLEXIBLE)
```powershell
# Phase 1: Preprocessing
python preprocessing/run_pipeline.py

# Phase 2: Twin validation
python twin/validate_twin.py

# Phase 3: Forecasting
python forecasting/train_models.py

# Phase 4&5: Hashing
python hashing/batch_hasher.py

# Phase 6: Blockchain (requires separate terminal with `npx hardhat node`)
cd blockchain
npm install
npx hardhat compile

# Phase 7: Sync
python sync/blockchain_sync.py

# Phase 8: Experiments
python experiments/run_all_experiments.py

# Phase 9: Dashboard
streamlit run dashboard/app.py  # Opens http://localhost:8501
```

---

## ✅ Step 6: Verify Results (5 minutes)

After execution, check these files exist:

```
✓ data/processed/scada_preprocessed.csv          (10K+ records)
✓ experiments/twin_validation_results.csv         (Accuracy metrics)
✓ experiments/forecast_results.csv                (Model comparison)
✓ experiments/hourly_hashes.csv                   (168+ hashes)
✓ sync/sync_logs.json                             (Blockchain logs)
✓ paper_results/experiment_results.json           (All findings)
```

---

## 📊 Dashboard Quick Tour (1 minute)

After launching Streamlit:
```bash
streamlit run dashboard/app.py
```

Browse these tabs:
1. **📊 Raw Data** — View SCADA time series
2. **👯 Digital Twin** — See twin accuracy metrics
3. **🔮 Forecasting** — Compare ML models
4. **⛓️ Blockchain Anchors** — View hash history
5. **✓ Integrity Check** — Test tamper detection

---

## ✅ Step 7: Run Tests (2 minutes)

Verify code quality:
```powershell
pytest tests/ -v --cov=preprocessing --cov=twin
```

Expected: All tests pass ✓

---

## ✅ Step 8: Prepare for Submission (30 minutes)

### Generate Conference-Ready Artifacts:

```
paper_results/
├── experiment_results.json              (Main findings)
├── Table_1_Twin_Accuracy.csv           (Table: MAE, RMSE, R²)
├── Table_2_Forecast_Comparison.csv     (Table: Model metrics)
├── Table_3_Scalability.csv             (Hybrid vs full-chain)
└── conference_paper_draft.pdf          (8-10 pages)
```

**Write paper sections:**
1. Intro (from proposal)
2. Related Work (blockchain + digital twins)
3. Methodology (our hybrid approach)
4. Experiments (4 experiments A-D)
5. Results (Tables 1-4)
6. Conclusion

---

## ⏱️ Timeline (2-3 Week Compressed Execution)

| Week | Focus | Time | Status |
|------|-------|------|--------|
| **Week 1** | Setup + Preprocessing + Twin | 20-25 hrs | ⚡ Run now |
| **Week 2** | Forecasting + Blockchain | 15-20 hrs | Parallel |
| **Week 3** | Experiments + Paper | 15-20 hrs | Final push |
| **TOTAL** | Complete delivery | 50-65 hrs | ✓ **Ready** |

---

## 🎯 Success Criteria

After 2-3 weeks, you should have:

- [ ] ✓ Clean SCADA data (data/processed/)
- [ ] ✓ Twin validation report (MAE < 500 kW)
- [ ] ✓ 2 trained ML models (Linear + RF)
- [ ] ✓ 4 experiment tables + findings
- [ ] ✓ Live Streamlit dashboard
- [ ] ✓ Blockchain deployment on testnet
- [ ] ✓ GitHub repository with CI/CD
- [ ] ✓ 8-10 page conference paper draft
- [ ] ✓ Full reproducibility documentation

---

## 🔧 Troubleshooting

**"ModuleNotFoundError: pandas"**
→ Virtual environment not activated: `.venv\Scripts\activate`

**"Dataset not found"**
→ Download CSV and save to: `data/raw/kaggle_scada.csv`

**"Port 8501 already in use"**
→ Use different port: `streamlit run dashboard/app.py --server.port=8502`

**"Out of memory"**
→ Process smaller batches or use machine with 16GB+ RAM

**"Tests fail"**
→ Ensure virtual environment is active and all deps installed

---

## 📞 Next Steps

### Immediate (Now):
1. ✅ Create `.venv` and install dependencies
2. ✅ Download kaggle_scada.csv
3. ✅ Run `make run-all` (takes 3-4 hours)

### Week 1-2:
4. Monitor experiments progress
5. Verify all result files generate
6. Test dashboard locally

### Week 2-3:
7. Write conference paper draft
8. Create GitHub public repo
9. Push to GitHub with CI/CD workflows
10. Submit paper + code

---

## CI/CD Automation

**GitHub Actions workflows will:**
- ✅ Auto-run tests on every commit
- ✅ Auto-preprocess data daily (if dataset available)
- ✅ Auto-generate result artifacts
- ✅ Publish results to Actions artifacts

**After pushing to GitHub:**
```bash
git add .
git commit -m "Initial WPP Digital Twin prototype - all phases complete"
git push origin main
# Watch: GitHub → Actions tab for automated testing
```

---

## 📚 Documentation

- `README.md` — Complete overview
- `docs/ARCHITECTURE.md` — System design
- `docs/DATA_SCHEMA.md` — MongoDB schema
- `docs/REPRODUCIBILITY.md` — Step-by-step reproduction

---

## 🎓 Publication Path

**Next Steps After 2-Week Work:**

1. **Conference Submission** (Week 3)
   - Target: IEEE Sustainable Energy Technology Conf
   - Format: 8-10 pages, peer-reviewed
   - Deadline: Check call for papers

2. **GitHub Release** (Week 3)
   - Tag: v0.1.0-research-prototype
   - Upload: paper_results artifacts
   - Document: reproducibility guide

3. **Extended Work** (Future)
   - Integrate Chainlink oracle
   - Deploy to Polygon L2
   - Scale to 100+ turbines
   - Real-time dashboard (real data)

---

**🚀 Ready? Start with: `make setup && make install`**

**⏰ You have 2-3 weeks. Let's build! ✨**

---

*Last Updated: March 9, 2025 | All tools & code ready to execute*
