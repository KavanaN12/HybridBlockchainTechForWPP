"""Settlement service for auction settlement and blockchain integration."""
from datetime import datetime
from typing import Optional, Dict
from database.mongo_client import bids_collection, settlement_collection
from services.hash_service import generate_hash
import logging

logger = logging.getLogger(__name__)


def settle_auction(auction_id: int = 1) -> Optional[Dict]:
    """
    Settle an auction by selecting winner, generating hash, and storing settlement.
    
    Args:
        auction_id: Auction identifier
        
    Returns:
        Settlement record or None if failed
    """
    if bids_collection is None or settlement_collection is None:
        logger.error("MongoDB connection not available")
        return None
        
    try:
        # Get all bids
        bids = list(bids_collection.find({}, {"_id": 0}))
        
        if not bids:
            logger.warning("No bids found for settlement")
            return None
        
        # Find winner (highest price)
        winner = max(bids, key=lambda x: x.get("price_per_wh", 0))
        
        # Generate hash for data integrity
        data_hash = generate_hash(bids)
        
        # Create settlement record
        settlement = {
            "auction_id": auction_id,
            "winner": winner,
            "all_bids": bids,  # ✅ STORE THE BIDS FOR VERIFICATION
            "all_bids_count": len(bids),
            "data_hash": data_hash,
            "tx_hash": None,  # Will be updated when stored on blockchain
            "timestamp": datetime.utcnow(),
            "status": "pending_blockchain"
        }
        
        # Store in MongoDB
        result = settlement_collection.insert_one(settlement)
        settlement["_id"] = str(result.inserted_id)
        
        logger.info(f"✓ Settlement created: {settlement['_id']}")
        return settlement
        
    except Exception as e:
        logger.error(f"✗ Error settling auction: {e}")
        return None


def update_settlement_with_blockchain_tx(settlement_id: str, tx_hash: str) -> bool:
    """
    Update settlement record with blockchain transaction hash.
    
    Args:
        settlement_id: Settlement MongoDB ID
        tx_hash: Blockchain transaction hash
        
    Returns:
        True if successful
    """
    if settlement_collection is None:
        logger.error("MongoDB connection not available")
        return False
        
    try:
        from bson.objectid import ObjectId
        
        result = settlement_collection.update_one(
            {"_id": ObjectId(settlement_id)},
            {
                "$set": {
                    "tx_hash": tx_hash,
                    "status": "confirmed_blockchain",
                    "confirmation_time": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"✓ Settlement updated with TX: {tx_hash}")
            return True
        else:
            logger.warning(f"Settlement {settlement_id} not found")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error updating settlement: {e}")
        return False


def get_settlement_history(limit: int = 10) -> list:
    """
    Get recent settlement history.
    
    Args:
        limit: Number of recent settlements to fetch
        
    Returns:
        List of settlement records
    """
    if settlement_collection is None:
        logger.error("MongoDB connection not available")
        return []
        
    try:
        settlements = list(
            settlement_collection.find()
            .sort("_id", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for s in settlements:
            s["_id"] = str(s["_id"])
            
        return settlements
        
    except Exception as e:
        logger.error(f"✗ Error fetching settlement history: {e}")
        return []
