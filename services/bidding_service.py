"""Bidding service for managing energy bids."""
from datetime import datetime
from typing import List, Dict, Optional
from database.mongo_client import bids_collection


def store_bid(user: str, energy: float, price: float) -> Optional[str]:
    """
    Store a bid in MongoDB.
    
    Args:
        user: User identifier
        energy: Energy amount (Wh)
        price: Price per Wh
        
    Returns:
        Inserted document ID or None if failed
    """
    if bids_collection is None:
        print("Error: MongoDB connection not available")
        return None
        
    bid = {
        "user": user,
        "energy": energy,
        "price_per_wh": price,
        "timestamp": datetime.utcnow()
    }
    
    try:
        result = bids_collection.insert_one(bid)
        print(f"✓ Bid stored: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"✗ Error storing bid: {e}")
        return None


def get_all_bids() -> List[Dict]:
    """
    Retrieve all bids from MongoDB.
    
    Returns:
        List of bid dictionaries
    """
    if bids_collection is None:
        print("Error: MongoDB connection not available")
        return []
        
    try:
        bids = list(bids_collection.find({}, {"_id": 0}))
        return bids
    except Exception as e:
        print(f"✗ Error fetching bids: {e}")
        return []


def get_winning_bid() -> Optional[Dict]:
    """
    Get the winning bid based on:
    1. Highest price
    2. Highest energy (tie-breaker)
    """

    bids = get_all_bids()
    if not bids:
        return None

    # Clean + validate bids
    valid_bids = [
        b for b in bids
        if isinstance(b.get("price_per_wh"), (int, float)) and
           isinstance(b.get("energy"), (int, float))
    ]

    if not valid_bids:
        return None

    # Winner logic
    winner = max(
        valid_bids,
        key=lambda x: (x["price_per_wh"], x["energy"])
    )

    return winner


def clear_bids() -> bool:
    """
    Clear all bids from the collection (for auction reset).
    
    Returns:
        True if successful
    """
    if bids_collection is None:
        print("Error: MongoDB connection not available")
        return False
        
    try:
        result = bids_collection.delete_many({})
        print(f"✓ Cleared {result.deleted_count} bids")
        return True
    except Exception as e:
        print(f"✗ Error clearing bids: {e}")
        return False
