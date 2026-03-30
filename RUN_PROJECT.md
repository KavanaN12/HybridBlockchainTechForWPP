# RUN_PROJECT.md

## WPP Digital Twin - Full Start-to-Streamlit Guide

This document describes the exact commands to run a complete local instance from Python environment activation through the Streamlit dashboard.

---

## 1) Activate Python virtual environment

```powershell
cd D:\WPPDigitalTwin
& .\.venv\Scripts\Activate.ps1
```

- Confirm prompt shows `(venv)` or similar.
- Python should run from `.venv`.

## 2) Start Hardhat local blockchain (keep open)

```powershell
cd D:\WPPDigitalTwin\blockchain
npx hardhat node
```

- Keep this terminal running (or set `isBackground: true`).
- It reported accounts and RPC at `http://127.0.0.1:8545`.

## 3) Compile and deploy contracts

In a second terminal (activated venv):

```powershell
cd D:\WPPDigitalTwin\blockchain
npx hardhat compile
cd scripts
node deploy_trading.js
```

Expected result:
- `EnergyToken` and `AuctionEngine` deployed
- Integration checks pass
- `DEPLOYMENT COMPLETE`
- `deployment_trading.json` + `.env` updated

## 4) Run trading orchestrator (one-shot hour process)

```powershell
cd D:\WPPDigitalTwin
python sync/trading_orchestrator.py
```

Expected result:
- Logs showing connection to Ganache + auction lifecycle
- `logs/trading_log.json` gets written

## 5) (Optional) Train forecast models

```powershell
cd D:\WPPDigitalTwin
python forecasting/models.py
```

or

```powershell
python -m forecasting.models
```

- Produces `experiments/forecast_results.csv` and `forecasting/models_checkpoint/*_model.pkl`.

## 6) Run Streamlit dashboard

If `streamlit` command works:

```powershell
cd D:\WPPDigitalTwin
streamlit run dashboard/app.py
```

If not:

```powershell
cd D:\WPPDigitalTwin
python -m streamlit run dashboard/app.py
```

- Open browser at `http://localhost:8501`.

## 7) Validate key UI tabs

- Tab 6: Energy Marketplace should show `logs/trading_log.json` entries
- Tab 7: Settlement Tracker should show auction info
- Forecast block should show trained model metrics and not the warning message after step 5

## 8) Quick sanity checks (post-run)

```powershell
# Check generated env values
type .env

# First 5 trades
powershell -NoProfile -Command "Get-Content logs\trading_log.json | Select-Object -First 5"

# Re-run orchestrator if needed
python sync/trading_orchestrator.py
```

---

## FAQ / troubleshooting

- "Cannot connect to Ganache": Make sure Hardhat node is running at `localhost:8545` and `.env` has deployed addresses.
- "Forecast evaluation produced no results": Run `python forecasting/models.py` and refresh dashboard.
- "Forecast file format missing timestamp": This is now handled by blueprint fallback in `sync/trading_orchestrator.py` with synthetic fallback.

---

## Optional: one-shot `run_all` script
A simple PowerShell script can call these commands in sequence with waits in between.

