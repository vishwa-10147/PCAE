"""FastAPI service for PCAE predictions."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils import load_model, load_config, get_top_features, get_recommended_action, validate_asset_ip
import shap

app = FastAPI(
    title="Predictive Cyber Attack Engine API",
    description="API for predicting attack probabilities on network assets",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables (loaded at startup)
model = None
feature_names = []
explainer = None
config = {}


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    asset_ip: str = Field(..., description="IP address of the asset")
    time_window_start: str = Field(..., description="Start of prediction window (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_ip": "192.168.1.100",
                "time_window_start": "2024-01-15T10:00:00"
            }
        }


class FeatureContribution(BaseModel):
    """Feature contribution model."""
    feature: str
    contribution: float


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    asset: str
    probability: float
    top_features: List[FeatureContribution]
    recommended_action: str
    timestamp: str


class AssetInfo(BaseModel):
    """Asset information model."""
    asset_ip: str
    last_prediction: Optional[float] = None
    last_updated: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Load model and resources on startup."""
    global model, feature_names, explainer, config
    
    try:
        # Load config
        config = load_config()
        model_path = config.get('model_path', 'models/xgboost_model.pkl')
        
        # Load model
        print(f"Loading model from {model_path}...")
        model = load_model(model_path)
        
        # Load feature names
        import json
        info_path = Path('models/model_info.json')
        if info_path.exists():
            with open(info_path, 'r') as f:
                model_info = json.load(f)
                feature_names = model_info.get('feature_names', [])
        else:
            # Try to infer from model
            feature_names = [f'feature_{i}' for i in range(model.n_features_in_)]
        
        print(f"Model loaded with {len(feature_names)} features")
        
        # Initialize SHAP explainer (use TreeExplainer for XGBoost)
        if model is not None:
            explainer = shap.TreeExplainer(model)
            print("SHAP explainer initialized")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("API will run but predictions will fail. Please ensure model is trained.")


def get_features_for_asset(asset_ip: str, time_window_start: str) -> np.ndarray:
    """Get features for an asset at a given time window."""
    # This is a placeholder - in production, fetch from feature store
    # For now, return zeros (will need actual feature store integration)
    
    # Load recent features if available
    features_file = Path('data/features/test.csv')
    if features_file.exists():
        df = pd.read_csv(features_file)
        asset_data = df[df['asset_ip'] == asset_ip]
        
        if not asset_data.empty:
            # Get most recent window
            asset_data['window'] = pd.to_datetime(asset_data['window'])
            latest = asset_data.sort_values('window').iloc[-1]
            
            # Extract features
            feature_cols = [col for col in latest.index 
                          if col not in ['window', 'asset_ip', 'label']]
            feature_values = latest[feature_cols].fillna(0).values
            return feature_values.reshape(1, -1)
    
    # Default: return zeros (mean/median imputation would be better)
    n_features = len(feature_names) if feature_names else model.n_features_in_
    return np.zeros((1, n_features))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "features_count": len(feature_names) if feature_names else 0
    }


@app.get("/assets")
async def list_assets():
    """List all monitored assets."""
    assets_file = Path('data/processed/assets.csv')
    if assets_file.exists():
        df = pd.read_csv(assets_file)
        assets = [{"asset_ip": ip} for ip in df['asset_ip'].unique()]
        return {"assets": assets, "count": len(assets)}
    return {"assets": [], "count": 0}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict attack probability for an asset."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate asset IP
    if not validate_asset_ip(request.asset_ip):
        raise HTTPException(status_code=400, detail="Invalid IP address format")
    
    try:
        # Get features for asset
        features = get_features_for_asset(request.asset_ip, request.time_window_start)
        
        # Ensure correct number of features
        if features.shape[1] != model.n_features_in_:
            raise HTTPException(
                status_code=500,
                detail=f"Feature mismatch: expected {model.n_features_in_}, got {features.shape[1]}"
            )
        
        # Predict probability
        probability = model.predict_proba(features)[0, 1]
        
        # Get SHAP values for explainability
        top_features = []
        if explainer is not None and feature_names:
            try:
                shap_values = explainer.shap_values(features)
                top_features = get_top_features(shap_values, feature_names, top_k=10)
            except Exception as e:
                print(f"Error computing SHAP values: {e}")
                # Fallback: use feature importance
                importances = model.feature_importances_
                top_indices = np.argsort(importances)[-10:][::-1]
                top_features = [
                    {"feature": feature_names[i], "contribution": float(importances[i])}
                    for i in top_indices
                ]
        
        # Get recommended action
        recommended_action = get_recommended_action(probability, top_features)
        
        return PredictionResponse(
            asset=request.asset_ip,
            probability=float(probability),
            top_features=[FeatureContribution(**f) for f in top_features],
            recommended_action=recommended_action,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Predictive Cyber Attack Engine API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "assets": "/assets",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
