# MongoDB Schema Definitions

## Overview

MongoDB stores all off-chain data in 4 immutable collections. Time-series collections are optimized for high-frequency sensor data.

---

## Collection 1: `raw_scada`

**Type**: Time-Series Collection  
**Purpose**: Immutable raw wind turbine operational data  
**Insert Rate**: 10,000+ records/week

### Schema
```json
{
  "_id": ObjectId,
  "time": ISODate("2025-03-09T10:00:00Z"),          // Timestamp
  "turbine_id": "WT-001",                           // Turbine identifier
  "farm_id": "FARM-01",                             // Farm identifier
  "wind_speed_ms": 12.5,                            // Wind speed (m/s)
  "wind_direction_deg": 225,                        // Direction (0-360)
  "power_output_kw": 1850,                          // Active power (kW)
  "rotor_speed_rpm": 12.3,                          // Rotor RPM
  "pitch_angle_deg": 5,                             // Blade pitch (degrees)
  "temperature_celsius": -2.5,                      // Ambient temperature
  "air_density_kgm3": 1.225,                        // Air density at timestamp
  "nacelle_temperature_celsius": 15,                // Nacelle temp
  "gearbox_temperature_celsius": 48,                // Gearbox oil temp
  "status": "NORMAL"                                // Status: NORMAL, WARNING, ALARM
}
```

### Indexes
```javascript
db.raw_scada.createIndex({ "time": 1, "turbine_id": 1 })
db.raw_scada.createIndex({ "farm_id": 1 })
```

### Immutability Rule
```
No updates allowed post-insert.
Only inserts and reads permitted.
Retention: 100% (never delete for auditability).
```

---

## Collection 2: `twin_results`

**Type**: Time-Series Collection  
**Purpose**: Digital twin calculations and efficiency metrics  
**Frequency**: 1 record per turbine per hour

### Schema
```json
{
  "_id": ObjectId,
  "time": ISODate("2025-03-09T10:00:00Z"),
  "turbine_id": "WT-001",
  "wind_speed_ms": 12.5,
  "actual_power_kw": 1850,                           // From raw_scada
  "theoretical_power_kw": 1920,                      // Physics-based calculation
  "efficiency_gap_kw": -70,                          // actual - theoretical
  "efficiency_gap_pct": -3.6,                        // (actual - theoretical) / theoretical * 100
  "cp_coefficient": 0.42,                            // Power coefficient
  "turbine_state": "PARTIAL_LOAD",                  // OFF, CUT_IN, PARTIAL_LOAD, RATED, CUT_OUT
  "rotor_speed_rpm": 12.3,
  "model_version": "1.0",                            // Twin model version
  "mae_kw": 45.2,                                   // Mean absolute error (rolling window)
  "r_squared": 0.87                                  // R² score (rolling window)
}
```

### Indexes
```javascript
db.twin_results.createIndex({ "time": 1, "turbine_id": 1 })
db.twin_results.createIndex({ "turbine_state": 1 })
```

---

## Collection 3: `forecast_results`

**Type**: Time-Series Collection  
**Purpose**: ML-based power forecasting  
**Frequency**: Every hour for 1-24 hour horizons

### Schema
```json
{
  "_id": ObjectId,
  "forecast_time": ISODate("2025-03-09T10:00:00Z"),  // When forecast was made
  "horizon_hours": 1,                                // 1h, 4h, 24h ahead
  "turbine_id": "WT-001",
  "actual_power_kw": 1850,                          // Actual production at forecast_time
  "forecast_power_kw": 1890,                        // Predicted output
  "forecast_error_kw": -40,                         // actual - forecast
  "forecast_error_pct": -2.1,                       // Error as % of actual
  "model_used": "random_forest",                    // linear_regression, random_forest
  "features_used": {
    "wind_speed_ms": 12.5,
    "lag_power_kw": 1750,
    "rolling_avg_wind_ms": 11.8,
    "hour_of_day": 10
  },
  "confidence_interval_lower": 1650,                // 90% CI
  "confidence_interval_upper": 2130,
  "prediction_time_ms": 5.2                         // Inference latency
}
```

### Indexes
```javascript
db.forecast_results.createIndex({ "forecast_time": 1, "turbine_id": 1, "horizon_hours": 1 })
db.forecast_results.createIndex({ "model_used": 1 })
```

---

## Collection 4: `blockchain_anchor`

**Type**: Regular Collection (not time-series)  
**Purpose**: References to blockchain hashes and transaction IDs  
**Frequency**: 1 record per hour (all turbines aggregated)

