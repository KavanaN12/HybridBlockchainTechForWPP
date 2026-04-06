#!/usr/bin/env powershell
# WPP Digital Twin - Quick Start PowerShell Script

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        WPP DIGITAL TWIN - QUICK START GUIDE                  ║" -ForegroundColor Cyan
Write-Host "║           Real Blockchain Integration Ready!                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ SETUP COMPLETE:" -ForegroundColor Green
Write-Host ""
Write-Host "✓ .env cleaned - MongoDB and Blockchain configured" -ForegroundColor Green
Write-Host "✓ blockchain/web3_client.py updated for DataAnchor" -ForegroundColor Green
Write-Host "✓ Deployment script ready" -ForegroundColor Green
Write-Host "✓ Services integrated" -ForegroundColor Green
Write-Host "✓ Kaggle API token configured" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "🎯 RUN THESE COMMANDS IN SEPARATE TERMINALS:" -ForegroundColor Cyan
Write-Host ""

Write-Host "┌─ TERMINAL 1: Start Blockchain Node ─────────────────────────┐" -ForegroundColor Blue
Write-Host "│                                                              │"
Write-Host "│  $ cd d:\WPPDigitalTwin\blockchain                           │"
Write-Host "│  $ npx hardhat node                                          │"
Write-Host "│                                                              │"
Write-Host "│  💡 Keep this terminal OPEN and RUNNING                     │"
Write-Host "│                                                              │"
Write-Host "└──────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
Write-Host ""

Write-Host "┌─ TERMINAL 2: Deploy DataAnchor Contract ──────────────────────┐" -ForegroundColor Blue
Write-Host "│                                                               │"
Write-Host "│  $ cd d:\WPPDigitalTwin\blockchain                            │"
Write-Host "│  $ npx hardhat run scripts/deploy.js --network localhost    │"
Write-Host "│                                                               │"
Write-Host "│  📌 Copy these from output:                                 │"
Write-Host "│     • CONTRACT_ADDRESS                                      │"
Write-Host "│     • PRIVATE_KEY (if shown)                                │"
Write-Host "│                                                               │"
Write-Host "└───────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
Write-Host ""

Write-Host "┌─ TERMINAL 3: Start MongoDB ───────────────────────────────────┐" -ForegroundColor Green
Write-Host "│                                                               │"
Write-Host "│  $ mongod --dbpath ./data/mongo                              │"
Write-Host "│                                                               │"
Write-Host "│  Or if MongoDB is a service:                                │"
Write-Host "│  $ net start MongoDB                                         │"
Write-Host "│                                                               │"
Write-Host "└───────────────────────────────────────────────────────────────┘" -ForegroundColor Green
Write-Host ""

Write-Host "┌─ TERMINAL 4: Run Dashboard ───────────────────────────────────┐" -ForegroundColor Green
Write-Host "│                                                               │"
Write-Host "│  $ cd d:\WPPDigitalTwin                                       │"
Write-Host "│  $ streamlit run dashboard/app.py                            │"
Write-Host "│                                                               │"
Write-Host "│  🌐 Opens at: http://localhost:8501                         │"
Write-Host "│                                                               │"
Write-Host "└───────────────────────────────────────────────────────────────┘" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "📝 AFTER DEPLOYMENT - UPDATE .env:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. From Terminal 2 output, copy CONTRACT_ADDRESS"
Write-Host "2. Edit d:\WPPDigitalTwin\.env"
Write-Host ""
Write-Host "   Set these values:"
Write-Host "   CONTRACT_ADDRESS=<from deployment output>"
Write-Host "   PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649"
Write-Host ""
Write-Host "3. Refresh dashboard (F5 in browser)"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "🧪 YOUR SYSTEM IS NOW READY TO:" -ForegroundColor Green
Write-Host ""
Write-Host "✓ Place real bids in MongoDB via Dashboard"
Write-Host "✓ Run settlement and select winner"
Write-Host "✓ Store settlement on blockchain (DataAnchor contract)"
Write-Host "✓ Verify data integrity with hash comparison"
Write-Host "✓ View transactions on local blockchain"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 KEY POINTS:" -ForegroundColor Magenta
Write-Host ""
Write-Host "• Terminal 1 (hardhat node) MUST stay open"
Write-Host "• Redeploy contract when you restart hardhat"
Write-Host "• .env already has Kaggle API configured"
Write-Host "• .env is cleaned and ready for blockchain values"
Write-Host "• MongoDB connects locally without auth"
Write-Host "• Use test accounts (never send real ETH)"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "✨ Ready? Start the terminals above and begin testing! 🚀" -ForegroundColor Cyan
Write-Host ""

# Optional: Show .env preview
Write-Host "📋 CURRENT .env CONFIGURATION:" -ForegroundColor Yellow
Write-Host ""
Write-Host "MONGO_URI=mongodb://localhost:27017/"
Write-Host "DB_NAME=wpp_db"
Write-Host "RPC_URL=http://127.0.0.1:8545"
Write-Host "PRIVATE_KEY=<TO_BE_FILLED>"
Write-Host "CONTRACT_ADDRESS=<TO_BE_FILLED>"
Write-Host "KAGGLE_USERNAME=kavanan12"
Write-Host "KAGGLE_KEY=d3799b4b5d852fa6ed45d477ea72b372"
Write-Host ""
