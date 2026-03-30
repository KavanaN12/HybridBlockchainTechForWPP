# System Architecture

## Overview

```
Real-World Wind Data
        ↓
   ┌────────────────────────────────┐
   │  PREPROCESSING LAYER            │
   │  • Kaggle SCADA Dataset         │
   │  • Data Cleaning (Pandas)       │
   │  • Feature Engineering          │
   │  • Outlier Detection            │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  DIGITAL TWIN LAYER            │
   │  • Physics-based Model (IEC)   │
   │  • Wind Speed → Power Output   │
   │  • Efficiency Gap Tracking     │
   │  • Twin Validation vs Real    │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  FORECASTING LAYER             │
   │  • Linear Regression           │
   │  • Random Forest               │
   │  • 1-hour ahead prediction    │
   │  • Model Evaluation (RMSE/MAE) │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  OFF-CHAIN STORAGE (MongoDB)   │
   │  • Raw SCADA (immutable)       │
   │  • Twin Results                │
   │  • Forecast Results            │
   │  • Time-Series Collections     │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  HASHING ENGINE                │
   │  • SHA-256 Hourly Batches      │
   │  • Deterministic JSON Hash     │
   │  • Batch Aggregation           │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  ON-CHAIN LAYER (Ethereum)     │
   │  • DataAnchor Smart Contract   │
   │  • Store Batch Hashes          │
   │  • Integrity Verification      │
   │  • Event Logging               │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  SYNC ENGINE                   │
   │  • MongoDB → Blockchain        │
   │  • Transaction Orchestration   │
   │  • Retry Logic & Audit Trail   │
   └────────────────────────────────┘
        ↓
   ┌────────────────────────────────┐
   │  DASHBOARD (Streamlit)         │
   │  • Real-time Visualization     │
   │  • Metrics & Results           │
   │  • Integrity Checks            │
   │  • Tamper Detection            │
   └────────────────────────────────┘
```

## Component Details

### 1. Preprocessing
- **Input**: Raw SCADA CSV (Kaggle)
- **Process**: Normalization, outlier detection, feature engineering
- **Output**: Clean CSV with 10K+ records
- **Tech**: Pandas, NumPy
- **File**: `preprocessing/data_cleaner.py`

### 2. Digital Twin
- **Input**: Wind speed data
- **Process**: Physics-based power curve (P = 0.5 × ρ × A × Cp × V³)
- **Output**: Theoretical power, efficiency gap
- **Validation Metric**: R² > 0.85, MAE < 5% rated power
- **Tech**: Custom Python implementation following IEC 61400
- **File**: `twin/wind_turbine.py`

### 3. Forecasting
- **Input**: [wind_speed, lag_power, rolling_avg_wind]
- **Models**: Linear Regression, Random Forest
- **Output**: 1-hour ahead power forecast
- **Metrics**: RMSE, MAE, MAPE
- **Tech**: Scikit-learn
- **File**: `forecasting/models.py`

### 4. Off-Chain Storage
- **Database**: MongoDB (local or Atlas)
- **Collections**:
  - `raw_scada`: Original SCADA data (immutable)
  - `twin_results`: Twin calculations
  - `forecast_results`: ML predictions
  - `blockchain_anchor`: Hash references
- **Tech**: MongoDB, Motor (async driver)

### 5. Hash Engine
- **Method**: SHA-256
- **Granularity**: Hourly batches
- **Input**: All readings for 1 hour
- **Output**: Single deterministic hash per hour
- **Verification**: Replay-proof (same data = same hash)
- **Tech**: hashlib, JSON serialization

### 6. Blockchain Layer
- **Network**: Ethereum (Sepolia testnet, or local Ganache)
- **Contract**: DataAnchor.sol
- **Functions**:
  - `storeBatchHash(hour, hash, totalEnergy)` — records hourly proof
  - `verifyIntegrity(hour, hash)` — boolean verification
- **Events**: `BatchStored` emitted for off-chain indexing
- **Tech**: Solidity 0.8.20, Hardhat, web3.py
- **File**: `blockchain/contracts/DataAnchor.sol`

