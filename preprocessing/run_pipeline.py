"""Main entry point for preprocessing."""
from pathlib import Path
from data_cleaner import SCADADataCleaner, download_kaggle_dataset
import sys

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

if __name__ == "__main__":
    main()
