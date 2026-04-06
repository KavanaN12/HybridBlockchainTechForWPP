#!/usr/bin/env python3
"""
Test script to verify hash verification works correctly.
Run this to test the entire flow:
  1. Place bids
  2. Run settlement
  3. Store on blockchain
  4. Verify hash matches
"""

import sys
from pathlib import Path

# Add workspace to path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from services.bidding_service import store_bid, get_all_bids, clear_bids
from services.settlement_service import settle_auction, get_settlement_history
from services.hash_service import generate_hash, verify_hash_integrity
from blockchain.web3_client import store_batch_hash, get_batch_from_chain


def test_hash_verification():
    """Test the complete hash verification flow."""
    
    print("\n" + "="*70)
    print("🧪 HASH VERIFICATION TEST")
    print("="*70)
    
    # Step 1: Clear existing bids
    print("\n[1] Clearing existing bids...")
    clear_bids()
    print("✓ Bids cleared")
    
    # Step 2: Place some test bids
    print("\n[2] Placing test bids...")
    bid_ids = []
    for i in range(3):
        user = f"User{i+1}"
        energy = 50 + (i * 10)
        price = 150 + (i * 5)
        bid_id = store_bid(user, energy, price)
        bid_ids.append(bid_id)
        print(f"   ✓ Bid placed: {user} - {energy}Wh @ ${price}/Wh")
    
    # Step 3: Get all bids and generate hash
    print("\n[3] Retrieving bids and generating hash...")
    bids = get_all_bids()
    print(f"   ✓ Retrieved {len(bids)} bids from MongoDB")
    
    mongo_hash = generate_hash(bids)
    print(f"   ✓ MongoDB Hash (Bid Data):")
    print(f"      {mongo_hash}")
    
    # Step 4: Verify hash of same data
    print("\n[4] Verifying hash integrity...")
    is_valid = verify_hash_integrity(bids, mongo_hash)
    if is_valid:
        print("   ✅ PASS: Hash verification successful (data integrity confirmed)")
    else:
        print("   ❌ FAIL: Hash mismatch (data may be tampered)")
        return False
    
    # Step 5: Settlement
    print("\n[5] Running settlement...")
    settlement = settle_auction(auction_id=1)
    if settlement:
        print(f"   ✓ Settlement created")
        print(f"   ✓ Winner: {settlement['winner']['user']}")
        print(f"   ✓ Settlement Hash (from settlement):")
        print(f"      {settlement['data_hash']}")
    else:
        print("   ❌ Settlement failed")
        return False
    
    # Step 6: Store on blockchain
    print("\n[6] Storing settlement hash on blockchain...")
    tx_hash = store_batch_hash(
        hour=1,
        data_hash=settlement['data_hash'],
        total_energy=int(settlement['winner']['energy'])
    )
    
    if tx_hash:
        print(f"   ✓ Stored on blockchain")
        print(f"   ✓ Transaction Hash: {tx_hash}")
    else:
        print("   ❌ Blockchain storage failed")
        return False
    
    # Step 7: Retrieve from blockchain and compare
    print("\n[7] Retrieving hash from blockchain and comparing...")
    blockchain_data = get_batch_from_chain(hour=1)
    
    if blockchain_data:
        blockchain_hash = blockchain_data['hash']
        print(f"   ✓ Blockchain Hash:")
        print(f"      {blockchain_hash}")
        
        print(f"\n[COMPARISON]")
        print(f"   MongoDB Hash:     {settlement['data_hash']}")
        print(f"   Blockchain Hash:  {blockchain_hash}")
        
        if settlement['data_hash'] == blockchain_hash:
            print(f"\n   ✅ HASHES MATCH - Perfect integrity!")
            return True
        else:
            print(f"\n   ❌ HASHES DO NOT MATCH")
            print(f"      MongoDB length:     {len(settlement['data_hash'])}")
            print(f"      Blockchain length:  {len(blockchain_hash)}")
            return False
    else:
        print("   ❌ Could not retrieve from blockchain")
        return False


if __name__ == "__main__":
    try:
        success = test_hash_verification()
        
        if success:
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED - Hash verification working correctly!")
            print("="*70 + "\n")
            sys.exit(0)
        else:
            print("\n" + "="*70)
            print("❌ TESTS FAILED - Issues detected")
            print("="*70 + "\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
