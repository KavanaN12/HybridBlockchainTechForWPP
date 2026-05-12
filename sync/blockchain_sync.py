"""Entry point for sync.

Synchronization between MongoDB and blockchain
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

class BlockchainSync:
    """Synchronize hourly hashes to blockchain."""
    
    def __init__(self, rpc_url="http://localhost:8545"):
        self.rpc_url = rpc_url
        self.sync_log = []
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["energy_data"]
            self.records_collection = self.db["records"]
            self._ensure_indexes()
            logger.info("MongoDB connection established successfully.")
        except (PyMongoError, ConnectionError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _ensure_indexes(self):
        """Ensure indexes for MongoDB collection."""
        self.records_collection.create_index("key", unique=True)
        self.records_collection.create_index("timestamp")
        logger.info("Indexes ensured for MongoDB collection 'records'")

    def sync_batch_to_blockchain(self, hour: str, batch_hash: str) -> dict:
        """Simulate sending batch hash to blockchain."""
        # In real implementation, this would use web3.py to call smart contract
        
        sync_record = {
            'hour': hour,
            'batch_hash': batch_hash,
            'tx_id': f"0x{'0'*62}{'1'*2}",  # Mock tx ID
            'status': 'confirmed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.sync_log.append(sync_record)
        logger.info(f"Synced {hour}: {batch_hash[:16]}... → {sync_record['tx_id']}")
        
        return sync_record
    
    def process_all_batches(self, hashes_df) -> list:
        """Process all hourly batches."""
        results = []
        for idx, row in hashes_df.iterrows():
            result = self.sync_batch_to_blockchain(row['hour'], row['batch_hash'])
            results.append(result)
        return results

    def transfer_data_to_off_chain(self, data: dict):
        """Transfer data to MongoDB for off-chain storage."""
        try:
            logger.debug(f"Attempting to transfer data to MongoDB: {data}")
            collection = self.mongo_client["energy_data"]["records"]
            result = collection.update_one(
                {"key": data["key"]},
                {"$set": data},
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"Data inserted into MongoDB with ID: {result.upserted_id}")
            else:
                logger.info(f"Data updated in MongoDB for key: {data['key']}")
            return result.upserted_id
        except PyMongoError as e:
            logger.error(f"Error transferring data to MongoDB: {e}")
            raise

    def transfer_data_to_on_chain(self, data: dict):
        """Transfer data to the blockchain for on-chain storage."""
        try:
            tx = self.data_anchor.functions.storeData(
                data["key"],
                data["value"]
            ).transact({'from': self.w3.eth.accounts[0]})

            receipt = self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info(f"Data transferred to blockchain. TX: {receipt.transactionHash.hex()}")
            return receipt.transactionHash
        except (AttributeError, ValueError, ConnectionError) as e:
            logger.error(f"Error transferring data to blockchain: {e}")
            raise

def run_sync():
    """Main execution."""
    print("=" * 60)
    print("WPP Digital Twin - Blockchain Sync Engine")
    print("=" * 60)
    
    hashes_file = "experiments/hourly_hashes.csv"
    if not Path(hashes_file).exists():
        print(f"\n❌ Hashes not found at {hashes_file}")
        return
    
    # Load hashes
    import pandas as pd
    hashes_df = pd.read_csv(hashes_file)
    
    # Sync to blockchain
    syncer = BlockchainSync()
    results = syncer.process_all_batches(hashes_df)
    
    # Save sync log
    output_file = "sync/sync_logs.json"
    Path(output_file).parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Synced {len(results)} batches to blockchain")
    print(f"✓ Logs saved to {output_file}")

if __name__ == "__main__":
    run_sync()
