"""
hashing/batch_hasher.py
SHA-256 batch hashing engine for data integrity
"""
import pandas as pd
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class BatchHasher:
    """Compute hashes for hourly data batches."""
    
    def __init__(self):
        self.hashes = []
    
    def compute_hash(self, data: dict) -> str:
        """Compute SHA-256 hash of data object."""
        # Convert to sorted JSON for deterministic hash
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash_obj = hashlib.sha256(data_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def batch_by_hour(self, df: pd.DataFrame, time_col='time') -> dict:
        """Group data by hour."""
        if time_col not in df.columns:
            logger.warning(f"Column {time_col} not found")
            return {}
        
        df[time_col] = pd.to_datetime(df[time_col])
        hourly_groups = df.groupby(df[time_col].dt.floor('H'))
        
        batches = {}
        for hour_key, group in hourly_groups:
            batches[hour_key.isoformat()] = group.to_dict('records')
        
        logger.info(f"Created {len(batches)} hourly batches")
        return batches
    
    def generate_hashes(self, hourly_batches: dict) -> pd.DataFrame:
        """Generate hashes for all batches."""
        hashes = []
        
        for hour, batch_data in hourly_batches.items():
            batch_dict = {
                'hour': hour,
                'record_count': len(batch_data),
                'data': batch_data
            }
            
            hash_value = self.compute_hash(batch_dict)
            
            hashes.append({
                'hour': hour,
                'batch_hash': hash_value,
                'record_count': len(batch_data),
                'timestamp_created': datetime.utcnow().isoformat()
            })
        
        logger.info(f"Generated {len(hashes)} hashes")
        self.hashes = hashes
        return pd.DataFrame(hashes)
    
    def verify_hash(self, hour: str, batch_data: list, stored_hash: str) -> bool:
        """Verify hash matches stored value."""
        batch_dict = {
            'hour': hour,
            'record_count': len(batch_data),
            'data': batch_data
        }
        computed_hash = self.compute_hash(batch_dict)
        match = computed_hash == stored_hash
        logger.info(f"Hash verification for {hour}: {'✓ PASS' if match else '✗ FAIL'}")
        return match

def generate_hashes():
    """Main execution."""
    print("=" * 60)
    print("WPP Digital Twin - Hash Engine")
    print("=" * 60)
    
    data_file = "data/processed/scada_preprocessed.csv"
    if not Path(data_file).exists():
        print(f"\n❌ Data not found at {data_file}")
        return
    
    # Load data
    df = pd.read_csv(data_file)
    
    # Generate hashes
    hasher = BatchHasher()
    # Use 'datetime' column if available, otherwise 'time'
    time_col = 'datetime' if 'datetime' in df.columns else 'time'
    hourly_batches = hasher.batch_by_hour(df, time_col=time_col)
    hashes_df = hasher.generate_hashes(hourly_batches)
    
    # Save
    output_file = "experiments/hourly_hashes.csv"
    Path(output_file).parent.mkdir(exist_ok=True)
    hashes_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Generated hashes for {len(hashes_df)} batches")
    print(f"✓ Saved to {output_file}")

if __name__ == "__main__":
    generate_hashes()
