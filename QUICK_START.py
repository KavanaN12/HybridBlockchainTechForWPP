#!/usr/bin/env python3
"""
Quick Start - WPP Digital Twin with Real Blockchain
====================================================
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              WPP DIGITAL TWIN - REAL BLOCKCHAIN INTEGRATION               ║
║                         Quick Start Guide                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ COMPLETED SETUP:

1. ✅ .env file cleaned and ready
2. ✅ blockchain/web3_client.py updated to use DataAnchor only
3. ✅ deployment_trading.json simplified for DataAnchor
4. ✅ Kaggle API token configured
5. ✅ Removed references to EnergyToken and AuctionEngine

════════════════════════════════════════════════════════════════════════════

📋 WHAT'S NEXT - RUN THESE COMMANDS:

════════════════════════════════════════════════════════════════════════════

🟢 TERMINAL 1 - Start Local Blockchain Node
─────────────────────────────────────────────

  $ cd d:\\WPPDigitalTwin\\blockchain
  $ npx hardhat node

  ⏳ Wait for output:
     Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545
     
  📌 KEEP THIS TERMINAL RUNNING!

════════════════════════════════════════════════════════════════════════════

🟡 TERMINAL 2 - Deploy DataAnchor Contract
───────────────────────────────────────────

  $ cd d:\\WPPDigitalTwin\\blockchain
  $ npx hardhat run scripts/deploy.js --network localhost

  ⏳ Wait for output like:
     ════════════════════════════════════════════════════════════════════
     🚀 Deploying DataAnchor Smart Contract
     ════════════════════════════════════════════════════════════════════
     
     📍 Deployer Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
     💰 Account Balance: 10000.0 ETH
     
     ⏳ Deploying DataAnchor contract...
     ✅ DataAnchor deployed successfully!
     📋 Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
     ⛽ Gas Used: 542872
     
     ✅ Deployment and testing complete!

════════════════════════════════════════════════════════════════════════════

🔵 COPY THESE VALUES TO .env FILE:
───────────────────────────────────

Address the deployment output:

  CONTRACT_ADDRESS = <copy from "📋 Contract Address: 0x5FbDB...">
  PRIVATE_KEY = 0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649
                (First test account from hardhat)

Example .env after update:

  MONGO_URI=mongodb://localhost:27017/
  DB_NAME=wpp_db
  RPC_URL=http://127.0.0.1:8545
  PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649
  CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
  KAGGLE_USERNAME=kavanan12
  KAGGLE_KEY=d3799b4b5d852fa6ed45d477ea72b372
  STREAMLIT_SERVER_PORT=8501
  STREAMLIT_SERVER_HEADLESS=true
  LOG_LEVEL=INFO

════════════════════════════════════════════════════════════════════════════

🟢 TERMINAL 3 - Start MongoDB (if not running)
───────────────────────────────────────────────

  If MongoDB is installed and not running:
  $ mongod --dbpath ./data/mongo
  
  Or if MongoDB is a Windows service:
  $ net start MongoDB  (PowerShell as Admin)

════════════════════════════════════════════════════════════════════════════

🟢 TERMINAL 4 - Run Dashboard
──────────────────────────────

  $ cd d:\\WPPDigitalTwin
  $ streamlit run dashboard/app.py
  
  🌐 Opens automatically at: http://localhost:8501
  
  Now you can:
  ✓ Place bids (stored in MongoDB)
  ✓ Run settlement
  ✓ Store on blockchain
  ✓ Verify data integrity

════════════════════════════════════════════════════════════════════════════

🎯 SYSTEM ARCHITECTURE - NOW LIVE:

  USER INTERFACE (Dashboard)
           ↓
  OFF-CHAIN (MongoDB)  ←→  ON-CHAIN (Ethereum/Hardhat)
  • Bids               • DataAnchor contract
  • Settlements        • Batch hashes
  • Predictions        • Integrity verification
           ↓
  PYTHON SERVICES (Bridging)
  • bidding_service.py
  • settlement_service.py
  • hash_service.py
  • web3_client.py (DataAnchor)

════════════════════════════════════════════════════════════════════════════

⚠️  IMPORTANT NOTES:

  1️⃣  Terminal 1 (hardhat node) must ALWAYS be running
  2️⃣  .env is already configured with Kaggle API token
  3️⃣  Fill in CONTRACT_ADDRESS and PRIVATE_KEY from deployment
  4️⃣  MongoDB should be running or accessible
  5️⃣  Each system restart requires redeploying the contract
  6️⃣  Only use test accounts from hardhat (never send real ETH)

════════════════════════════════════════════════════════════════════════════

🚀 YOU'RE READY!

  Follow the terminal steps above to get started.
  Your system is now configured for production-grade testing!

════════════════════════════════════════════════════════════════════════════
""")

print("\n✅ Setup guide complete!\n")
