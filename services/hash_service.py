"""Hash service for data integrity verification."""
import hashlib
import json
from typing import Any, Dict
from datetime import datetime


def serialize_for_hash(obj: Any) -> Any:
    """
    Convert non-JSON-serializable objects to JSON-compatible format.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-compatible object
    """
    if isinstance(obj, datetime):
        # Serialize datetime in ISO format
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_hash(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_hash(item) for item in obj]
    else:
        return obj


def generate_hash(data: Any) -> str:
    """
    Generate SHA-256 hash of data for integrity verification.
    
    Args:
        data: Dictionary or any JSON-serializable object
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    try:
        # Serialize datetime objects consistently
        serializable_data = serialize_for_hash(data)
        
        # Remove MongoDB _id fields for consistent hashing
        if isinstance(serializable_data, dict) and "_id" in serializable_data:
            serializable_data = {k: v for k, v in serializable_data.items() if k != "_id"}
        elif isinstance(serializable_data, list):
            serializable_data = [
                {k: v for k, v in item.items() if k != "_id"} if isinstance(item, dict) else item
                for item in serializable_data
            ]
        
        data_string = json.dumps(serializable_data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()
    except Exception as e:
        print(f"Error generating hash: {e}")
        return ""


def verify_hash_integrity(data: Any, hash_value: str) -> bool:
    """
    Verify if data matches the provided hash.
    
    Args:
        data: Dictionary or any JSON-serializable object
        hash_value: Hash to compare against
        
    Returns:
        True if hash matches, False otherwise
    """
    computed_hash = generate_hash(data)
    return computed_hash == hash_value
