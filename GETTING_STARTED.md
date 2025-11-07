# 🚀 Getting Started - Step-by-Step Guide

This guide will walk you through starting the Predictive Cyber Attack Engine project from scratch.

## Prerequisites Check

Before starting, ensure you have:
- ✅ **Python 3.8 or higher** installed
- ✅ **pip** (Python package manager) installed
- ✅ **PowerShell** or **Command Prompt** access

To check your Python version:
```powershell
python --version
```

---

## Method 1: Quick Start (Recommended for First Time)

This is the fastest way to get everything running.

### Step 1: Navigate to Project Directory

```powershell
cd D:\cybersecurity\PCAE
```

### Step 2: Install Dependencies

```powershell
python setup.py
```

This will:
- Check Python version
- Create necessary directories
- Install all required packages from `requirements.txt`

**Expected time: 2-5 minutes**

### Step 3: Run the Full Pipeline

```powershell
python quick_start.py
```

This automatically runs:
1. ✅ Create sample data
2. ✅ Preprocess data
3. ✅ Engineer features
4. ✅ Train the model

**Expected time: 2-5 minutes**

### Step 4: Start the Services

You have two options:

#### Option A: Use PowerShell Script (Windows)

```powershell
.\start_all.ps1
```

This will open two new PowerShell windows:
- One for the API server (port 8000)
- One for the Dashboard (port 8501)

#### Option B: Manual Start (Two Terminals)

**Terminal 1 - Start API Server:**
```powershell
cd D:\cybersecurity\PCAE
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Dashboard:**
```powershell
cd D:\cybersecurity\PCAE
streamlit run dashboard/app.py
```

### Step 5: Access the Application

Once both services are running:

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Dashboard**: http://localhost:8501

---

## Method 2: Manual Step-by-Step (For Learning)

If you want to understand each step in detail:

### Step 1: Install Dependencies

```powershell
cd D:\cybersecurity\PCAE
pip install -r ..\requirements.txt
```

### Step 2: Create Sample Data

```powershell
python src/create_sample_data.py
```

This creates:
- `data/raw/sample_netflow.csv` - Network flow data
- `data/raw/incidents.csv` - Attack incidents
- `data/raw/assets.csv` - Asset inventory

### Step 3: Preprocess Data

```powershell
python src/preprocess.py
```

This processes raw data into time windows and creates:
- `data/processed/processed_data.csv`
- `data/processed/assets.csv`

### Step 4: Engineer Features

```powershell
python src/feature_engineering.py
```

This creates ML features:
- `data/features/train.csv` - Training data
- `data/features/test.csv` - Test data

### Step 5: Train the Model

```powershell
python src/train_model.py
```

This trains the XGBoost model and saves:
- `models/xgboost_model.pkl` - Trained model
- `models/model_info.json` - Model metadata
- `models/evaluation_metrics.png` - Performance plots

You should see output like:
```
Model Evaluation Metrics
==================================================
Accuracy: 0.xxxx
ROC-AUC: 0.xxxx
PR-AUC: 0.xxxx
```

### Step 6: Start API Server

Open a **new PowerShell window**:

```powershell
cd D:\cybersecurity\PCAE
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this window open!**

### Step 7: Start Dashboard

Open **another new PowerShell window**:

```powershell
cd D:\cybersecurity\PCAE
streamlit run dashboard/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

The dashboard will open automatically in your browser!

---

## Verification Checklist

After completing the setup, verify everything works:

- [ ] **API Server Running**: Visit http://localhost:8000/docs - Should show API documentation
- [ ] **API Health Check**: Visit http://localhost:8000/health - Should show `"model_loaded": true`
- [ ] **Dashboard Running**: Visit http://localhost:8501 - Should show security dashboard
- [ ] **Model File Exists**: Check `models/xgboost_model.pkl` exists
- [ ] **Data Files Exist**: Check `data/features/train.csv` and `test.csv` exist

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```powershell
pip install -r ..\requirements.txt
```

### Issue: "Model not loaded" in dashboard

**Solution:** Make sure you completed Step 5 (train_model.py):
```powershell
python src/train_model.py
```

### Issue: API won't start (Port 8000 already in use)

**Solution:** Use a different port:
```powershell
python -m uvicorn api.main:app --reload --port 8001
```

Then update `API_URL` in `dashboard/app.py` to `http://localhost:8001`

### Issue: Dashboard can't connect to API

**Solution:**
1. Make sure API server is running (Step 6)
2. Check `API_URL` in `dashboard/app.py` matches your API port
3. Verify API health: http://localhost:8000/health

### Issue: Data generation fails

**Solution:**
1. Check you have write permissions in the `data/` folder
2. Verify Python version: `python --version` (should be 3.8+)
3. Make sure all dependencies are installed

### Issue: Low model performance

**Solution:**
1. Check data quality in `data/features/train.csv`
2. Review feature engineering in `src/feature_engineering.py`
3. Try adjusting model hyperparameters in `config/config.yaml`

---

## Project Structure

```
PCAE/
├── api/                    # FastAPI REST API
│   ├── main.py            # API endpoints
│   └── models.py          # API data models
├── dashboard/              # Streamlit Dashboard
│   └── app.py             # Dashboard UI
├── src/                    # Source code
│   ├── create_sample_data.py
│   ├── preprocess.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   └── evaluate_model.py
├── data/                   # Data files
│   ├── raw/               # Raw input data
│   ├── processed/         # Preprocessed data
│   └── features/          # ML features
├── models/                 # Trained models
├── config/                 # Configuration
│   └── config.yaml
├── setup.py               # Setup script
├── quick_start.py         # Quick pipeline script
└── start_all.ps1          # Start services script
```

---

## What's Next?

Once everything is running:

1. **Explore the Dashboard**:
   - View asset risk scores
   - Check detailed predictions
   - See SHAP feature explanations

2. **Test the API**:
   - Visit http://localhost:8000/docs
   - Try the `/predict` endpoint
   - List all assets with `/assets`

3. **Customize**:
   - Edit `config/config.yaml` for settings
   - Modify feature engineering in `src/feature_engineering.py`
   - Adjust model parameters in `src/train_model.py`

4. **Add Real Data**:
   - Replace sample data with real network logs
   - Format according to schemas in README.md

---

## Quick Reference Commands

```powershell
# Full setup (first time)
python setup.py
python quick_start.py
.\start_all.ps1

# Or manually:
python src/create_sample_data.py
python src/preprocess.py
python src/feature_engineering.py
python src/train_model.py

# Start services
python -m uvicorn api.main:app --reload
streamlit run dashboard/app.py
```

---

## Need Help?

1. Check the main `README.md` for detailed documentation
2. Review `STEP_BY_STEP_GUIDE.md` for more details
3. Check error messages - they usually point to the solution
4. Verify all files exist in the expected locations

---

**Happy Hacking! 🚀**