### Schema
```json
{
  "_id": ObjectId,
  "hour": ISODate("2025-03-09T10:00:00Z"),           // Batch hour
  "batch_hash": "a7f3b2c8e5d9f1a6b4c7e2d5f8a3b6c9...", // SHA-256 hash
  "tx_id": "0x5c...",                               // Ethereum tx hash
  "contract_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
  "block_number": 19824561,
  "block_timestamp": ISODate("2025-03-09T10:15:33Z"),
  "confirmation_status": "CONFIRMED",               // PENDING, CONFIRMED, FAILED
  "record_count": 156,                              // Number of raw_scada records in batch
  "batch_records": [
    "WT-001", "WT-002", "WT-003_avg"                // Turbines included
  ],
  "total_energy_kwh": 2847.5,                        // Sum of power for hour
  "gas_used": 152834,                               // Gas consumed
  "transaction_fee_eth": 0.00324,                   // Fee paid
  "created_at": ISODate("2025-03-09T10:00:05Z"),
  "synced_at": ISODate("2025-03-09T10:01:15Z"),     // When sent to blockchain
  "verified_at": ISODate("2025-03-09T10:02:45Z"),   // When confirmation received
  "metadata": {
    "environment": "testnet",                       // testnet, mainnet
    "network": "sepolia",                           // ethereum, polygon, etc.
    "batch_version": 1
  }
}
```

### Indexes
```javascript
db.blockchain_anchor.createIndex({ "hour": -1 })
db.blockchain_anchor.createIndex({ "confirmation_status": 1 })
db.blockchain_anchor.createIndex({ "batch_hash": 1 })
```

---

## Query Examples

### Query 1: Get latest twin errors for turbine
```javascript
db.twin_results.find(
  { "turbine_id": "WT-001" }
).sort({ "time": -1 }).limit(24)
```

### Query 2: Find forecast predictions for next 24h
```javascript
db.forecast_results.find(
  { 
    "forecast_time": { $gte: ISODate("2025-03-09T10:00:00Z") },
    "horizon_hours": 24
  }
).sort({ "forecast_time": -1 })
```

### Query 3: Verify blockchain anchor
```javascript
db.blockchain_anchor.find(
  { "hour": ISODate("2025-03-09T10:00:00Z") }
)
```

### Query 4: Calculate daily energy production
```javascript
db.raw_scada.aggregate([
  { $match: { "time": { $gte: ISODate("2025-03-09T00:00:00Z"), $lt: ISODate("2025-03-10T00:00:00Z") } } },
  { $group: { 
      _id: "$turbine_id",
      daily_energy_kwh: { $sum: { $multiply: ["$power_output_kw", 1/60] } }
    }
  },
  { $sort: { "daily_energy_kwh": -1 } }
])
```

---

## Data Retention Policy

| Collection | Retention | Reason |
|-----------|-----------|--------|
| `raw_scada` | 100% | Auditability, immutable source of truth |
| `twin_results` | 100% | Validation metrics for research |
| `forecast_results` | 100% | Model accuracy tracking |
| `blockchain_anchor` | 100% | Blockchain sync verification |

**Backup Schedule**: Daily snapshots (automated via MongoDB Atlas)

---

## Access Patterns

### Read-Heavy
- Twin validation (compare actual vs theoretical)
- Forecast verification (check error metrics)
- Dashboard queries (latest hour data)

### Write-Heavy
- Raw SCADA ingestion (10K+/week)
- Forecasting batch update (hourly)

### Performance Tuning
- Time-series collections: Automatic columnar indexing
- Compound indexes on (time, turbine_id) for multi-turbine queries
- TTL indexes (optional) for transient data

---

## Initialization Script

```python
# Connect and create collections
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

client = MongoClient('mongodb://localhost:27017')
db = client['wind_twin_db']

# Create time-series collections
db.create_collection("raw_scada", timeseries={
    "timeField": "time",
    "metaField": "turbine_id",
    "granularity": "minutes"
})

db.create_collection("twin_results", timeseries={
    "timeField": "time",
    "metaField": "turbine_id",
    "granularity": "hours"
})

db.create_collection("forecast_results", timeseries={
    "timeField": "forecast_time",
    "metaField": "turbine_id",
    "granularity": "hours"
})

# Regular collection for blockchain anchors
db.create_collection("blockchain_anchor")

# Create indexes
db.raw_scada.create_index([("time", ASCENDING), ("turbine_id", ASCENDING)])
db.twin_results.create_index([("time", ASCENDING), ("turbine_id", ASCENDING)])
db.forecast_results.create_index([("forecast_time", ASCENDING)])
db.blockchain_anchor.create_index([("hour", DESCENDING)])

print("✓ All MongoDB collections created successfully")
```

---

**Schema Version**: 1.0  
**Last Updated**: March 2025  
**Compliance**: GDPR-aware (no PII stored)
