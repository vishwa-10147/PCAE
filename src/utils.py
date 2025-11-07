"""Utility functions for PCAE project."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import yaml
import os
from pathlib import Path


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def ensure_dir(path: str) -> None:
    """Ensure directory exists, create if not."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_model(model_path: str):
    """Load trained model from file."""
    import joblib
    return joblib.load(model_path)


def save_model(model, model_path: str) -> None:
    """Save trained model to file."""
    import joblib
    ensure_dir(os.path.dirname(model_path))
    joblib.dump(model, model_path)


def create_time_windows(df: pd.DataFrame, window_size: str = '1H', 
                       time_col: str = 'timestamp') -> pd.DataFrame:
    """Create time windows for feature aggregation."""
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col)
    df['window'] = pd.to_datetime(df[time_col]).dt.floor(window_size)
    return df


def calculate_entropy(series: pd.Series) -> float:
    """Calculate Shannon entropy of a series."""
    value_counts = series.value_counts()
    probabilities = value_counts / len(series)
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    return entropy


def safe_divide(numerator, denominator, default: float = 0.0):
    """Safely divide two numbers/arrays/Series, with zero-protection.

    Supports scalars, numpy arrays, and pandas Series. Returns the same type
    as the inputs (vectorized when inputs are vector-like).
    """
    # Vectorized handling for pandas Series
    if isinstance(denominator, pd.Series):
        denom = denominator.replace(0, np.nan)
        if isinstance(numerator, pd.Series):
            result = numerator / denom
            return result.fillna(default)
        else:
            result = numerator / denom
            return result.fillna(default)

    # Vectorized handling for numpy arrays
    if isinstance(denominator, np.ndarray):
        denom = np.where(denominator == 0, np.nan, denominator)
        result = numerator / denom
        return np.nan_to_num(result, nan=default, posinf=default, neginf=default)

    # Scalar fallback
    try:
        if denominator == 0:
            return default
    except Exception:
        pass
    return numerator / denominator


def get_top_features(shap_values, feature_names: List[str], top_k: int = 10) -> List[Dict]:
    """Get top contributing features from SHAP values."""
    if len(shap_values.shape) > 1:
        shap_values = shap_values[0]  # Get first prediction
    
    feature_contributions = [
        {"feature": name, "contribution": float(contrib)}
        for name, contrib in zip(feature_names, shap_values)
    ]
    
    # Sort by absolute contribution
    feature_contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    return feature_contributions[:top_k]


def get_recommended_action(probability: float, top_features: List[Dict]) -> str:
    """Get recommended action based on probability and top features."""
    if probability < 0.3:
        return "Monitor - Low risk detected"
    elif probability < 0.6:
        return "Review logs and investigate suspicious activity"
    elif probability < 0.8:
        return "Increase monitoring and consider blocking suspicious IPs"
    else:
        return "Isolate host and block suspicious IPs immediately"


def anonymize_ip(ip: str) -> str:
    """Anonymize IP address for privacy (simple hashing)."""
    import hashlib
    return hashlib.md5(ip.encode()).hexdigest()[:12]


def validate_asset_ip(ip: str) -> bool:
    """Validate IP address format."""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

