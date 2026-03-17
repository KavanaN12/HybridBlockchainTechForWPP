"""
forecasting/models.py
ML-based power forecasting models
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class ForecastingEngine:
    """ML-based forecasting for wind power."""
    
    def __init__(self):
        self.models = {}
        self.metrics = {}
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare training data."""
        # Features
        feature_cols = ['wind_speed', 'rolling_avg_wind', 'lag_power']
        target_col = 'power'
        
        # Filter available columns
        available_features = [c for c in feature_cols if c in df.columns]
        
        if target_col not in df.columns or len(available_features) == 0:
            logger.warning("Required columns not found")
            return None, None, None, None
        
        # Remove NaN
        df_clean = df[available_features + [target_col]].dropna()
        
        X = df_clean[available_features]
        y = df_clean[target_col]
        
        # Train/test split (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"Prepared features: {available_features}")
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def train_linear_regression(self, X_train, y_train):
        """Train linear regression model."""
        print("Training Linear Regression...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        self.models['linear'] = model
        logger.info("Linear Regression trained")
        return model
    
    def train_random_forest(self, X_train, y_train):
        """Train random forest model."""
        print("Training Random Forest...")
        model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        logger.info("Random Forest trained")
        return model
    
    def evaluate_models(self, X_test, y_test) -> pd.DataFrame:
        """Evaluate all trained models."""
        results = []
        
        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # MAPE with division-by-zero protection
            non_zero_mask = y_test != 0
            if non_zero_mask.sum() > 0:
                mape = np.mean(np.abs((y_test[non_zero_mask] - y_pred[non_zero_mask]) / y_test[non_zero_mask])) * 100
            else:
                mape = 0.0
            
            results.append({
                'model': name,
                'mae': mae,
                'rmse': rmse,
                'mape': mape
            })
            
            logger.info(f"{name.upper()}: MAE={mae:.1f}, RMSE={rmse:.1f}, MAPE={mape:.1f}%")
        
        return pd.DataFrame(results)
    
    def save_models(self, output_dir="forecasting/models_checkpoint"):
        """Save trained models."""
        Path(output_dir).mkdir(exist_ok=True)
        for name, model in self.models.items():
            path = f"{output_dir}/{name}_model.pkl"
            with open(path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Saved {name} to {path}")

def evaluate_forecast(X_test=None, y_test=None):
    """Evaluate forecast model performance.

    If model results exist from prior training (`experiments/forecast_results.csv`), return them.
    Otherwise, if X_test and y_test are provided and models are checkpointed, evaluate them.
    """
    result_file = Path("experiments/forecast_results.csv")
    if result_file.exists():
        return pd.read_csv(result_file)

    if X_test is not None and y_test is not None:
        engine = ForecastingEngine()
        # Load models from checkpoint if available
        model_dir = Path("forecasting/models_checkpoint")
        if model_dir.exists():
            for model_file in model_dir.glob("*_model.pkl"):
                model_name = model_file.stem.replace("_model", "")
                with open(model_file, "rb") as f:
                    engine.models[model_name] = pickle.load(f)

        if not engine.models:
            raise RuntimeError("No trained models loaded. Run forecasting.train_models() first.")

        return engine.evaluate_models(X_test, y_test)

    raise ValueError("No forecast evaluation data found. Provide test data or run training first.")


def train_models():
    """Execute full forecasting pipeline."""
    print("=" * 60)
    print("WPP Digital Twin - Forecasting Engine")
    print("=" * 60)
    
    # Check data
    data_file = "data/processed/scada_preprocessed.csv"
    if not Path(data_file).exists():
        print(f"\n❌ Preprocessed data not found at {data_file}")
        return
    
    # Load data
    df = pd.read_csv(data_file)
    
    # Initialize engine
    engine = ForecastingEngine()
    X_train, X_test, y_train, y_test = engine.prepare_features(df)
    
    if X_train is None:
        print("❌ Error preparing features")
        return
    
    # Train models
    engine.train_linear_regression(X_train, y_train)
    engine.train_random_forest(X_train, y_train)
    
    # Evaluate
    results = engine.evaluate_models(X_test, y_test)
    
    # Save
    engine.save_models()
    results_file = "experiments/forecast_results.csv"
    Path(results_file).parent.mkdir(exist_ok=True)
    results.to_csv(results_file, index=False)
    
    print(f"\n✓ Forecast models trained and saved")
    print(f"✓ Results: {results_file}")

if __name__ == "__main__":
    train_models()
