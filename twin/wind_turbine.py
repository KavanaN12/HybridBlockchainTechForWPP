"""
twin/wind_turbine.py
Physics-based wind turbine digital twin model
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class WindTurbineModel:
    """Physics-based turbine model following IEC 61400 standard."""
    
    def __init__(self, rotor_diameter_m=70, rated_power_kw=2000, cp_max=0.45):
        """
        Initialize turbine model.
        
        Args:
            rotor_diameter_m: Rotor diameter in meters
            rated_power_kw: Rated power capacity in kW
            cp_max: Maximum power coefficient (Betz limit ~0.59, typical ~0.4-0.45)
        """
        self.rotor_diameter = rotor_diameter_m
        self.rotor_area = np.pi * (rotor_diameter_m / 2) ** 2
        self.rated_power = rated_power_kw
        self.cp_max = cp_max
        self.air_density = 1.225  # kg/m^3 at sea level
        
        # Operating zones (m/s)
        self.cut_in_speed = 3.0
        self.rated_speed = 12.0
        self.cut_out_speed = 25.0
        
        logger.info(f"Initialized turbine: {rotor_diameter_m}m rotor, {rated_power_kw}kW rated")
    
    def power_coefficient(self, wind_speed: float) -> float:
        """
        Calculate power coefficient based on wind speed.
        Uses simplified IEC 61400 curve.
        """
        if wind_speed < self.cut_in_speed or wind_speed > self.cut_out_speed:
            return 0.0
        elif wind_speed <= self.rated_speed:
            # Ramp up from cut-in to rated
            ramp = (wind_speed - self.cut_in_speed) / (self.rated_speed - self.cut_in_speed)
            return self.cp_max * (ramp ** 2)
        else:
            # Decline after rated (pitch control)
            return self.cp_max * (1 - 0.5 * (wind_speed - self.rated_speed) / 
                                  (self.cut_out_speed - self.rated_speed))
    
    def calculate_theoretical_power(self, wind_speed: float) -> float:
        """
        Calculate theoretical power output.
        P = 0.5 * rho * A * Cp * V^3
        """
        if wind_speed < self.cut_in_speed or wind_speed > self.cut_out_speed:
            return 0.0
        
        cp = self.power_coefficient(wind_speed)
        power = 0.5 * self.air_density * self.rotor_area * (wind_speed ** 3) * cp
        
        # Cap at rated power
        power = min(power, self.rated_power)
        return max(0, power)
    
    def turbine_operating_zone(self, wind_speed: float) -> str:
        """Determine operating zone."""
        if wind_speed < self.cut_in_speed:
            return "Off"
        elif wind_speed < self.rated_speed:
            return "Partial Load"
        elif wind_speed < self.cut_out_speed:
            return "Rated"
        else:
            return "Cut-Out"
    
    def efficiency_gap(self, actual_power: float, theoretical_power: float) -> float:
        """Calculate efficiency gap (actual - theoretical)."""
        return actual_power - theoretical_power
    
    def validate_twin_on_dataset(self, df: pd.DataFrame, 
                                  wind_col='wind_speed', 
                                  power_col='power') -> Dict:
        """
        Validate twin accuracy against real data.
        
        Args:
            df: DataFrame with wind speed and actual power
            wind_col: Column name for wind speed
            power_col: Column name for actual power
            
        Returns:
            Dictionary with accuracy metrics
        """
        # Calculate theoretical power
        theoretical = df[wind_col].apply(self.calculate_theoretical_power)
        actual = df[power_col]
        
        # Metrics
        mae = np.mean(np.abs(actual - theoretical))
        rmse = np.sqrt(np.mean((actual - theoretical) ** 2))
        r2 = 1 - (np.sum((actual - theoretical) ** 2) / np.sum((actual - np.mean(actual)) ** 2))
        
        # Normalized metrics
        rated_power = self.rated_power
        mae_pct = 100 * mae / rated_power
        rmse_pct = 100 * rmse / rated_power
        
        metrics = {
            'mae': mae,
            'mae_pct': mae_pct,
            'rmse': rmse,
            'rmse_pct': rmse_pct,
            'r2': r2,
            'samples': len(df)
        }
        
        logger.info(f"Twin Validation Results:")
        logger.info(f"  MAE: {mae:.1f} kW ({mae_pct:.1f}%)")
        logger.info(f"  RMSE: {rmse:.1f} kW ({rmse_pct:.1f}%)")
        logger.info(f"  R²: {r2:.3f}")
        
        return metrics
    
    def calculate_zone_errors(self, df: pd.DataFrame, 
                              wind_col='wind_speed', 
                              power_col='power') -> pd.DataFrame:
        """Calculate errors by operating zone."""
        df_copy = df.copy()
        df_copy['theoretical_power'] = df[wind_col].apply(self.calculate_theoretical_power)
        df_copy['zone'] = df[wind_col].apply(self.turbine_operating_zone)
        df_copy['error'] = df[power_col] - df_copy['theoretical_power']
        df_copy['abs_error'] = np.abs(df_copy['error'])
        
        zone_stats = df_copy.groupby('zone').agg({
            'error': ['mean', 'std'],
            'abs_error': 'mean'
        })
        
        logger.info(f"\nErrors by Operating Zone:")
        logger.info(zone_stats)
        
        return zone_stats

def validate_twin():
    """Example validation function."""
    import sys
    from pathlib import Path
    
    print("=" * 60)
    print("WPP Digital Twin - Twin Validation")
    print("=" * 60)
    
    # Initialize turbine
    turbine = WindTurbineModel(rotor_diameter_m=70, rated_power_kw=2000)
    
    # Check if preprocessed data exists
    data_file = "data/processed/scada_preprocessed.csv"
    if not Path(data_file).exists():
        print(f"\n❌ ERROR: Preprocessed data not found at {data_file}")
        print("   Run preprocessing first: python preprocessing/run_pipeline.py")
        sys.exit(1)
    
    # Load and validate
    df = pd.read_csv(data_file)
    metrics = turbine.validate_twin_on_dataset(df, wind_col='wind_speed', power_col='power')
    
    # Save results
    results_file = "experiments/twin_validation_results.csv"
    Path(results_file).parent.mkdir(exist_ok=True)
    pd.DataFrame([metrics]).to_csv(results_file, index=False)
    print(f"\n✓ Results saved to {results_file}")

if __name__ == "__main__":
    validate_twin()