### 7. Synchronization
- **Trigger**: Every hour after preprocessing
- **Flow**: Aggregate readings → Compute hash → Call smart contract → Store tx ID in MongoDB
- **Retry Logic**: Exponential backoff if failed
- **Audit Trail**: JSON log of all syncs
- **Tech**: web3.py, async handlers
- **File**: `sync/blockchain_sync.py`

### 8. Dashboard
- **Tool**: Streamlit
- **Tabs**:
  - **Raw Data**: Time-series plots, SCADA metrics
  - **Digital Twin**: Validation results, overlay plot
  - **Forecasting**: Model comparison, accuracy tables
  - **Blockchain Anchors**: Hash history, batch stats
  - **Integrity Check**: Tamper detection button
- **Tech**: Streamlit, Plotly
- **File**: `dashboard/app.py`

## Hybrid Architecture Design

### On-Chain Storage
- Energy trading data and critical hashes are stored on the blockchain for immutability and transparency.
- Smart contracts ensure secure and automated transactions.

### Off-Chain Storage
- MongoDB is used for storing detailed energy data and logs.
- Optional archival to S3 for long-term storage and cost optimization.

### Synchronization
- A hashing layer ensures data integrity between on-chain and off-chain storage.
- BlockchainSync class handles data transfer and verification.

## Data Flow

```
1. External SCADA Data (CSV)
     ↓
2. Preprocessor normalizes timestamps, removes outliers
     ↓
3. Twin calculates theoretical power curve
     ↓
4. Forecaster trains on [wind_speed, lag_power]
     ↓
5. All results stored in MongoDB (off-chain)
     ↓
6. Hourly: Aggregate + SHA-256 hash
     ↓
7. Hash sent to smart contract via web3.py
     ↓
8. Blockchain confirms receipt (low tx cost: ~150K gas/hour)
     ↓
9. Dashboard reads all layers and displays live
     ↓
10. User can verify integrity: blockchain hash matches MongoDB data
```

## Why Hybrid Architecture?

### Problem: Full On-Chain
- ❌ 1,440+ transactions/day (1-min readings)
- ❌ ~$2000+ USD/month gas cost (Ethereum)
- ❌ Latency unsuitable for real-time control

### Solution: Hybrid (Our Approach)
- ✅ 24 transactions/day (1 hash/hour)
- ✅ ~$10 USD/month gas cost (99% reduction)
- ✅ Instant off-chain queries, immutable blockchain proof

### Trust Model
- **Off-Chain Data**: Trusted via centralized MongoDB (research only)
- **On-Chain Proof**: Blockchain-verified hourly summaries
- **Integrity Guarantee**: Cryptographic hash prevents tampering
- **Auditability**: Full history on blockchain

## Scalability Metrics

| Metric | Full On-Chain | Hybrid (Ours) | Improvement |
|--------|---------------|---------------|-------------|
| Transactions/day | 1,440 | 24 | **60x reduction** |
| Gas cost/day | 216M | 3.6M | **99% savings** |
| Latency (query) | 15+ sec | <100ms | **Real-time** |
| Throughput | Limited by block time | Unlimited | **Unbounded** |

## Security Considerations

✅ **Hash Collisions**: SHA-256 is cryptographically secure  
✅ **Transaction Integrity**: Smart contract immutable once deployed  
✅ **Access Control**: MongoDB credentials in .env (non-production)  
✅ **Replay Protection**: Timestamp + unique hour ID on each record  

⚠️ **Production Considerations**:
- Deploy to Polygon L2 (lower gas)
- Add Chainlink oracle for decentralized verification
- Use Hardware Security Module (HSM) for private keys
- Implement time-lock governance for contract upgrades

## Technology Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Database | MongoDB | Flexible schema, native time-series collections |
| Blockchain | Ethereum | Largest DeFi ecosystem, proven security |
| Language | Python | Data science friendly, web3.py bindings |
| Dashboard | Streamlit | Rapid iteration, interactive visualizations |
| Hashing | SHA-256 | Industry standard, deterministic |
| Testing | Pytest + Hardhat | Comprehensive coverage, CI/CD ready |

---

**Architecture Version**: 1.0  
**Last Updated**: March 2025  
**Status**: Research-Grade Prototype (Pre-Production)
