"""MongoDB client configuration for WPP Digital Twin."""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "wpp_db")

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Test connection
    client.admin.command('ping')
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"✗ MongoDB connection error: {e}")
    db = None

# Collections
bids_collection = db["bids"] if db is not None else None
scada_collection = db["scada"] if db is not None else None
prediction_collection = db["predictions"] if db is not None else None
settlement_collection = db["settlements"] if db is not None else None
