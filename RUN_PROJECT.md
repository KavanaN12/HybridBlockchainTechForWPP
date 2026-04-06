# RUN_PROJECT.md

## 🚀 WPP Digital Twin - Complete Start-to-Finish Guide

This document provides **step-by-step instructions** to run the complete WPP Digital Twin system from scratch after closing all terminals.

**System Architecture:**
- 🔗 **Blockchain:** Hardhat Local Node (Ethereum)
- 📦 **Database:** MongoDB (Local)
- 🎨 **Frontend:** Streamlit Dashboard
- ⚡ **Backend:** Python Services (Bidding, Settlement, Hashing)

---

## ⏱️ Total Setup Time: ~5 minutes

---

## 📋 Prerequisites

Before starting, ensure:
- ✅ Python 3.9+ installed
- ✅ Node.js 16+ installed
- ✅ MongoDB installed on your system
- ✅ Virtual environment at `d:\WPPDigitalTwin\.venv`
- ✅ All dependencies from `requirements.txt` installed

---

## 🔄 Complete Startup Process (4 Easy Steps)

### **STEP 1: Activate Python Virtual Environment**

**Terminal 1 - Execute this:**

```powershell
cd d:\WPPDigitalTwin
& .\.venv\Scripts\Activate.ps1
```

**Expected Output:**
```
(venv) D:\WPPDigitalTwin>
```

✅ You should see `(venv)` in the prompt

---

### **STEP 2: Start Hardhat Blockchain Node**

**Terminal 1 - Execute this:**

```powershell
cd d:\WPPDigitalTwin\blockchain
npx hardhat node
```

**Expected Output:**
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
...
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

✅ Keep this terminal **ALWAYS OPEN** - it's the blockchain node!
✅ You should see all 20 test accounts with 10,000 ETH each

---

### **STEP 3: Start MongoDB Database**

**Terminal 2 - Open new PowerShell terminal and execute:**

```powershell
mongosh  
no need of next line
mongod --dbpath d:\WPPDigitalTwin\data\mongo
```

**Expected Output:**
```
waiting for connections on port 27017
```

✅ Keep this terminal open - database is running

---

### **STEP 4: Launch Streamlit Dashboard**

**Terminal 3 - Open new PowerShell terminal and execute:**

```powershell
cd d:\WPPDigitalTwin
& .\.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8503
```

✅ Both services connected:
```
✓ MongoDB connected successfully
✓ Web3 connected to blockchain
```

---

## 🌐 Access Your Dashboard

**Open your browser and go to:**

```
http://localhost:8503
```

You should see:
- ⚡ **WPP Digital Twin Dashboard** title
- 🎭 **Select your role** dropdown with 3 options:
  - **Consumer** - Place bids, run settlements, store on blockchain
  - **Maintainer** - Verify data integrity, check blockchain
  - **Producer** - View SCADA data, forecasting, wind analysis

---

## 🧪 Test the System (5 Minutes)

### **Test 1: Consumer - Place Bids**

1. Select **Consumer** role
2. Go to **Energy Marketplace** tab
3. Enter:
   - Energy: `50` (Wh)
   - Price: `150` ($/Wh)
4. Click **Place Bid**
5. **Expected:** Bid appears in "Your Bids" table immediately

**Time:** ~5 seconds

---

### **Test 2: Consumer - Run Settlement**

1. Stay in **Consumer** role
2. Go to **Settlement Tracker** tab
3. Click **Run Settlement** button
4. **Expected:** 
   - Winner selected (highest price)
   - Hash generated (SHA-256 of bid data)
   - Settlement record created

**Time:** <1 second

---

### **Test 3: Consumer - Store on Blockchain**

1. Still in **Settlement Tracker**
2. Click **Store on Blockchain** button
3. **Expected:**
   - ✅ Success message shown
   - Transaction hash displayed
   - Status changes to "confirmed_blockchain"

**Time:** 1-3 seconds (local blockchain is instant)

---

### **Test 4: Maintainer - Verify Hash Integrity**

1. Select **Maintainer** role
2. Go to **Integrity Check** tab
3. Click **Compare Latest Settlement Hash** button
4. **Expected:**
   ```
   MongoDB Hash:     8b883fcf10c6fc037b629f7cbf3b3949017572fd11a6f983979995228dbbd305
   Blockchain Hash:  8b883fcf10c6fc037b629f7cbf3b3949017572fd11a6f983979995228dbbd305
   ✅ HASHES MATCH - Data integrity confirmed!
   ```

**Time:** ~2 seconds

---

## 📊 System Status Verification

| Component | Status Check |
|-----------|--------------|
| **Hardhat Node** | Terminal 1 shows "Listening on 127.0.0.1:8545" |
| **MongoDB** | Terminal 2 shows "waiting for connections on port 27017" |
| **Dashboard** | Terminal 3 shows "Local URL: http://localhost:8503" |
| **Web3** | Dashboard shows "✓ Web3 connected to blockchain" |
| **MongoDB** | Dashboard shows "✓ MongoDB connected successfully" |

