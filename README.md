# Predictive Cyber Attack Engine (PCAE)

A Machine Learning system that predicts cyber attack probabilities for network assets using historical telemetry data, vulnerability information, and threat intelligence.

## 🎯 Project Overview

This system:
- Consumes historical attack/telemetry data + service/vulnerability data
- Outputs Attack Probability Scores per asset/network segment
- Provides a dashboard visualizing predicted hotspots and suggested mitigations

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Git** (optional) - For version control

### Required Python Packages
All dependencies are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd PCAE

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Generate Synthetic Data

Since you may not have real network data initially, the project includes a synthetic data generator:

```bash
python src/data_generator.py
```

This will create:
- `data/netflow.csv` - Network flow data with attack patterns
- `data/incidents.csv` - Attack incident timestamps
- `data/asset_inventory.csv` - Asset information with vulnerabilities

### Step 3: Create Features

Extract and engineer features from the network data:

```bash
python src/feature_engineering.py
```

This generates:
- `data/features.csv` - Engineered features for model training

### Step 4: Train the Model

Train the XGBoost classifier:

```bash
python src/train_model.py
```

This will:
- Train the model on your features
- Evaluate performance (AUC-ROC, AUC-PR)
- Save the model to `models/xgboost_model.pkl`
- Create SHAP explainer for interpretability

### Step 5: Start the API Server

Start the FastAPI backend:

```bash
# From the PCAE directory
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
cd api
python main.py
```

The API will be available at `http://localhost:8000`

### Step 6: Launch the Dashboard

In a new terminal, start the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

Or:

```bash
cd dashboard
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
PCAE/
├── data/                   # Data files (CSV)
│   ├── netflow.csv        # Network flow data
│   ├── incidents.csv      # Attack incidents
│   ├── asset_inventory.csv # Asset information
│   └── features.csv        # Engineered features
├── notebooks/             # Jupyter notebooks for EDA
├── models/                # Trained models
│   ├── xgboost_model.pkl
│   ├── shap_explainer.pkl
│   └── feature_columns.pkl
├── api/                   # FastAPI backend
│   └── main.py
├── dashboard/             # Streamlit dashboard
│   └── app.py
├── src/                   # Source code
│   ├── data_generator.py  # Synthetic data generation
│   ├── feature_engineering.py # Feature extraction
│   └── train_model.py     # Model training
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### API Configuration
- Default API URL: `http://localhost:8000`
- Can be changed in `dashboard/app.py` (line 11)

### Model Configuration
- Window size: 1 hour (can be changed in `feature_engineering.py`)
- Model: XGBoost Classifier
- Evaluation metrics: AUC-ROC, AUC-PR, Precision, Recall

## 📊 Features

### Static Features
- OS type
- Open service ports
- Number of known CVEs
- Patch age (days)
- Asset criticality

### Temporal Features
- Unique source IPs
- Failed login counts
- SSH connection counts
- HTTP error counts
- Network flow bytes (in/out)
- Connection entropy
- Port scan indicators
- Previous attack counts

### Derived Features
- Trend slopes
- Rolling statistics
- Time-based features (hour, day of week)

## 🎯 Usage Examples

### Using the API

#### Get prediction for an asset:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_ip": "192.168.1.1",
    "time_window_start": "2024-01-01T12:00:00"
  }'
```

#### List all assets:
```bash
curl http://localhost:8000/assets
```

#### Get batch predictions:
```bash
curl http://localhost:8000/predictions/batch
```

### Using Python

```python
import requests

# Get prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "asset_ip": "192.168.1.1",
        "time_window_start": "2024-01-01T12:00:00"
    }
)
prediction = response.json()
print(f"Attack probability: {prediction['probability']:.2%}")
```

## 📈 Model Evaluation

The model is evaluated using:
- **AUC-ROC**: Area under ROC curve
- **AUC-PR**: Area under Precision-Recall curve (better for imbalanced data)
- **Precision/Recall/F1**: Classification metrics
- **Confusion Matrix**: True/False positives/negatives

## 🛡️ Security Considerations

- Uses synthetic data for demos (no real PII)
- Anonymizes IPs in example data
- Predictions are probabilistic and require human verification
- No real credentials or sensitive data in demo

## 🔮 Future Enhancements

- [ ] Real-time streaming with Kafka
- [ ] Graph Neural Networks for lateral movement detection
- [ ] LSTM/GRU for sequence modeling
- [ ] Integration with SIEM systems
- [ ] Automated mitigation playbooks
- [ ] Email/Slack alerting
- [ ] Docker containerization

## 🐛 Troubleshooting

### Model not loading
- Make sure you've run `train_model.py` first
- Check that files exist in `models/` directory

### API connection errors
- Ensure API server is running on port 8000
- Check firewall settings
- Verify API_URL in dashboard code

### Data generation issues
- Ensure you have write permissions in `data/` directory
- Check Python version (3.8+ required)

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path if using custom directories

## 📚 Resources

- **Datasets**: CICIDS2017, UNSW-NB15, CIC-IDS2018
- **Documentation**: See `PredictiveCyberAttackEngine.txt` for detailed specifications
- **XGBoost**: https://xgboost.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **SHAP**: https://shap.readthedocs.io/

## 👥 Contributing

This is a hackathon/project template. Feel free to:
- Add new features
- Improve model performance
- Enhance the dashboard
- Add more data sources

## 📄 License

This project is for educational/demonstration purposes.

## 🎓 Learning Path

1. **Data Understanding**: Explore the generated synthetic data
2. **Feature Engineering**: Understand how features are created
3. **Model Training**: Learn about XGBoost and imbalanced data handling
4. **API Development**: Build REST APIs with FastAPI
5. **Visualization**: Create interactive dashboards with Streamlit

## ✨ Tips for Hackathon

1. **Start Simple**: Use XGBoost baseline first
2. **Focus on Demo**: Ensure end-to-end flow works
3. **Show Explainability**: Use SHAP to show "why" predictions
4. **Prepare Scenario**: Have a synthetic attack scenario ready
5. **Document Everything**: README, code comments, demo script

---

**Happy Hacking! 🚀**

For questions or issues, refer to the main specification document: `PredictiveCyberAttackEngine.txt`
