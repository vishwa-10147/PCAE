# Step-by-Step Guide to Start PCAE Project

This guide will walk you through setting up and running the Predictive Cyber Attack Engine from scratch.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Step 1: Navigate to Project Directory

```bash
cd PCAE
```

## Step 2: Install Dependencies

### Option A: Using the Setup Script (Recommended)

```bash
python setup.py
```

This will:
- Check Python version
- Create necessary directories
- Install all required packages

### Option B: Manual Installation

1. Create virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

## Step 3: Create Sample Data

If you don't have real data yet, create sample data for testing:

```bash
python src/create_sample_data.py
```

This creates:
- `data/raw/sample_netflow.csv` - Sample network flow data
- `data/raw/incidents.csv` - Sample attack incidents
- `data/raw/assets.csv` - Sample asset inventory

**Alternative:** If you have real data, place it in `data/raw/` directory with appropriate naming.

## Step 4: Preprocess Data

This step aggregates raw data into time windows:

```bash
python src/preprocess.py --input data/raw/ --output data/processed/
```

**What it does:**
- Loads netflow/log data
- Creates time windows (default: 1 hour)
- Aggregates features per asset per window
- Creates labels from incidents
- Saves processed data to `data/processed/processed_data.csv`

**Output:**
- `data/processed/processed_data.csv` - Time-windowed aggregated data
- `data/processed/assets.csv` - List of monitored assets

## Step 5: Feature Engineering

Create temporal and static features for modeling:

```bash
python src/feature_engineering.py --input data/processed/ --output data/features/
```

**What it does:**
- Creates static features (OS, CVEs, services, criticality)
- Creates temporal features (rolling statistics, trends)
- Creates derived features (anomaly scores, risk scores)
- Splits data into train/test sets

**Output:**
- `data/features/train.csv` - Training features
- `data/features/test.csv` - Test features

## Step 6: Train Model

Train the XGBoost baseline model:

```bash
python src/train_model.py --data data/features/ --output models/
```

**What it does:**
- Loads training features
- Trains XGBoost classifier with class weighting
- Evaluates on validation set
- Saves model and metrics

**Output:**
- `models/xgboost_model.pkl` - Trained model
- `models/model_info.json` - Model metadata and feature names
- `models/evaluation_metrics.png` - Evaluation plots

**Expected output:**
```
Model Evaluation Metrics
==================================================
Accuracy: 0.xxxx
ROC-AUC: 0.xxxx
PR-AUC: 0.xxxx
Precision: 0.xxxx
Recall: 0.xxxx
F1-Score: 0.xxxx
```

## Step 7: (Optional) Evaluate Model on Test Set

Evaluate the trained model on held-out test data:

```bash
python src/evaluate_model.py --model models/xgboost_model.pkl --test data/features/test.csv
```

## Step 8: Start API Server

In a new terminal window (keep the virtual environment activated):

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify API is running:**
- Open browser: http://localhost:8000/docs
- You should see the FastAPI interactive documentation

**API Endpoints:**
- `GET /health` - Health check
- `GET /assets` - List all assets
- `POST /predict` - Get prediction for an asset

## Step 9: Start Dashboard

In another new terminal window (keep the virtual environment activated):

```bash
cd dashboard
streamlit run app.py
```

The dashboard will automatically open in your browser at: http://localhost:8501

**Dashboard Features:**
- Asset Overview: View all assets with risk scores
- Asset Details: Detailed view with SHAP explanations
- Trends: Time-series visualization (placeholder)

## Step 10: Quick Start (Alternative)

For a faster setup, use the quick start script:

```bash
python quick_start.py
```

This automatically runs steps 3-6 (data creation through model training).

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r ../requirements.txt
```

### Issue: API can't load model

**Solution:** 
1. Ensure model is trained: `python src/train_model.py`
2. Check model path in `config/config.yaml`
3. Verify `models/xgboost_model.pkl` exists

### Issue: Dashboard can't connect to API

**Solution:**
1. Ensure API server is running (Step 8)
2. Check API URL in dashboard sidebar (default: http://localhost:8000)
3. Verify API health: http://localhost:8000/health

### Issue: No data available

**Solution:**
1. Run `python src/create_sample_data.py` to create sample data
2. Or place your own data in `data/raw/` directory
3. Ensure data files are CSV format with required columns

### Issue: Low model performance

**Solution:**
1. Check data quality and labels
2. Adjust model hyperparameters in `config/config.yaml`
3. Review feature engineering logic in `src/feature_engineering.py`
4. Try different window sizes for aggregation

## Next Steps

Once everything is running:

1. **Customize Configuration:**
   - Edit `config/config.yaml` to adjust settings
   - Modify thresholds, window sizes, model parameters

2. **Add Real Data:**
   - Replace sample data with real network logs
   - Format data according to schemas in README.md

3. **Improve Model:**
   - Experiment with different features
   - Try sequence models (LSTM/GRU) for Phase B
   - Implement graph neural networks for Phase C

4. **Enhance Dashboard:**
   - Add real-time log streaming
   - Implement alert notifications
   - Add more visualizations

5. **Production Deployment:**
   - Dockerize the application
   - Set up CI/CD pipeline
   - Add monitoring and logging
   - Implement authentication

## Project Structure Reference

```
PCAE/
├── api/                    # FastAPI REST API
│   └── main.py
├── dashboard/              # Streamlit dashboard
│   └── app.py
├── src/                    # Source code
│   ├── preprocess.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── create_sample_data.py
│   └── utils.py
├── data/
│   ├── raw/               # Raw input data
│   ├── processed/         # Preprocessed data
│   └── features/          # Engineered features
├── models/                # Trained models
├── config/                # Configuration files
│   └── config.yaml
├── setup.py               # Setup script
├── quick_start.py         # Quick start script
└── README.md              # Main documentation
```

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review error messages carefully
3. Verify all dependencies are installed
4. Ensure data files are in correct format

Happy coding! 🛡️

