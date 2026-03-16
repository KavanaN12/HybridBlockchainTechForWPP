"""Unit tests for digital twin module."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'twin'))

from wind_turbine import WindTurbineModel

@pytest.fixture
def turbine():
    """Create turbine instance."""
    return WindTurbineModel(rotor_diameter_m=70, rated_power_kw=2000)

def test_turbine_initialization(turbine):
    """Test turbine initialization."""
    assert turbine.rated_power == 2000
    assert turbine.cut_in_speed == 3.0

def test_power_coefficient(turbine):
    """Test power coefficient calculation."""
    # Below cut-in
    assert turbine.power_coefficient(2.0) == 0.0
    
    # Middle wind speed
    cp_mid = turbine.power_coefficient(8.0)
    assert 0 < cp_mid < turbine.cp_max
    
    # Above cut-out
    assert turbine.power_coefficient(26.0) == 0.0

def test_theoretical_power(turbine):
    """Test theoretical power calculation."""
    power_low = turbine.calculate_theoretical_power(4.0)
    power_high = turbine.calculate_theoretical_power(10.0)
    assert power_low < power_high, f"Expected {power_low} < {power_high}"
    assert power_low >= 0
    assert power_high <= turbine.rated_power

def test_operating_zone(turbine):
    """Test zone identification."""
    assert turbine.turbine_operating_zone(2.0) == "Off"
    assert turbine.turbine_operating_zone(8.0) == "Partial Load"
    assert turbine.turbine_operating_zone(14.0) == "Rated"
    assert turbine.turbine_operating_zone(26.0) == "Cut-Out"
