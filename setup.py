"""Setup script for PCAE project."""
import os
import sys
from pathlib import Path
import subprocess


def create_directories():
    """Create necessary directories."""
    dirs = [
        'data/raw',
        'data/processed',
        'data/features',
        'models',
        'logs',
        'config',
        'notebooks'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling dependencies...")
    requirements_path = Path(__file__).parent.parent / 'requirements.txt'
    
    if not requirements_path.exists():
        print(f"Error: requirements.txt not found at {requirements_path}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def main():
    print("="*60)
    print("Predictive Cyber Attack Engine - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\nCreating project directories...")
    create_directories()
    
    # Install dependencies
    print("\n" + "="*60)
    install_dependencies()
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Create sample data: python src/create_sample_data.py")
    print("2. Preprocess data: python src/preprocess.py")
    print("3. Engineer features: python src/feature_engineering.py")
    print("4. Train model: python src/train_model.py")
    print("5. Start API: cd api && uvicorn main:app --reload")
    print("6. Start Dashboard: cd dashboard && streamlit run app.py")
    print("\nOr run the quick_start script: python quick_start.py")


if __name__ == '__main__':
    main()

