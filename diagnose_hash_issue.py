#!/usr/bin/env python3
"""Diagnose hash verification issues."""

import sys
from pathlib import Path
import json

root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from services.settlement_service import get_settlement_history
from services.hash_service import generate_hash, serialize_for_hash
from blockchain.web3_client import get_batch_from_chain
from database.mongo_client import settlement_collection

print("="*70)
print("🔍 DIAGNOSING HASH VERIFICATION ISSUE")
print("="*70)

# Get latest settlement
settlements = get_settlement_history(limit=1)
if not settlements:
    print("❌ No settlements found")
    sys.exit(1)

s = settlements[0]
print("\n[SETTLEMENT DATA]")
print(f"Settlement ID: {s.get('_id')}")
print(f"Auction ID: {s.get('auction_id')}")
print(f"Stored Hash: {s.get('data_hash')}")
print(f"Winner: {s.get('winner', {}).get('user')}")
print(f"Total Bids Count: {s.get('all_bids_count')}")
print(f"Status: {s.get('status')}")

print("\n[SETTLEMENT STRUCTURE]")
print(f"Settlement keys: {list(s.keys())}")

# Check if bids are stored in settlement
all_bids = s.get('all_bids', [])
print(f"\nBids stored in settlement: {len(all_bids)}")

if all_bids:
    print(f"First bid: {all_bids[0]}")
    
    # Recompute hash from bids
    print("\n[HASH VERIFICATION]")
    serialized = serialize_for_hash(all_bids)
    print(f"Serialized bids type: {type(serialized)}")
    
    recomputed = generate_hash(all_bids)
    print(f"Recomputed Hash: {recomputed}")
    print(f"Stored Hash:     {s.get('data_hash')}")
    
    if recomputed == s.get("data_hash"):
        print("✅ Hashes MATCH - Settlement data is consistent")
    else:
        print("❌ Hashes DO NOT MATCH")
        print(f"\nDifference detected!")
        print(f"  Stored hash length:     {len(str(s.get('data_hash')))}")
        print(f"  Recomputed hash length: {len(recomputed)}")
else:
    print("⚠️  No bids found in settlement structure")
    print("This is the problem! Settlement needs to store which bids were included")

# Check blockchain
print("\n[BLOCKCHAIN DATA]")
auction_id = s.get('auction_id', 1)
blockchain_data = get_batch_from_chain(auction_id)

if blockchain_data:
    bc_hash = blockchain_data.get('hash')
    print(f"Blockchain Hash: {bc_hash}")
    print(f"Stored Hash:     {s.get('data_hash')}")
    
    if bc_hash == s.get('data_hash'):
        print("✅ MongoDB and Blockchain hashes MATCH")
    else:
        print("❌ MongoDB and Blockchain hashes DO NOT MATCH")
else:
    print("❌ Could not retrieve from blockchain")

print("\n[ROOT CAUSE ANALYSIS]")
print("""
The hash verification is failing because:

1. Settlement doesn't store which BIDS were included
   - When settlement is created, the hash is of the bids
   - But settlement record doesn't keep the bids
   
2. When verifying, we can't recompute the same hash
   - New bids may have been added
   - We can't access the original bid data

SOLUTION:
- Store the list of bids in the settlement record
- This way we can always verify the hash matches the original bids
""")