✅ **All 5 indicators green = System fully operational!**

---

## 🔧 Advanced Configuration

### **Contract Deployment (if needed)**

If you need to redeploy the DataAnchor contract:

```powershell
cd d:\WPPDigitalTwin\blockchain
npx hardhat run scripts/deploy.js --network localhost
```

This will:
- Update `.env` with new contract address
- Update `deployment_trading.json`
- Test all contract functions
- Display gas usage

**Note:** This resets the blockchain state on the local Hardhat node

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration with real contract address and private key |
| `blockchain/web3_client.py` | Blockchain interaction layer |
| `services/bidding_service.py` | Bid management (MongoDB) |
| `services/settlement_service.py` | Settlement logic (MongoDB + Blockchain) |
| `services/hash_service.py` | Hash generation and verification |
| `dashboard/app.py` | Streamlit user interface |
| `blockchain/DataAnchor.sol` | Smart contract for hash storage |

---

## ⚠️ Troubleshooting

### **Problem: "Failed to connect to blockchain"**

**Solution:**
- Check Terminal 1 (Hardhat node) is running and shows "Listening on 127.0.0.1:8545"
- Verify RPC URL in `.env`: `http://127.0.0.1:8545`
- Restart Hardhat node if needed

---

### **Problem: "MongoDB connection error"**

**Solution:**
- Check Terminal 2 (MongoDB) is running
- Verify MongoDB path: `d:\WPPDigitalTwin\data\mongo`
- If data folder doesn't exist, create it: `mkdir d:\WPPDigitalTwin\data\mongo`
- Restart MongoDB in Terminal 2

---

### **Problem: "Dashboard not loading at localhost:8503"**

**Solution:**
- Check Terminal 3 (Streamlit) shows "Local URL: http://localhost:8503"
- Refresh browser or clear cache
- Check if port 8503 is in use: `netstat -ano | findstr :8503`
- Try different port: `streamlit run dashboard/app.py --server.port 8504`

---

### **Problem: "Hash verification failed"**

**Solution:**
- Ensure settlement was created BEFORE storing on blockchain
- Order of operations: Place Bid → Run Settlement → Store on Blockchain
- Click "Compare Latest Settlement Hash" immediately after storing

---

## 🎯 Daily Workflow (After Initial Setup)

Once everything is set up, this is the minimal daily startup:

**Terminal 1:**
```powershell
cd d:\WPPDigitalTwin\blockchain
npx hardhat node
```

**Terminal 2:**
```powershell
mongod --dbpath d:\WPPDigitalTwin\data\mongo
```

**Terminal 3:**
```powershell
cd d:\WPPDigitalTwin
& .\.venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

Then open browser to: `http://localhost:8503`

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD                     │
│  (Consumer / Maintainer / Producer Role Selector)   │
└────────────────┬────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
     ▼           ▼           ▼
┌─────────┐  ┌────────┐  ┌──────────┐
│ Bidding │  │Settlem.│  │   Hash   │
│Service  │  │Service │  │ Service  │
└────┬────┘  └───┬────┘  └─────┬────┘
     │           │             │
     └───────────┼─────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ┌────────┐      ┌──────────────┐
    │MongoDB │      │  Blockchain  │
    │(Bids)  │      │DataAnchor.sol│
    └────────┘      └──────────────┘
```

---

## ✅ System Ready!

Your production-grade hybrid blockchain + MongoDB system is now **fully operational** and ready for use!

**Key Features:**
- ✅ Real Ethereum-like blockchain (Hardhat local)
- ✅ MongoDB integration for off-chain data
- ✅ Automatic hash verification
- ✅ Blockchain data anchoring
- ✅ Tamper detection
- ✅ Real-time dashboard
- ✅ Three user roles (Consumer/Maintainer/Producer)

**Next Steps:**
1. Place test bids
2. Run settlements
3. Store on blockchain
4. Verify integrity
5. Deploy to production when ready!

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| **Activate venv** | `& .\.venv\Scripts\Activate.ps1` |
| **Start blockchain** | `npx hardhat node` (in `blockchain/` folder) |
| **Start MongoDB** | `mongod --dbpath d:\WPPDigitalTwin\data\mongo` |
| **Run dashboard** | `streamlit run dashboard/app.py` |
| **Deploy contract** | `npx hardhat run scripts/deploy.js --network localhost` |
| **Test hashing** | `python test_hash_verification.py` |
| **Access dashboard** | `http://localhost:8503` |
| **Contract address** | From `.env` file or deployment output |

---

**Good luck! Your system is ready to revolutionize wind power trading! 🌬️⚡**

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

