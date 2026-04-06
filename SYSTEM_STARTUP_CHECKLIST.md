# 🚀 SYSTEM STARTUP CHECKLIST

## Before Starting
- [ ] Verify hardhat node is running in Terminal 1 (check for "Listening on" message)
- [ ] Verify DataAnchor contract is deployed (check .env for CONTRACT_ADDRESS)
- [ ] Verify .env has all real values configured
- [ ] Verify MongoDB is installed on system

---

## 5-MINUTE STARTUP PROCESS

### ✅ STEP 1: Start MongoDB (Terminal 2)
```powershell
# Option A: If MongoDB is installed
mongod --dbpath d:\WPPDigitalTwin\data\mongo

# Option B: If MongoDB is a Windows service
net start MongoDB
```
**Expected Output:** `waiting for connections on port 27017`

**Time:** ~5 seconds

---

### ✅ STEP 2: Launch Dashboard (Terminal 3)
```powershell
cd d:\WPPDigitalTwin
streamlit run dashboard/app.py
```

**Expected Output:**
```
  Welcome to Streamlit!
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

**Time:** ~10 seconds

---

### ✅ STEP 3: Open Browser
Go to: **http://localhost:8501**

**Expected UI:**
- WPP Digital Twin header
- Role selector dropdown (Consumer/Maintainer/Producer)
- Sidebar with authenticated status

**Time:** Instant

---

## TEST THE SYSTEM

### Consumer Role - Test Bid Placement
1. Select **Consumer** from role dropdown
2. Click **Energy Marketplace**
3. Enter energy amount: **50** (MW)
4. Enter price: **150** ($/MWh)
5. Click **Place Bid**
6. **✅ Expected:** Bid appears in table immediately

**Time:** ~2 seconds per bid

---

### Consumer Role - Test Settlement
1. Click **Settlement Tracker**
2. Click **Run Settlement** button
3. **✅ Expected:** 
   - Winner shows the bid with highest price
   - Hash shows SHA-256 of bid data
   - Timestamp shows current time

**Time:** <1 second

---

### Consumer Role - Test Blockchain Storage
1. Click **Store on Blockchain** button
2. **✅ Expected:**
   - Success message appears
   - Transaction hash shows
   - Latest settlement shows blockchain link

**Time:** 1-3 seconds

---

### Maintainer Role - Test Integrity Verification
1. Select **Maintainer** from role dropdown
2. Click **Integrity Check**
3. Click **Verify Latest Settlement Hash**
4. **✅ Expected:**
   - Loads both database and blockchain hash
   - Shows ✓ VALID if they match
   - Shows ✗ TAMPERING if they differ

**Time:** ~2 seconds

---

## TROUBLESHOOTING

### Problem: "Failed to connect to MongoDB"
**Solution:**
1. Check MongoDB is running: `tasklist | findstr mongod`
2. If not running, start it:
   ```powershell
   mongod --dbpath d:\WPPDigitalTwin\data\mongo
   ```
3. Refresh dashboard (F5)

---

### Problem: "Failed to connect to blockchain"
**Solution:**
1. Check hardhat node is running in Terminal 1
2. Verify RPC URL: http://127.0.0.1:8545
3. If needed, restart:
   ```powershell
   cd d:\WPPDigitalTwin\blockchain
   npx hardhat node
   ```
4. Refresh dashboard (F5)

---

### Problem: "Contract not found at address"
**Solution:**
1. Check .env CONTRACT_ADDRESS matches deployment:
   ```text
   CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
   ```
2. If address differs, re-deploy:
   ```powershell
   cd d:\WPPDigitalTwin\blockchain
   npx hardhat run scripts/deploy.js --network localhost
   ```
3. Update .env with new address
4. Restart dashboard

---

### Problem: "Streamlit not found"
**Solution:**
```powershell
cd d:\WPPDigitalTwin
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

## SYSTEM VERIFICATION

| Component | Status | Check Command |
|-----------|--------|---------------|
| Hardhat Node | 🟢 Running | Terminal 1 shows "Listening on" |
| MongoDB | 🟢 Running | Terminal 2 shows "waiting for connections" |
| Dashboard | 🟢 Running | http://localhost:8501 loads |
| Contract | 🟢 Deployed | .env shows CONTRACT_ADDRESS |

---

## KEY INFORMATION

**Dashboard URL:** http://localhost:8501

**Hardhat Node URL:** http://127.0.0.1:8545

**MongoDB Connection:** mongodb://localhost:27017/

**Database Name:** wpp_db

**Collections:**
- `bids` - All user bids
- `settlements` - Auction results
- `scada` - Wind turbine data
- `predictions` - ML predictions

**Contract Address:** 0x5FbDB2315678afecb367f032d93F642f64180aa3

**Deployer Account:** 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

---

## SAMPLE DATA FLOW

```
1. Consumer places bid
   ↓ [stored in MongoDB via bidding_service]
   
2. Consumer runs settlement
   ↓ [winner selected, hash generated via settlement_service]
   
3. Consumer stores on blockchain
   ↓ [calls DataAnchor contract, records batch]
   
4. Maintainer verifies integrity
   ↓ [compares MongoDB hash with blockchain hash]
   
5. System shows ✓ VALID
   ↓ [Data integrity confirmed]
```

---

## QUICK COMMANDS

```powershell
# Start everything
Terminal 1: cd d:\WPPDigitalTwin\blockchain && npx hardhat node
Terminal 2: mongod --dbpath d:\WPPDigitalTwin\data\mongo
Terminal 3: cd d:\WPPDigitalTwin && streamlit run dashboard/app.py

# Stop everything
# Press Ctrl+C in each terminal

# Restart contract deployment
cd d:\WPPDigitalTwin\blockchain
npx hardhat run scripts/deploy.js --network localhost
```

---

## SUCCESS INDICATORS ✅

- [ ] Dashboard loads without errors
- [ ] Role dropdown works (Consumer/Maintainer/Producer)
- [ ] Can place bids in Consumer → Energy Marketplace
- [ ] Can run settlement in Consumer → Settlement Tracker
- [ ] Can store on blockchain
- [ ] Can verify hash matches in Maintainer → Integrity Check
- [ ] All timestamps update correctly
- [ ] No error messages in terminal

---

## NEXT AFTER STARTUP ⚡

1. **Explore the Dashboard**
   - Try each role (Consumer, Maintainer, Producer)
   - Click each section to see what data appears

2. **Place Test Bids**
   - Use Consumer role
   - Place multiple bids with different prices
   - See which becomes the winner

3. **Test Settlement Flow**
   - Run settlement
   - Store on blockchain
   - Check transaction hash

4. **Verify Data**
   - Use Maintainer role
   - Verify integrity of settlement
   - Check blockchain verification

5. **Review Logs**
   - Check MongoDB logs in Terminal 2
   - Check hardhat node logs in Terminal 1
   - Check dashboard logs in Terminal 3

---

## 🎉 You're All Set!

Your production-ready WPP Digital Twin system is now up and running with real blockchain integration!

**Start Terminal 2 and Terminal 3 now!**
