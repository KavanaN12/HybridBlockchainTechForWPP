"""Web3 client for blockchain interactions with DataAnchor contract."""
from web3 import Web3
import json
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Web3 connection
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

try:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if w3.is_connected():
        print("✓ Web3 connected to blockchain")
        # Get network info
        network_id = w3.net.version
        print(f"  Network ID: {network_id}")
    else:
        print("✗ Web3 connection failed - is hardhat node running?")
        w3 = None
except Exception as e:
    print(f"✗ Web3 initialization error: {e}")
    w3 = None

# Load DataAnchor contract ABI
def load_dataanchor_abi() -> Optional[list]:
    """
    Load DataAnchor contract ABI from artifacts.
    
    Returns:
        Contract ABI or None if not found
    """
    try:
        # Try to load from hardhat artifacts
        artifact_paths = [
            Path(__file__).parent / "artifacts" / "contracts" / "DataAnchor.sol" / "DataAnchor.json",
            Path(__file__).parent.parent / "blockchain" / "artifacts" / "contracts" / "DataAnchor.sol" / "DataAnchor.json",
        ]
        
        for artifact_path in artifact_paths:
            if artifact_path.exists():
                with open(artifact_path) as f:
                    artifact = json.load(f)
                    print(f"✓ Loaded DataAnchor ABI from {artifact_path}")
                    return artifact.get("abi", [])
        
        logger.warning("DataAnchor ABI file not found in artifacts")
        
        # Fallback: Use a minimal ABI based on DataAnchor contract
        fallback_abi = [
            {
                "type": "function",
                "name": "storeBatchHash",
                "inputs": [
                    {"name": "_hour", "type": "uint256"},
                    {"name": "_hash", "type": "bytes32"},
                    {"name": "_totalEnergy", "type": "uint256"}
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "getBatch",
                "inputs": [{"name": "_hour", "type": "uint256"}],
                "outputs": [
                    {"name": "hour", "type": "uint256"},
                    {"name": "batchHash", "type": "bytes32"},
                    {"name": "totalEnergy", "type": "uint256"},
                    {"name": "timestamp", "type": "uint256"}
                ],
                "stateMutability": "view"
            },
            {
                "type": "function",
                "name": "verifyIntegrity",
                "inputs": [
                    {"name": "_hour", "type": "uint256"},
                    {"name": "_hash", "type": "bytes32"}
                ],
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view"
            },
            {
                "type": "function",
                "name": "batchCount",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view"
            }
        ]
        
        print("⚠ Using fallback ABI for DataAnchor")
        return fallback_abi
        
    except Exception as e:
        logger.error(f"Error loading ABI: {e}")
        return None


def get_dataanchor_contract():
    """
    Get DataAnchor contract instance.
    
    Returns:
        Web3 contract instance or None
    """
    if w3 is None or not CONTRACT_ADDRESS:
        logger.error("Web3 not connected or CONTRACT_ADDRESS not set in .env")
        return None
        
    try:
        abi = load_dataanchor_abi()
        if abi is None:
            return None
        
        # Validate contract address
        if not w3.is_address(CONTRACT_ADDRESS):
            logger.error(f"Invalid contract address: {CONTRACT_ADDRESS}")
            return None
            
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        print(f"✓ DataAnchor contract loaded at {CONTRACT_ADDRESS}")
        return contract
        
    except Exception as e:
        logger.error(f"Error getting contract: {e}")
        return None


def store_batch_hash(hour: int, data_hash: str, total_energy: int = 0) -> Optional[str]:
    """
    Store batch hash on DataAnchor contract.
    
    Args:
        hour: Hour identifier
        data_hash: Hash of bid data
        total_energy: Total energy in batch (optional)
        
    Returns:
        Transaction hash or None if failed
    """
    if w3 is None or not PRIVATE_KEY:
        logger.error("Web3 or PRIVATE_KEY not configured")
        return None
        
    try:
        contract = get_dataanchor_contract()
        if contract is None:
            return None
        
        account = w3.eth.account.from_key(PRIVATE_KEY)
        
        # Convert hash to bytes32 if needed
        if isinstance(data_hash, str):
            if data_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(data_hash[2:])
            else:
                hash_bytes = bytes.fromhex(data_hash)
        else:
            hash_bytes = data_hash
        
        # Ensure it's 32 bytes
        if len(hash_bytes) != 32:
            logger.error(f"Hash must be 32 bytes, got {len(hash_bytes)}")
            return None
        
        # Build transaction
        tx = contract.functions.storeBatchHash(
            hour,
            hash_bytes,
            total_energy
        ).build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        logger.info(f"✓ Batch hash stored on blockchain")
        logger.info(f"  TX Hash: {tx_hash.hex()}")
        logger.info(f"  Gas Used: {receipt['gasUsed']}")
        
        return tx_hash.hex()
        
    except Exception as e:
        logger.error(f"✗ Error storing batch hash: {e}")
        return None


def verify_batch_on_chain(hour: int, data_hash: str) -> Optional[bool]:
    """
    Verify batch hash on blockchain.
    
    Args:
        hour: Hour identifier
        data_hash: Hash to verify
        
    Returns:
        True if hash matches, False if not, None if error
    """
    if w3 is None:
        logger.error("Web3 not connected")
        return None
        
    try:
        contract = get_dataanchor_contract()
        if contract is None:
            return None
        
        # Convert hash to bytes32
        if isinstance(data_hash, str):
            if data_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(data_hash[2:])
            else:
                hash_bytes = bytes.fromhex(data_hash)
        else:
            hash_bytes = data_hash
        
        if len(hash_bytes) != 32:
            logger.error(f"Hash must be 32 bytes, got {len(hash_bytes)}")
            return False
        
        result = contract.functions.verifyIntegrity(hour, hash_bytes).call()
        logger.info(f"✓ Batch verification result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"✗ Error verifying batch: {e}")
        return None


def get_batch_from_chain(hour: int) -> Optional[Dict]:
    """
    Retrieve batch data from blockchain.
    
    Args:
        hour: Hour identifier
        
    Returns:
        Batch data or None
    """
    if w3 is None:
        logger.error("Web3 not connected")
        return None
        
    try:
        contract = get_dataanchor_contract()
        if contract is None:
            return None
        
        batch = contract.functions.getBatch(hour).call()
        
        # BatchRecord structure: (bytes32 batchHash, uint256 totalEnergy, uint256 timestamp)
        # batch is a tuple: batch[0] = hash (bytes32), batch[1] = energy (uint256), batch[2] = timestamp (uint256)
        batch_hash = batch[0]
        
        # Convert bytes32 to hex string (consistent format without 0x prefix)
        if isinstance(batch_hash, bytes):
            hash_str = batch_hash.hex()
        else:
            hash_str = str(batch_hash)
        
        # Remove 0x prefix if present
        if isinstance(hash_str, str) and hash_str.startswith("0x"):
            hash_str = hash_str[2:]
        
        return {
            "hour": hour,
            "hash": hash_str,
            "totalEnergy": batch[1],
            "timestamp": batch[2]
        }
        
    except Exception as e:
        logger.error(f"✗ Error fetching batch: {e}")
        return None


def get_batch_count() -> Optional[int]:
    """Get total number of stored batches."""
    if w3 is None:
        logger.error("Web3 not connected")
        return None
        
    try:
        contract = get_dataanchor_contract()
        if contract is None:
            return None
        
        count = contract.functions.batchCount().call()
        return count
        
    except Exception as e:
        logger.error(f"✗ Error getting batch count: {e}")
        return None


def store_settlement_on_chain(auction_id: int, winner: str, energy: float, price: float, data_hash: str) -> Optional[str]:
    """
    Store a settlement on the blockchain via DataAnchor contract.
    
    Args:
        auction_id: Auction identifier
        winner: Winner address
        energy: Energy amount in Wh
        price: Price per Wh
        data_hash: SHA-256 hash of settlement data
        
    Returns:
        Transaction hash or None if failed
    """
    try:
        # Use auction_id as hour and store the hash
        tx_hash = store_batch_hash(hour=auction_id, data_hash=data_hash, total_energy=int(energy))
        return tx_hash
    except Exception as e:
        logger.error(f"✗ Error storing settlement on chain: {e}")
        return None
