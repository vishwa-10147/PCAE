"""Quick start script for PCAE - runs the full pipeline."""
import subprocess
import sys
from pathlib import Path
import os


def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print('='*60)
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False


def main():
    print("="*60)
    print("Predictive Cyber Attack Engine - Quick Start")
    print("="*60)
    print("\nThis script will:")
    print("1. Create sample data")
    print("2. Preprocess data")
    print("3. Engineer features")
    print("4. Train model")
    print("\nNote: API and Dashboard need to be started separately")
    print("="*60)
    
    # Change to PCAE directory
    os.chdir(Path(__file__).parent)
    
    steps = [
        ("python src/create_sample_data.py", "Creating sample data"),
        ("python src/preprocess.py", "Preprocessing data"),
        ("python src/feature_engineering.py", "Engineering features"),
        ("python src/train_model.py", "Training model"),
    ]
    
    for cmd, description in steps:
        if not run_command(cmd, description):
            print(f"\n[FAIL] Failed at: {description}")
            print("Please check the error messages above and fix any issues.")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("[OK] Quick start complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start API server:")
    print("   cd api")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\n2. Start Dashboard (in a new terminal):")
    print("   cd dashboard")
    print("   streamlit run app.py")
    print("\n3. Access:")
    print("   - API docs: http://localhost:8000/docs")
    print("   - Dashboard: http://localhost:8501")


if __name__ == '__main__':
    main()
