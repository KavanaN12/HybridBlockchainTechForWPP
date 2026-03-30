# 🚀 Hybrid Blockchain + Digital Twin (WPP) — Final Implementation Plan

## 🎯 Goal

Transform current prototype into a **real hybrid system**:

* Off-chain → MongoDB (data + ML + bids)
* On-chain → Ethereum (proof + settlement)
* Dashboard → UI layer only (no heavy logic)

---

# 🧱 FINAL ARCHITECTURE

```
SCADA Data → MongoDB
            ↓
      Feature Engineering
            ↓
        ML Model
            ↓
     Predictions (MongoDB)
            ↓
     Bidding System (MongoDB)
            ↓
   Auction Settlement Engine
            ↓
   Hash → Blockchain (Ethereum)
            ↓
   Verification Layer
            ↓
       Dashboard (Streamlit)
```

---

# 📦 FOLDER STRUCTURE (CLEAN)

```
project/
│
├── dashboard/
│   └── app.py
│
├── forecasting/
│   └── models.py
│
├── blockchain/
│   ├── contracts/
│   │   └── EnergyTrading.sol
│   ├── scripts/
│   │   └── deploy.js
│   └── web3_client.py
│
├── database/
│   └── mongo_client.py
│
├── services/
│   ├── bidding_service.py
│   ├── settlement_service.py
│   └── hash_service.py
│
├── data/
│
└── experiments/
```

---

# 🟢 STEP 1 — FIX MONGODB (OFF-CHAIN STORAGE)

## 📍 Create: `database/mongo_client.py`

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["wpp_db"]

bids_collection = db["bids"]
scada_collection = db["scada"]
prediction_collection = db["predictions"]
settlement_collection = db["settlements"]
```

---

## 📍 STORE BIDS

### In `bidding_service.py`

```python
from database.mongo_client import bids_collection
from datetime import datetime

def store_bid(user, energy, price):
    bid = {
        "user": user,
        "energy": energy,
        "price_per_wh": price,
        "timestamp": datetime.utcnow()
    }
    bids_collection.insert_one(bid)
```

---

## 📍 FETCH BIDS

```python
def get_all_bids():
    return list(bids_collection.find({}, {"_id": 0}))
```

---

---

# 🔵 STEP 2 — REAL BLOCKCHAIN (ON-CHAIN)

---

## 📍 Smart Contract: `EnergyTrading.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EnergyTrading {

    struct Settlement {
        uint auctionId;
        address winner;
        uint energy;
        uint price;
        string dataHash;
    }

    Settlement[] public settlements;

    function storeSettlement(
        uint _auctionId,
        address _winner,
        uint _energy,
        uint _price,
        string memory _hash
    ) public {
        settlements.push(Settlement(
            _auctionId,
            _winner,
            _energy,
            _price,
            _hash
        ));
    }

    function getSettlement(uint index) public view returns (Settlement memory) {
        return settlements[index];
    }
}
```

---

## 📍 Deploy (Hardhat)

```bash
npx hardhat compile
npx hardhat node
npx hardhat run scripts/deploy.js --network localhost
```

---

---

# 🔗 STEP 3 — CONNECT PYTHON TO BLOCKCHAIN

---

## 📍 `blockchain/web3_client.py`

```python
from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

with open("blockchain/contracts/abi.json") as f:
    abi = json.load(f)

contract_address = "PASTE_DEPLOYED_ADDRESS"

contract = w3.eth.contract(address=contract_address, abi=abi)

account = w3.eth.accounts[0]
```

---

## 📍 STORE ON BLOCKCHAIN

```python
def store_settlement_on_chain(auction_id, winner, energy, price, data_hash):
    tx = contract.functions.storeSettlement(
        auction_id,
        winner,
        energy,
        int(energy),
        data_hash
    ).transact({"from": account})

    return tx.hex()
```

---

---

# 🧠 STEP 4 — HASHING (INTEGRITY LAYER)

---

## 📍 `services/hash_service.py`

```python
import hashlib
import json

def generate_hash(data):
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()
```

---

---

# ⚖️ STEP 5 — SETTLEMENT ENGINE

---

## 📍 `services/settlement_service.py`

```python
from database.mongo_client import bids_collection, settlement_collection
from services.hash_service import generate_hash
from blockchain.web3_client import store_settlement_on_chain

def settle_auction():

    bids = list(bids_collection.find())

    if not bids:
        return None

    winner = max(bids, key=lambda x: x["price_per_wh"])

    data_hash = generate_hash(bids)

    tx_hash = store_settlement_on_chain(
        auction_id=1,
        winner="0xABC123",
        energy=winner["energy"],
        price=winner["price_per_wh"],
        data_hash=data_hash
    )

    settlement = {
        "winner": winner,
        "hash": data_hash,
        "tx_hash": tx_hash
    }

    settlement_collection.insert_one(settlement)

    return settlement
```

---

---

# 🧪 STEP 6 — UPDATE DASHBOARD

---

## ❌ REMOVE:

* JSON storage
* fake blockchain
* static logs

---

## ✅ ADD:

### 📍 When placing bid:

```python
from services.bidding_service import store_bid

store_bid(user="consumer_1", energy=energy, price=price)
```

---

### 📍 When showing bids:

```python
from services.bidding_service import get_all_bids

bids = get_all_bids()
st.dataframe(bids)
```

---

### 📍 Settlement button:

```python
from services.settlement_service import settle_auction

if st.button("Run Settlement"):
    result = settle_auction()
    st.write(result)
```

---

---

# 🔍 STEP 7 — VERIFICATION (IMPORTANT)

---

## 📍 Compare:

* MongoDB data
* Blockchain hash

```python
if hash_from_db == hash_from_blockchain:
    st.success("Data integrity verified")
else:
    st.error("Tampering detected")
```

---

---

# 🧠 FINAL SYSTEM BEHAVIOR

---

## ✔ OFF-CHAIN (MongoDB)

* SCADA data
* ML predictions
* bids
* logs

---

## ✔ ON-CHAIN (Blockchain)

* settlement record
* hash of bids
* proof of integrity

---

## ✔ DASHBOARD

* UI only
* no heavy logic
* triggers services

---

---

# 💬 FINAL RESULT

---

## 🎯 YOU NOW HAVE:

✔ Real data storage
✔ Real blockchain transaction
✔ Real hybrid architecture
✔ Real verification system

---

## 🚀 THIS IS:

> 🔥 **Production-grade academic project**

---

# 🧠 FINAL NOTE

---

## If short on time:

👉 Implement ONLY:

1. MongoDB bids
2. Hash + store on blockchain
3. Settlement

---

That alone = **huge upgrade**

---
