# 🚀 How to Run This Project - Fixed Guide

## ❌ What Went Wrong

The errors you saw were caused by:
1. **PowerShell script using CMD syntax** (`cd /d` doesn't work in PowerShell)
2. **Wrong directory for running commands** - API and Dashboard must run from the **PCAE root directory**, not from inside their folders

## ✅ Correct Way to Run

### Option 1: Use the Fixed PowerShell Script

The script has been fixed. Run it from the PCAE directory:

```powershell
cd D:\cybersecurity\PCAE
.\start_all.ps1
```

This will open two new PowerShell windows with the services running.

---

### Option 2: Manual Start (Recommended for First Time)

Open **TWO separate PowerShell windows** and run these commands:

#### Window 1 - API Server:
```powershell
cd D:\cybersecurity\PCAE
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Important:** Run from `PCAE` directory, NOT from `api` directory!

#### Window 2 - Dashboard:
```powershell
cd D:\cybersecurity\PCAE
streamlit run dashboard/app.py
```

**Important:** Run from `PCAE` directory, NOT from `dashboard` directory!

---

## 📍 Where to See Everything

Once both services are running:

### 1. **API Documentation** (Interactive)
- **URL:** http://localhost:8000/docs
- **What you'll see:** Interactive API documentation where you can test endpoints
- **Features:** Try the `/predict`, `/assets`, `/health` endpoints

### 2. **API Health Check**
- **URL:** http://localhost:8000/health
- **What you'll see:** JSON response showing if the model is loaded
- **Example response:**
  ```json
  {
    "status": "healthy",
    "model_loaded": true,
    "version": "1.0.0"
  }
  ```

### 3. **Dashboard** (Main Interface)
- **URL:** http://localhost:8501
- **What you'll see:** Interactive web dashboard with:
  - Asset risk scores
  - Attack probability predictions
  - SHAP feature explanations
  - Risk visualization charts

### 4. **API Root**
- **URL:** http://localhost:8000
- **What you'll see:** JSON response with API information

---

## 🔍 Understanding the Project Structure

```
PCAE/
├── api/
│   ├── main.py          ← API server code
│   └── models.py        ← API data models
├── dashboard/
│   └── app.py           ← Dashboard UI code
├── src/                 ← Core ML code
├── models/              ← Trained models (created after training)
├── data/                ← Data files (created after data generation)
└── start_all.ps1        ← Script to start both services
```

**Key Point:** Both `api.main:app` and `dashboard/app.py` are referenced from the **PCAE root directory**, not from inside their folders.

---

## 🛠️ Step-by-Step First Time Setup

### Step 1: Install Dependencies
```powershell
cd D:\cybersecurity\PCAE
python setup.py
```

### Step 2: Generate Data and Train Model
```powershell
python quick_start.py
```

Wait for it to complete. You should see:
- ✅ Data created
- ✅ Features engineered
- ✅ Model trained with metrics

### Step 3: Start Services

**Method A - Use Script:**
```powershell
.\start_all.ps1
```

**Method B - Manual (Two Windows):**

**Window 1:**
```powershell
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Window 2:**
```powershell
streamlit run dashboard/app.py
```

### Step 4: Access the Application

1. Open browser to **http://localhost:8501** (Dashboard)
2. Open **http://localhost:8000/docs** (API docs) in another tab

---

## 🐛 Troubleshooting

### Error: "Could not import module 'main'"

**Cause:** Running from wrong directory

**Fix:** Make sure you're in `D:\cybersecurity\PCAE` directory, NOT in `api` or `dashboard` folders

```powershell
# Check your current directory
pwd

# Should show: D:\cybersecurity\PCAE
# If not, run:
cd D:\cybersecurity\PCAE
```

### Error: "File does not exist: app.py"

**Cause:** Running from wrong directory

**Fix:** Run from PCAE root:
```powershell
cd D:\cybersecurity\PCAE
streamlit run dashboard/app.py
```

### Error: "Model not loaded"

**Cause:** Model hasn't been trained yet

**Fix:** Run the training first:
```powershell
python quick_start.py
```

### Port Already in Use

**For API (port 8000):**
```powershell
python -m uvicorn api.main:app --reload --port 8001
```

**For Dashboard (port 8501):**
```powershell
streamlit run dashboard/app.py --server.port 8502
```

---

## 📊 What Each Service Does

### API Server (Port 8000)
- Provides REST API endpoints
- Serves predictions from the trained model
- Handles SHAP explanations
- Returns JSON responses

**Endpoints:**
- `GET /health` - Health check
- `GET /assets` - List all assets
- `POST /predict` - Get prediction for an asset
- `GET /docs` - Interactive API documentation

### Dashboard (Port 8501)
- Web-based user interface
- Visualizes risk scores
- Shows feature contributions
- Interactive charts and graphs
- Connects to API for data

---

## ✅ Verification Checklist

After starting both services, verify:

- [ ] API window shows: `Uvicorn running on http://0.0.0.0:8000`
- [ ] Dashboard window shows: `You can now view your Streamlit app`
- [ ] Browser opens to http://localhost:8501 automatically
- [ ] http://localhost:8000/docs shows API documentation
- [ ] http://localhost:8000/health returns `"model_loaded": true`

---

## 🎯 Quick Reference

```powershell
# Full setup (first time only)
cd D:\cybersecurity\PCAE
python setup.py
python quick_start.py

# Start services (every time you want to use the app)
# Option 1: Use script
.\start_all.ps1

# Option 2: Manual (two windows)
# Window 1:
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Window 2:
streamlit run dashboard/app.py
```

---

## 📱 Access Points Summary

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:8501 | Main user interface |
| **API Docs** | http://localhost:8000/docs | Interactive API testing |
| **API Health** | http://localhost:8000/health | Service status check |
| **API Root** | http://localhost:8000 | API information |

---

**Remember:** Always run commands from `D:\cybersecurity\PCAE` directory, not from subdirectories!

