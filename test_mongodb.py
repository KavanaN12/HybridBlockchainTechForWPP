"""
MongoDB Connectivity Verification
"""
import sys
from pathlib import Path

def test_mongodb():
    """Test MongoDB connection."""
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure
        
        # Try default local connection
        mongo_uri = "mongodb://127.0.0.1:27017/wpp_digital_twin"
        
        print("=" * 60)
        print("MongoDB Connectivity Test")
        print("=" * 60)
        print(f"\n⏳ Testing connection to: {mongo_uri}")
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Trigger connection
        client.server_info()
        
        print("✅ MongoDB connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"\n📊 Available databases: {databases}")
        
        # Create test collection
        db = client['wpp_digital_twin']
        collection = db['test_collection']
        test_doc = {
            'test': 'document',
            'status': 'verified',
            'timestamp': str(Path('data/processed/scada_preprocessed.csv').resolve())
        }
        result = collection.insert_one(test_doc)
        print(f"\n✓ Test document inserted: {result.inserted_id}")
        
        # Clean up
        collection.delete_one({'_id': result.inserted_id})
        print("✓ Test document cleaned up")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("✅ MongoDB Ready for Production!")
        print("=" * 60)
        
        return True
        
    except ConnectionFailure:
        print("\n❌ MongoDB Connection Failed")
        print("\n🐳 To start MongoDB with Docker:")
        print("   cd docker")
        print("   docker-compose up -d")
        print("\n   Then wait 10 seconds and re-run this test.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_mongodb() else 1)
