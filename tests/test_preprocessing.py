"""Unit tests for preprocessing module."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'preprocessing'))

from data_cleaner import SCADADataCleaner

@pytest.fixture
def sample_data():
    """Create sample SCADA data for testing."""
    return pd.DataFrame({
        'time': pd.date_range('2023-01-01', periods=100, freq='H'),
        'wind_speed': np.random.uniform(3, 15, 100),
        'power': np.random.uniform(100, 5000, 100),
        'rotor_speed': np.random.uniform(5, 15, 100)
    })

def test_initialize_cleaner():
    """Test cleaner initialization."""
    cleaner = SCADADataCleaner(max_power_kw=5000)
    assert cleaner.max_power == 5000
    assert cleaner.min_wind == 0

def test_normalize_timestamps(sample_data):
    """Test timestamp normalization."""
    cleaner = SCADADataCleaner()
    df = cleaner.normalize_timestamps(sample_data)
    assert len(df) <= 100
    assert 'time' in df.columns

def test_physical_limits(sample_data):
    """Test physical constraint enforcement."""
    cleaner = SCADADataCleaner(max_power_kw=5000)
    df = cleaner.validate_physical_limits(sample_data)
    assert (df['power'] >= 0).all()
    assert (df['power'] <= 5000).all()

def test_feature_engineering(sample_data):
    """Test feature creation."""
    cleaner = SCADADataCleaner()
    df = cleaner.engineer_features(sample_data)
    assert 'theoretical_power' in df.columns
    assert 'rolling_avg_wind' in df.columns
