"""
Quick Start Script for Predictive Cyber Attack Engine
Run this script to set up and run the entire project
"""
import os
import sys
import subprocess
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    try:
        import pandas
        import numpy
        import xgboost
        import fastapi
        import streamlit
        import shap
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_data():
    """Generate synthetic data if it doesn't exist"""
    print_header("Setting Up Data")
    
    data_dir = "data"
    netflow_file = os.path.join(data_dir, "netflow.csv")
    
    if os.path.exists(netflow_file):
        print("✅ Data files already exist")
        return True
    
    print("Generating synthetic data...")
    try:
        sys.path.insert(0, 'src')
        from data_generator import generate_synthetic_network_data, generate_asset_inventory
        
        df_flows, df_incidents, assets = generate_synthetic_network_data(n_assets=10, days=30)
        df_inventory = generate_asset_inventory(assets)
        
        os.makedirs(data_dir, exist_ok=True)
        df_flows.to_csv(os.path.join(data_dir, 'netflow.csv'), index=False)
        df_incidents.to_csv(os.path.join(data_dir, 'incidents.csv'), index=False)
        df_inventory.to_csv(os.path.join(data_dir, 'asset_inventory.csv'), index=False)
        
        print("✅ Data generated successfully")
        return True
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        return False

def setup_features():
    """Generate features if they don't exist"""
    print_header("Setting Up Features")
    
    features_file = os.path.join("data", "features.csv")
    
    if os.path.exists(features_file):
        print("✅ Features already exist")
        return True
    
    print("Creating features...")
    try:
        sys.path.insert(0, 'src')
        from feature_engineering import create_time_windows, merge_static_features
        import pandas as pd
        
        df_flows = pd.read_csv(os.path.join("data", "netflow.csv"))
        df_inventory = pd.read_csv(os.path.join("data", "asset_inventory.csv"))
        
        df_features = create_time_windows(df_flows, window_size='1H')
        df_features = merge_static_features(df_features, df_inventory)
        
        df_features.to_csv(features_file, index=False)
        print("✅ Features created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating features: {e}")
        return False

def train_model():
    """Train the model if it doesn't exist"""
    print_header("Training Model")
    
    model_file = os.path.join("models", "xgboost_model.pkl")
    
    if os.path.exists(model_file):
        print("✅ Model already trained")
        return True
    
    print("Training model...")
    try:
        sys.path.insert(0, 'src')
        from train_model import train_attack_predictor
        import pandas as pd
        
        df_features = pd.read_csv(os.path.join("data", "features.csv"))
        model, explainer, feature_cols, auc_roc, auc_pr = train_attack_predictor(df_features)
        
        print(f"✅ Model trained successfully")
        print(f"   AUC-ROC: {auc_roc:.4f}")
        print(f"   AUC-PR: {auc_pr:.4f}")
        return True
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return False

def main():
    """Main setup function"""
    print_header("Predictive Cyber Attack Engine - Setup")
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("❌ Please run this script from the PCAE directory")
        print("   Current directory:", os.getcwd())
        return
    
    # Step 1: Check dependencies
    if not check_dependencies():
        return
    
    # Step 2: Setup data
    if not setup_data():
        return
    
    # Step 3: Setup features
    if not setup_features():
        return
    
    # Step 4: Train model
    if not train_model():
        return
    
    print_header("Setup Complete!")
    print("\nNext steps:")
    print("1. Start the API server:")
    print("   python -m uvicorn api.main:app --reload")
    print("\n2. In a new terminal, start the dashboard:")
    print("   streamlit run dashboard/app.py")
    print("\n3. Open your browser to http://localhost:8501")

if __name__ == "__main__":
    main()

