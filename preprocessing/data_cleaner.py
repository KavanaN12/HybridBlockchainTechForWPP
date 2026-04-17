"""
preprocessing/data_cleaner.py
Data cleaning and feature engineering for SCADA data
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import os
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_kaggle_dataset(output_dir="data/raw"):
    """
    Download wind turbine SCADA dataset from Kaggle using kagglehub.
    
    Args:
        output_dir: Directory to save dataset
        
    Returns:
        Path to downloaded dataset file
    """
    try:
        import kagglehub
    except ImportError:
        logger.error("kagglehub not installed. Run: pip install kagglehub")
        return None
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Downloading Wind Turbine SCADA dataset from Kaggle...")
    
    try:
        # Download dataset - using common wind turbine SCADA dataset
        path = kagglehub.dataset_download("pythonafroz/wind-turbine-scada-data")
        logger.info(f"✓ Dataset downloaded to: {path}")
        
        # Find CSV files in downloaded path
        csv_files = list(Path(path).glob("**/*.csv"))
        
        if csv_files:
            # Copy first CSV to our data directory
            source_file = csv_files[0]
            dest_file = output_path / "kaggle_scada.csv"
            
            logger.info(f"Copying: {source_file.name} → {dest_file}")
            df = pd.read_csv(source_file)
            df.to_csv(dest_file, index=False)
            
            logger.info(f"✓ Dataset ready at: {dest_file}")
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {list(df.columns)}")
            
            return str(dest_file)
        else:
            logger.warning("No CSV files found in downloaded dataset")
            return None
            
    except Exception as e:
        logger.error(f"Failed to download: {e}")
        logger.info("Alternative: Download manually from https://www.kaggle.com/datasets/pythonafroz/wind-turbine-scada-data")
        return None

class SCADADataCleaner:
    """Clean and preprocess raw SCADA data from Kaggle."""
    
    def __init__(self, max_power_kw=5000, min_wind_speed=0, max_wind_speed=30):
        """
        Initialize cleaner with physical constraints.
        
        Args:
            max_power_kw: Rated turbine capacity
            min_wind_speed: Physical lower bound
            max_wind_speed: Physical upper bound (safety cutout)
        """
        self.max_power = max_power_kw
        self.min_wind = min_wind_speed
        self.max_wind = max_wind_speed
        self.report = {}
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client["wpp_digital_twin"]
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load SCADA dataset from CSV."""
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} records, columns: {list(df.columns)}")
        self.report['rows_initial'] = len(df)
        return df
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names from Kaggle dataset."""
        column_mapping = {
            'Datetime': 'datetime',
            'WindSpeed': 'wind_speed',
            'PowerOutput': 'power',
            'RotorSpeed': 'rotor_speed',
            'GeneratorSpeed': 'generator_speed',
            'GeneratorTemperature': 'temp',
            'offsetWindDirection': 'wind_direction'
        }
        # Rename columns that exist
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        return df
    
    def normalize_timestamps(self, df: pd.DataFrame, time_col='datetime') -> pd.DataFrame:
        """Convert timestamps to hourly granularity."""
        # First standardize column names
        df = self.standardize_columns(df)
        
        if time_col not in df.columns:
            logger.warning(f"Column {time_col} not found, skipping normalization")
            return df
        
        try:
            df[time_col] = pd.to_datetime(df[time_col])
            df = df.set_index(time_col).resample('H').mean().reset_index()
            logger.info(f"Resampled to hourly — {len(df)} records")
        except Exception as e:
            logger.warning(f"Could not normalize timestamps: {e}")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, threshold=0.3) -> pd.DataFrame:
        """Remove/interpolate missing values based on threshold."""
        missing_pct = df.isnull().sum() / len(df)
        cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
        df = df.drop(columns=cols_to_drop, errors='ignore')
        df = df.interpolate(method='linear', limit_direction='both')
        logger.info(f"Handled missing values — dropped {len(cols_to_drop)} high-missing columns")
        return df
    
    def detect_outliers(self, df: pd.DataFrame, columns=None) -> pd.DataFrame:
        """Detect outliers using IQR method."""
        if columns is None:
            columns = ['power', 'wind_speed']
        
        removed_count = 0
        for col in columns:
            if col not in df.columns:
                continue
            try:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                removed_count += len(outliers)
                logger.info(f"Removed {len(outliers)} outliers from {col}")
            except Exception as e:
                logger.warning(f"Could not detect outliers in {col}: {e}")
        
        if removed_count > 0:
            logger.info(f"Total outliers removed: {removed_count}")
        return df
    
    def validate_physical_limits(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enforce physical constraints."""
        initial_len = len(df)
        # Power constraint
        if 'power' in df.columns:
            df = df[(df['power'] >= 0) & (df['power'] <= self.max_power)]
        # Wind speed constraint
        if 'wind_speed' in df.columns:
            df = df[(df['wind_speed'] >= self.min_wind) & (df['wind_speed'] <= self.max_wind)]
        removed = initial_len - len(df)
        logger.info(f"Validated physical limits — removed {removed} invalid records")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for ML."""
        if 'wind_speed' in df.columns and 'power' in df.columns:
            # Theoretical power (simple: proportional to V^3)
            rotor_radius = 35  # meters (typical)
            air_density = 1.225  # kg/m^3
            cp_coefficient = 0.4  # power coefficient
            rotor_area = np.pi * rotor_radius ** 2
            
            df['theoretical_power'] = 0.5 * air_density * rotor_area * (df['wind_speed']**3) * cp_coefficient
            df['theoretical_power'] = df['theoretical_power'].clip(0, self.max_power)
            
            # Rolling average (use standardized columns if present)
            source_wind = 'wind_speed' if 'wind_speed' in df.columns else 'WindSpeed' if 'WindSpeed' in df.columns else None
            if source_wind is not None:
                df['rolling_avg_wind'] = df[source_wind].rolling(window=10, min_periods=1).mean()

            source_power = 'power' if 'power' in df.columns else 'PowerOutput' if 'PowerOutput' in df.columns else None
            if source_power is not None:
                df['lag_power'] = df[source_power].shift(1).bfill()

            # Efficiency gap
            df['efficiency_gap'] = df[source_power] - df['theoretical_power'] if source_power is not None else np.nan

            # Drop rows with NaN values after feature engineering
            df = df.dropna()

            logger.info("Added rolling_avg_wind and lag_power features")
            
            logger.info(f"Engineered features: theoretical_power, rolling_avg_wind, lag_power, efficiency_gap")
        
        return df
    
    def run_full_pipeline_chunked(self, input_csv: str, output_csv: str, chunk_size=100000) -> None:
        """Execute cleaning pipeline in chunks to handle large datasets with limited memory."""
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting chunked processing (chunk size: {chunk_size:,})")
        
        chunk_count = 0
        total_output_rows = 0
        header_written = False
        
        try:
            # Read CSV in chunks
            for chunk in pd.read_csv(input_csv, chunksize=chunk_size):
                chunk_count += 1
                logger.info(f"Processing chunk {chunk_count} ({len(chunk):,} rows)...")
                
                # Process each chunk
                df = chunk.copy()
                df = self.standardize_columns(df)  # Standardize column names first
                df = self.normalize_timestamps(df)
                df = self.handle_missing_values(df)
                df = self.detect_outliers(df, columns=['power', 'wind_speed'])
                df = self.validate_physical_limits(df)
                df = self.engineer_features(df)
                
                # Append to output file
                if not header_written:
                    df.to_csv(output_csv, mode='w', index=False)
                    header_written = True
                    logger.info(f"  → Output file created with {len(df):,} rows")
                else:
                    df.to_csv(output_csv, mode='a', index=False, header=False)
                    logger.info(f"  → Appended {len(df):,} rows")
                
                total_output_rows += len(df)
            
            self.report['rows_initial'] = chunk_count * chunk_size  # Approximate
            self.report['rows_final'] = total_output_rows
            self.report['reduction_pct'] = 100 * (1 - total_output_rows / (chunk_count * chunk_size))
            
            logger.info(f"✓ Chunked processing complete!")
            logger.info(f"  Chunks processed: {chunk_count}")
            logger.info(f"  Total output rows: {total_output_rows:,}")
            logger.info(f"✓ Cleaned data saved to {output_csv}")
            
        except Exception as e:
            logger.error(f"Error during chunked processing: {e}")
            raise
    
    def run_full_pipeline(self, input_file, output_file):
        """Execute full cleaning pipeline using chunked processing."""
        try:
            # Load and preprocess data
            df = self.load_data(input_file)
            df = self.standardize_columns(df)
            
            # Save cleaned data
            df.to_csv(output_file, index=False)
            logger.info(f"Cleaned data saved to {output_file}")
            
            # Store in MongoDB
            self.store_in_mongodb(df, "scada_cleaned")
            return df
        except Exception as e:
            logger.error(f"Error during pipeline execution: {e}")
            raise

    def store_in_mongodb(self, df, collection_name):
        """Store DataFrame in MongoDB."""
        collection = self.db[collection_name]
        records = df.to_dict(orient="records")
        collection.insert_many(records)
        logger.info(f"Stored {len(records)} records in MongoDB collection '{collection_name}'")

    def archive_to_s3(self, local_file, bucket_name, s3_key):
        """Upload a local file to S3 if AWS credentials are configured."""
        try:
            import boto3
        except ImportError:
            logger.warning("boto3 is not installed; S3 archive skipped.")
            return False

        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        if not aws_access_key or not aws_secret:
            logger.warning("AWS credentials are not configured; S3 archive skipped.")
            return False

        try:
            s3 = boto3.client("s3", region_name=aws_region)
            s3.upload_file(str(local_file), bucket_name, s3_key)
            logger.info(f"Uploaded {local_file} to s3://{bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.warning(f"S3 archive failed: {e}")
            return False

def run_pipeline():
    """Main execution."""
    cleaner = SCADADataCleaner()
    
    # TODO: Replace with actual Kaggle dataset path
    input_file = "data/raw/kaggle_scada.csv"
    output_file = "data/processed/scada_preprocessed.csv"
    
    if not Path(input_file).exists():
        print(f"⚠ Dataset not found at {input_file}")
        print("Download from Kaggle: https://www.kaggle.com/datasets/...")
        return
    
    df = cleaner.run_full_pipeline(input_file, output_file)
    print(f"\n✓ Cleaned {cleaner.report['rows_initial']} → {cleaner.report['rows_final']} records")
    print(f"  Reduction: {cleaner.report['reduction_pct']:.1f}%")

if __name__ == "__main__":
    run_pipeline()
