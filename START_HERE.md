# 🚀 START HERE - Quick Setup Guide

## What You Need

### 1. **Python 3.8 or Higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

### 2. **Internet Connection**
   - Required to download Python packages

### 3. **Text Editor/IDE** (Optional but recommended)
   - VS Code, PyCharm, or any code editor

## 📦 Step-by-Step Setup (5-10 minutes)

### Step 1: Install Python Packages

Open PowerShell/Terminal in the `PCAE` directory and run:

```bash
pip install -r requirements.txt
```

**This will install:**
- pandas, numpy (data processing)
- xgboost (machine learning)
- fastapi, uvicorn (API server)
- streamlit (dashboard)
- shap (explainability)
- plotly (visualizations)

**Expected time: 2-5 minutes**

---

### Step 2: Generate Data

Run the data generator:

```bash
python src/data_generator.py
```

**This creates:**
- `data/netflow.csv` - Network traffic data with attack patterns
- `data/incidents.csv` - Attack incident records
- `data/asset_inventory.csv` - Asset information

**Expected time: 30 seconds - 2 minutes**

---

### Step 3: Create Features

Extract features from the data:

```bash
python src/feature_engineering.py
```

**This creates:**
- `data/features.csv` - Engineered features for ML

**Expected time: 10-30 seconds**

---

### Step 4: Train the Model

Train the attack prediction model:

```bash
python src/train_model.py
```

**This creates:**
- `models/xgboost_model.pkl` - Trained model
- `models/shap_explainer.pkl` - Explainability tool
- `models/feature_columns.pkl` - Feature metadata

**Expected time: 1-3 minutes**

You'll see evaluation metrics like:
- AUC-ROC score
- AUC-PR score
- Classification report

---

### Step 5: Start the API Server

Open a **new terminal/PowerShell window** and run:

```bash
cd PCAE
python -m uvicorn api.main:app --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal open!**

**Test the API:** Open http://localhost:8000 in your browser. You should see API documentation.

---

### Step 6: Launch the Dashboard

Open **another new terminal/PowerShell window** and run:

```bash
cd PCAE
streamlit run dashboard/app.py
```

**You should see:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

**The dashboard will open automatically in your browser!**

---

## ✅ Quick Check: Is Everything Working?

1. **API Server**: Visit http://localhost:8000 - Should show API docs
2. **Dashboard**: Visit http://localhost:8501 - Should show security dashboard
3. **Health Check**: Visit http://localhost:8000/health - Should show `"model_loaded": true`

---

## 🎯 What You Can Do Now

### In the Dashboard:
- **Dashboard Tab**: See risk scores for all assets
- **Asset Details**: Get detailed risk analysis for specific assets
- **Threat Analysis**: View risk trends and alerts

### Using the API:
- Get predictions for any asset
- List all assets
- Get batch predictions

---

## 🐛 Troubleshooting

### "Module not found" errors
**Solution:** Run `pip install -r requirements.txt` again

### "Model not loaded" in dashboard
**Solution:** Make sure you completed Step 4 (train_model.py)

### API won't start
**Solution:** 
- Check if port 8000 is already in use
- Try: `python -m uvicorn api.main:app --reload --port 8001`
- Then update `API_URL` in `dashboard/app.py` to `http://localhost:8001`

### Dashboard can't connect to API
**Solution:**
- Make sure API server is running (Step 5)
- Check `API_URL` in `dashboard/app.py` matches your API port

### Data generation fails
**Solution:**
- Make sure you have write permissions in the `data/` folder
- Check Python version: `python --version` (should be 3.8+)

---

## 📚 Next Steps

1. **Explore the Data**: Look at `data/netflow.csv` to understand the structure
2. **Experiment with Models**: Modify `src/train_model.py` to try different parameters
3. **Customize Dashboard**: Edit `dashboard/app.py` to add new visualizations
4. **Add Real Data**: Replace synthetic data with real network logs

---

## 🎓 Understanding the Project

### How It Works:
1. **Data Layer**: Network flows, incidents, asset inventory
2. **Feature Engineering**: Extract temporal and static features
3. **Model Training**: XGBoost learns attack patterns
4. **Prediction API**: FastAPI serves predictions
5. **Dashboard**: Streamlit visualizes results

### Key Files:
- `src/data_generator.py` - Creates synthetic attack data
- `src/feature_engineering.py` - Extracts ML features
- `src/train_model.py` - Trains the prediction model
- `api/main.py` - REST API for predictions
- `dashboard/app.py` - Interactive web dashboard

---

## 💡 Pro Tips

1. **Use the Quick Setup Script**: 
   ```bash
   python run_project.py
   ```
   This automates steps 2-4!

2. **Monitor Model Performance**: Check `models/feature_importance.csv` to see which features matter most

3. **Customize Attack Patterns**: Edit `src/data_generator.py` to create different attack scenarios

4. **Improve Predictions**: Modify feature engineering in `src/feature_engineering.py`

---

## 📞 Need Help?

1. Check the main `README.md` for detailed documentation
2. Review `PredictiveCyberAttackEngine.txt` for project specifications
3. Check error messages - they usually point to the solution

---

## ✨ You're All Set!

Once you see the dashboard running, you've successfully set up the Predictive Cyber Attack Engine!

**Happy Hacking! 🚀**

---

*Last updated: 2024*

