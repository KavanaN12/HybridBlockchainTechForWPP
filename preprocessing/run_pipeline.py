"""Main entry point for preprocessing."""
from pathlib import Path
from data_cleaner import SCADADataCleaner, download_kaggle_dataset
import sys
import os

# Debugging: Print the current Python path
print("PYTHONPATH:", sys.path)

# Ensure the project directory is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
    print("Added project root to PYTHONPATH:", project_root)

from forecasting.models import ForecastingEngine
import boto3
import logging

def main():
    """Execute preprocessing pipeline."""
    print("=" * 60)
    print("WPP Digital Twin - Data Preprocessing Pipeline")
    print("=" * 60)
    
    cleaner = SCADADataCleaner(max_power_kw=5000)
    
    input_file = "data/raw/kaggle_scada.csv"
    output_file = "data/processed/scada_preprocessed.csv"
    
    # Check if data exists, if not attempt download
    if not Path(input_file).exists():
        print(f"\n📥 Dataset not found at {input_file}")
        print("   Attempting automatic download from Kaggle...")
        
        downloaded_file = download_kaggle_dataset("data/raw")
        
        if downloaded_file and Path(downloaded_file).exists():
            input_file = downloaded_file
            print(f"\n✓ Downloaded successfully!")
        else:
            print(f"\n❌ Download failed or kagglehub not available")
            print("\n📍 Manual Alternative:")
            print("   1. Visit: https://www.kaggle.com/datasets/pythonafroz/wind-turbine-scada-data")
            print("   2. Download the CSV file")
            print(f"   3. Save to: data/raw/kaggle_scada.csv")
            sys.exit(1)
    else:
        print(f"\n✓ Dataset found at: {input_file}")
    
    try:
        df = cleaner.run_full_pipeline(input_file, output_file)
        print(f"\n✓ SUCCESS!")
        print(f"  Initial records:  {cleaner.report['rows_initial']}")
        print(f"  Final records:    {cleaner.report['rows_final']}")
        print(f"  Reduction:        {cleaner.report['reduction_pct']:.1f}%")
        print(f"\n✓ Cleaned data saved to {output_file}")
    except Exception as e:
        print(f"\n❌ ERROR during pipeline: {e}")
        sys.exit(1)

    # Train forecasting models
    engine = ForecastingEngine()
    X_train, X_test, y_train, y_test = engine.prepare_features(df)
    if X_train is not None and y_train is not None:
        engine.train_linear_regression(X_train, y_train)
        engine.train_random_forest(X_train, y_train)
        print("\n\u2713 Forecasting models trained successfully")
    else:
        print("\n\u274c Failed to train models: Insufficient data")

    # Archive the cleaned data to S3
    cleaner.archive_to_s3(output_file, "wpp-digital-twin", "scada_preprocessed.csv")

if __name__ == "__main__":
    main()
