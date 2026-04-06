#!/usr/bin/env python3
"""
Setup Instructions for Real Blockchain Deployment
===================================================

STEP-BY-STEP GUIDE
"""

import os
import sys

instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║           REAL BLOCKCHAIN SETUP - WPP Digital Twin                        ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ .env file has been CLEANED

Now follow these steps:

┌─ STEP 1: START HARDHAT NODE ─────────────────────────────────────────────┐
│                                                                             │
│ TERMINAL 1:                                                               │
│ $ cd blockchain                                                           │
│ $ npx hardhat node                                                        │
│                                                                             │
│ ⏳ Wait for output like:                                                  │
│    Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545  │
│                                                                             │
│ 📌 NOTE: Keep this terminal RUNNING                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 2: DEPLOY DATANCHOR CONTRACT ──────────────────────────────────────┐
│                                                                             │
│ TERMINAL 2 (in d:\\WPPDigitalTwin):                                       │
│ $ cd blockchain                                                           │
│ $ npx hardhat run scripts/deploy.js --network localhost                 │
│                                                                             │
│ ⏳ You will see output like:                                              │
│                                                                             │
│    ════════════════════════════════════════════════════════════════════  │
│    🚀 Deploying DataAnchor Smart Contract                               │
│    ════════════════════════════════════════════════════════════════════  │
│                                                                             │
│    📍 Deployer Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266  │
│    💰 Account Balance: 10000.0 ETH                                       │
│                                                                             │
│    ⏳ Deploying DataAnchor contract...                                    │
│    ✅ DataAnchor deployed successfully!                                  │
│    📋 Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3  │
│    ⛽ Gas Used: 542872                                                    │
│                                                                             │
│    ✅ Deployment and testing complete!                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 3: COPY DEPLOYMENT VALUES ─────────────────────────────────────────┐
│                                                                             │
│ From the deployment output above, copy:                                  │
│                                                                             │
│ 1️⃣  CONTRACT_ADDRESS (copy from "📋 Contract Address: 0x5FbDB...") │
│ 2️⃣  PRIVATE_KEY (first account from hardhat node)                       │
│                                                                             │
│ Default hardhat test accounts:                                           │
│                                                                             │
│ Private Key #1:                                                          │
│ 0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649   │
│                                                                             │
│ Account Address #1:                                                      │
│ 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 4: UPDATE .env FILE ──────────────────────────────────────────────┐
│                                                                             │
│ Edit d:\\WPPDigitalTwin\\.env and set:                                   │
│                                                                             │
│ CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3            │
│ PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649
│                                                                             │
│ Replace with YOUR actual values from deployment!                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 5: START MONGODB (if not running) ────────────────────────────────┐
│                                                                             │
│ TERMINAL 3:                                                               │
│ $ mongod --dbpath ./data/mongo                                           │
│                                                                             │
│ Or if MongoDB is as a service, just ensure it's running                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 6: RUN DASHBOARD ─────────────────────────────────────────────────┐
│                                                                             │
│ TERMINAL 4 (in d:\\WPPDigitalTwin):                                      │
│ $ streamlit run dashboard/app.py                                         │
│                                                                             │
│ 🌐 Browser will open at http://localhost:8501                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════

🎯 WHAT YOU'LL HAVE:

✅ Real DataAnchor contract on local blockchain
✅ Real MongoDB database for off-chain storage
✅ Real private key for transactions
✅ Dashboard connected to both systems

════════════════════════════════════════════════════════════════════════════

⚠️  IMPORTANT NOTES:

1️⃣  Keep hardhat node running in Terminal 1
2️⃣  Only use test accounts from hardhat
3️⃣  Each time you restart hardhat, you need to redeploy the contract
4️⃣  .env file already cleaned - just fill in the real values
5️⃣  Kaggle API token is already set

════════════════════════════════════════════════════════════════════════════
"""

print(instructions)

# Print .env template
print("\n📝 EXAMPLE .env CONFIGURATION:\n")
print("""# ================================================
# MongoDB Configuration (Local)
MONGO_URI=mongodb://localhost:27017/
DB_NAME=wpp_db

# Blockchain Configuration (Local Hardhat)
RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649

# Smart Contracts
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3

# API Keys
KAGGLE_USERNAME=kavanan12
KAGGLE_KEY=d3799b4b5d852fa6ed45d477ea72b372

# Dashboard
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true

# Logging
LOG_LEVEL=INFO
# ================================================
""")

print("\n✅ Ready! Follow the steps above to get started.\n")
