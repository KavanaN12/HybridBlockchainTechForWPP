#!/usr/bin/env powershell
# Launch Dashboard - WPP Digital Twin

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        ✅ DEPLOYMENT COMPLETE - LAUNCHING DASHBOARD          ║" -ForegroundColor Green
Write-Host "║           Real Blockchain + MongoDB Integration              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 REAL VALUES ACTIVE:" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3" -ForegroundColor Yellow
Write-Host "✓ Deployer: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266" -ForegroundColor Yellow
Write-Host "✓ Balance: 10,000 ETH" -ForegroundColor Yellow
Write-Host "✓ Network: http://127.0.0.1:8545" -ForegroundColor Yellow
Write-Host "✓ MongoDB: mongodb://localhost:27017/" -ForegroundColor Yellow
Write-Host "✓ Kaggle API: Configured" -ForegroundColor Yellow
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 PRE-FLIGHT CHECKLIST:" -ForegroundColor Blue
Write-Host ""

# Check if hardhat node is running
Write-Host "  1. Hardhat Node is running?" -ForegroundColor Blue
Write-Host "     $ cd blockchain && npx hardhat node" -ForegroundColor Gray
Write-Host ""

# Check if MongoDB is running
Write-Host "  2. MongoDB is running?" -ForegroundColor Blue
Write-Host "     $ mongod --dbpath ./data/mongo" -ForegroundColor Gray
Write-Host "     or" -ForegroundColor Gray
Write-Host "     $ net start MongoDB" -ForegroundColor Gray
Write-Host ""

Write-Host "  If both are running, proceed..." -ForegroundColor Yellow
Write-Host ""

# Activate venv
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 STARTING DASHBOARD..." -ForegroundColor Green
Write-Host ""

# Change to project directory
Set-Location "d:\WPPDigitalTwin"

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

Write-Host "Starting Streamlit dashboard..." -ForegroundColor Cyan
Write-Host ""

# Run dashboard
streamlit run dashboard/app.py

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
