"""
download_dataset.py
Automated Kaggle dataset download using kagglehub
"""
import sys
from pathlib import Path

# Add preprocessing to path
sys.path.insert(0, str(Path(__file__).parent / 'preprocessing'))

from data_cleaner import download_kaggle_dataset

def main():
    """Download wind turbine SCADA dataset."""
    print("\n" + "="*70)
    print("   WPP Digital Twin - Automated Dataset Download")
    print("="*70)
    
    output_dir = "data/raw"
    
    print(f"\n🔄 Downloading Wind Turbine SCADA dataset from Kaggle...")
    print(f"📁 Destination: {output_dir}/")
    
    result = download_kaggle_dataset(output_dir)
    
    if result:
        print(f"\n✅ SUCCESS! Dataset downloaded and prepared.")
        print(f"📍 Location: {result}")
        print(f"\n✓ Next step: Run preprocessing")
        print(f"   python preprocessing/run_pipeline.py")
        return 0
    else:
        print(f"\n⚠️  Automatic download failed.")
        print(f"\n📍 Manual Download Instructions:")
        print(f"   1. Visit: https://www.kaggle.com/datasets/pythonafroz/wind-turbine-scada-data")
        print(f"   2. Click 'Download' button")
        print(f"   3. Save CSV to: data/raw/kaggle_scada.csv")
        print(f"\n   Then run: python preprocessing/run_pipeline.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
