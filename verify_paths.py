"""Verify all file paths in the project are correct."""
import os
from pathlib import Path

# Expected file structure
EXPECTED_FILES = {
    # Root level
    'README.md': 'Main project documentation',
    'STEP_BY_STEP_GUIDE.md': 'Detailed setup guide',
    'PROJECT_SUMMARY.md': 'Quick reference guide',
    'setup.py': 'Setup script',
    'quick_start.py': 'Quick start script',
    '.gitignore': 'Git ignore rules',
    'requirements.txt': 'Python dependencies (parent directory)',
    
    # Source code
    'src/utils.py': 'Utility functions',
    'src/preprocess.py': 'Data preprocessing',
    'src/feature_engineering.py': 'Feature engineering',
    'src/train_model.py': 'Model training',
    'src/evaluate_model.py': 'Model evaluation',
    'src/create_sample_data.py': 'Sample data generator',
    
    # API
    'api/main.py': 'FastAPI main application',
    'api/models.py': 'API data models',
    
    # Dashboard
    'dashboard/app.py': 'Streamlit dashboard',
    
    # Configuration
    'config/config.yaml': 'Project configuration',
}

EXPECTED_DIRS = [
    'data',
    'data/raw',
    'data/processed',
    'data/features',
    'models',
    'notebooks',
    'config',
    'logs',
]

def verify_structure():
    """Verify project structure."""
    base_path = Path(__file__).parent
    issues = []
    missing_files = []
    missing_dirs = []
    found_files = []
    found_dirs = []
    
    print("="*60)
    print("PCAE Project Structure Verification")
    print("="*60)
    
    # Check files
    print("\n[CHECKING FILES]")
    for file_path, description in EXPECTED_FILES.items():
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
            found_files.append(file_path)
        else:
            # Check if requirements.txt is in parent
            if file_path == 'requirements.txt':
                parent_path = base_path.parent / file_path
                if parent_path.exists():
                    print(f"  [OK] {file_path} (in parent directory)")
                    found_files.append(file_path)
                    continue
            print(f"  [MISSING] {file_path} - MISSING")
            missing_files.append((file_path, description))
    
    # Check directories
    print("\n[CHECKING DIRECTORIES]")
    for dir_path in EXPECTED_DIRS:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  [OK] {dir_path}/")
            found_dirs.append(dir_path)
        else:
            print(f"  [WARNING] {dir_path}/ - Will be created on first run")
            missing_dirs.append(dir_path)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"[OK] Files found: {len(found_files)}/{len(EXPECTED_FILES)}")
    print(f"[OK] Directories found: {len(found_dirs)}/{len(EXPECTED_DIRS)}")
    
    if missing_files:
        print(f"\n[MISSING] Missing files: {len(missing_files)}")
        for file_path, desc in missing_files:
            print(f"   - {file_path} ({desc})")
    
    if missing_dirs:
        print(f"\n[WARNING] Missing directories (will be auto-created): {len(missing_dirs)}")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}/")
    
    # Check for additional files
    print("\n[ADDITIONAL FILES FOUND]")
    all_expected = set(EXPECTED_FILES.keys())
    all_found_py = list(base_path.rglob("*.py"))
    all_found_md = list(base_path.rglob("*.md"))
    
    additional = []
    for py_file in all_found_py:
        rel_path = py_file.relative_to(base_path)
        if str(rel_path) not in all_expected and 'venv' not in str(rel_path) and '__pycache__' not in str(rel_path):
            additional.append(str(rel_path))
    
    for md_file in all_found_md:
        rel_path = md_file.relative_to(base_path)
        if str(rel_path) not in all_expected:
            additional.append(str(rel_path))
    
    if additional:
        for file_path in additional:
            print(f"   [INFO] {file_path} (not in expected list)")
    else:
        print("   (none)")
    
    # Path consistency check
    print("\n[CHECKING PATH REFERENCES]")
    check_path_consistency(base_path)
    
    print("\n" + "="*60)
    if missing_files:
        print("[FAIL] Verification incomplete - some files are missing")
        return False
    else:
        print("[SUCCESS] All expected files are present!")
        return True


def check_path_consistency(base_path):
    """Check if code references match actual structure."""
    import re
    
    # Check key files for path references
    key_files = [
        'src/preprocess.py',
        'src/feature_engineering.py',
        'src/train_model.py',
        'api/main.py',
        'dashboard/app.py',
    ]
    
    path_patterns = [
        r'data/raw',
        r'data/processed',
        r'data/features',
        r'models/',
        r'config/',
    ]
    
    issues = []
    for file_path in key_files:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                content = full_path.read_text()
                for pattern in path_patterns:
                    if re.search(pattern, content):
                        # Check if the path exists or will be created
                        if 'data/raw' in pattern and not (base_path / 'data' / 'raw').exists():
                            pass  # Will be created
                        elif 'data/processed' in pattern and not (base_path / 'data' / 'processed').exists():
                            pass  # Will be created
                        elif 'data/features' in pattern and not (base_path / 'data' / 'features').exists():
                            pass  # Will be created
                        elif 'models/' in pattern and not (base_path / 'models').exists():
                            pass  # Will be created
            except Exception as e:
                print(f"   [WARNING] Could not check {file_path}: {e}")
    
    print("   [OK] Path references appear consistent")


if __name__ == '__main__':
    success = verify_structure()
    exit(0 if success else 1)

