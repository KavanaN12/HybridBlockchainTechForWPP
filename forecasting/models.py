"""
forecasting/models.py
ML-based power forecasting models
"""

# Load environment variables from .env
from dotenv import load_dotenv
import os
load_dotenv()

from ddtrace import patch_all
patch_all()

import logging
from pathlib import Path
import pickle
from datetime import timedelta

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel

from auth.auth_manager import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

log_path = Path("logs/api.log")
log_path.parent.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove old handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add handlers
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

# Forward uvicorn + fastapi logs to same handlers
logging.getLogger("uvicorn").handlers = root_logger.handlers
logging.getLogger("uvicorn.error").handlers = root_logger.handlers
logging.getLogger("uvicorn.access").handlers = root_logger.handlers
logging.getLogger("fastapi").handlers = root_logger.handlers

logger = logging.getLogger("wpp-digital-twin")

logger.info("Logging system initialized")

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI()

logger.info("FastAPI application started")

# =========================================================
# REQUEST LOGGING MIDDLEWARE
# =========================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"Response status: {response.status_code}")

    return response
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

    def load_models(self, checkpoint_dir="forecasting/models_checkpoint") -> bool:
        """Load models from checkpoint directory."""
        model_dir = Path(checkpoint_dir)
        if not model_dir.exists():
            logger.warning(f"No checkpoint dir found at {checkpoint_dir}")
            return False

        loaded = False
        for model_file in model_dir.glob("*_model.pkl"):
            with open(model_file, 'rb') as f:
                model_name = model_file.stem.replace("_model", "")
                self.models[model_name] = pickle.load(f)
                loaded = True
                logger.info(f"Loaded model: {model_name}")

        if not loaded:
            logger.warning("No models found in checkpoint directory")
        return loaded

# Define the FastAPI app
app = FastAPI()

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
        if not engine.load_models():
            raise RuntimeError("No trained models loaded. Run forecasting/models.py first.")

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

class ForecastRequest(BaseModel):
    wind_speed: float
    rolling_avg_wind: float
    lag_power: float

@app.post("/forecast")
def forecast_power(request: ForecastRequest):
    """API endpoint to forecast power based on user input."""
    try:
        engine = ForecastingEngine()
        if not engine.load_models():
            raise HTTPException(status_code=500, detail="No trained models available.")

        # Prepare input data
        input_data = pd.DataFrame([{
            "wind_speed": request.wind_speed,
            "rolling_avg_wind": request.rolling_avg_wind,
            "lag_power": request.lag_power
        }])

        # Ensure all models are loaded
        predictions = {}
        for name, model in engine.models.items():
            predictions[name] = model.predict(input_data)[0]

        return {"predictions": predictions}

    except Exception as e:
        logger.error(f"Error in forecasting: {e}")
        raise HTTPException(status_code=500, detail="Error in forecasting.")

class PredictionRequest(BaseModel):
    wind_speed: float
    rolling_avg_wind: float
    lag_power: float

@app.post("/predict")
def predict_power(request: PredictionRequest):
    """API endpoint to predict power based on user input."""
    try:
        engine = ForecastingEngine()
        if not engine.load_models():
            raise HTTPException(status_code=500, detail="No trained models available.")

        # Prepare input data
        input_data = pd.DataFrame([{
            "wind_speed": request.wind_speed,
            "rolling_avg_wind": request.rolling_avg_wind,
            "lag_power": request.lag_power
        }])

        # Ensure all models are loaded
        predictions = {}
        for name, model in engine.models.items():
            predictions[name] = model.predict(input_data)[0]

        return {"predictions": predictions}

    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        raise HTTPException(status_code=500, detail="Error in prediction.")

# User database simulation
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": hash_password("testpassword"),
        "role": "Producer"
    },
    "newuser": {
        "username": "newuser",
        "hashed_password": hash_password("newpassword"),
        "role": "Consumer"
    }
}

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Authentication endpoints
@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": "Consumer"  # Default role
    }
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token)
def login(user: User):
    db_user = fake_users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def read_users_me(request: Request, current_user: str = Depends(get_current_user)):
    logger.debug(f"Authorization header: {request.headers.get('authorization')}")
    logger.debug(f"Current user: {current_user}")
    return {"username": current_user, "role": fake_users_db[current_user]["role"]}
