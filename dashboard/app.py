"""Streamlit dashboard for Predictive Cyber Attack Engine."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from utils import load_config

# Page configuration
st.set_page_config(
    page_title="Predictive Cyber Attack Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
config = load_config()
DEFAULT_API_URL = config.get('api_url', 'http://localhost:8000')
THRESHOLD_HIGH = config.get('threshold_high', 0.7)
THRESHOLD_MEDIUM = config.get('threshold_medium', 0.4)


@st.cache_data
def fetch_assets(api_url: str):
    """Fetch list of assets from API."""
    try:
        response = requests.get(f"{api_url}/assets", timeout=5)
        if response.status_code == 200:
            return response.json().get('assets', [])
    except Exception as e:
        st.warning(f"Could not connect to API: {e}")
        # Fallback: load from local file
        assets_file = Path('data/processed/assets.csv')
        if assets_file.exists():
            df = pd.read_csv(assets_file)
            return [{"asset_ip": ip} for ip in df['asset_ip'].unique()]
    return []


def fetch_prediction(asset_ip: str, api_url: str, time_window_start: str = None):
    """Fetch prediction for an asset."""
    if time_window_start is None:
        time_window_start = datetime.now().isoformat()
    
    try:
        response = requests.post(
            f"{api_url}/predict",
            json={
                "asset_ip": asset_ip,
                "time_window_start": time_window_start
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching prediction: {e}")
        return None


def get_risk_color(probability: float) -> str:
    """Get color based on risk probability."""
    if probability >= THRESHOLD_HIGH:
        return "#FF0000"  # Red
    elif probability >= THRESHOLD_MEDIUM:
        return "#FFA500"  # Orange
    else:
        return "#00FF00"  # Green


def main():
    st.title("🛡️ Predictive Cyber Attack Engine")
    st.markdown("---")
    
    # Initialize session state for API URL
    if 'api_url' not in st.session_state:
        st.session_state.api_url = DEFAULT_API_URL
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        api_url = st.text_input("API URL", value=st.session_state.api_url)
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.cache_data.clear()
        
        st.markdown("---")
        st.header("Risk Thresholds")
        threshold_high = st.slider("High Risk", 0.0, 1.0, THRESHOLD_HIGH, 0.05)
        threshold_medium = st.slider("Medium Risk", 0.0, 1.0, THRESHOLD_MEDIUM, 0.05)
        
        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Get API URL from session state
    api_url = st.session_state.api_url
    
    # Health check
    try:
        health_response = requests.get(f"{api_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            if health_data.get('model_loaded'):
                st.success("✅ API Connected - Model Loaded")
            else:
                st.warning("⚠️ API Connected - Model Not Loaded")
        else:
            st.error("❌ API Health Check Failed")
    except:
        st.error("❌ Cannot Connect to API")
        st.info("Please ensure the API server is running on the configured URL")
        return
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Asset Overview", "🔍 Asset Details", "📈 Trends"])
    
    with tab1:
        st.header("Asset Risk Overview")
        
        assets = fetch_assets(api_url)
        
        if not assets:
            st.warning("No assets found. Please ensure data preprocessing is complete.")
            return
        
        # Fetch predictions for all assets
        predictions = []
        with st.spinner("Fetching predictions..."):
            for asset in assets[:20]:  # Limit to 20 for performance
                asset_ip = asset.get('asset_ip', '')
                pred = fetch_prediction(asset_ip, api_url)
                if pred:
                    predictions.append(pred)
        
        if not predictions:
            st.warning("No predictions available. Please check API connection and model status.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(predictions)
        df = df.sort_values('probability', ascending=False)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Assets", len(df))
        with col2:
            high_risk = (df['probability'] >= threshold_high).sum()
            st.metric("High Risk Assets", high_risk, delta=None if high_risk == 0 else f"+{high_risk}")
        with col3:
            medium_risk = ((df['probability'] >= threshold_medium) & (df['probability'] < threshold_high)).sum()
            st.metric("Medium Risk Assets", medium_risk)
        with col4:
            avg_risk = df['probability'].mean()
            st.metric("Average Risk", f"{avg_risk:.2%}")
        
        st.markdown("---")
        
        # Asset list with risk scores
        st.subheader("Asset Risk Scores")
        
        # Create visualization
        fig = go.Figure()
        
        for _, row in df.iterrows():
            color = get_risk_color(row['probability'])
            fig.add_trace(go.Bar(
                x=[row['asset']],
                y=[row['probability']],
                marker_color=color,
                text=f"{row['probability']:.2%}",
                textposition='auto',
                name=row['asset']
            ))
        
        fig.update_layout(
            title="Attack Probability by Asset",
            xaxis_title="Asset IP",
            yaxis_title="Attack Probability",
            yaxis=dict(range=[0, 1]),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Detailed Asset List")
        display_df = df[['asset', 'probability', 'recommended_action']].copy()
        display_df['probability'] = display_df['probability'].apply(lambda x: f"{x:.2%}")
        display_df.columns = ['Asset IP', 'Attack Probability', 'Recommended Action']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.header("Asset Details & Explainability")
        
        assets = fetch_assets(api_url)
        if not assets:
            st.warning("No assets available.")
            return
        
        asset_ips = [a.get('asset_ip', '') for a in assets]
        selected_asset = st.selectbox("Select Asset", asset_ips)
        
        if selected_asset:
            with st.spinner("Fetching prediction and explanation..."):
                pred = fetch_prediction(selected_asset, api_url)
            
            if pred:
                # Risk score display
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    probability = pred['probability']
                    risk_color = get_risk_color(probability)
                    
                    st.metric(
                        "Attack Probability",
                        f"{probability:.2%}",
                        delta=None
                    )
                    
                    # Risk level indicator
                    if probability >= threshold_high:
                        st.error("🔴 HIGH RISK")
                    elif probability >= threshold_medium:
                        st.warning("🟠 MEDIUM RISK")
                    else:
                        st.success("🟢 LOW RISK")
                    
                    st.markdown("---")
                    st.subheader("Recommended Action")
                    st.info(pred['recommended_action'])
                
                with col2:
                    # SHAP waterfall plot (simplified)
                    if pred.get('top_features'):
                        st.subheader("Top Contributing Features")
                        
                        features_df = pd.DataFrame(pred['top_features'])
                        features_df = features_df.sort_values('contribution', key=abs, ascending=False)
                        
                        # Bar chart
                        fig = px.bar(
                            features_df,
                            x='contribution',
                            y='feature',
                            orientation='h',
                            title="Feature Contributions (SHAP values)",
                            labels={'contribution': 'Contribution to Prediction', 'feature': 'Feature'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Table
                        st.dataframe(features_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Feature contributions not available")
                
                # Recent activity (placeholder)
                st.markdown("---")
                st.subheader("Recent Activity")
                st.info("Recent log samples would be displayed here. "
                       "This requires integration with a log storage system.")
            else:
                st.error("Could not fetch prediction for selected asset")
    
    with tab3:
        st.header("Risk Trends")
        
        st.info("Time-series visualization would be displayed here. "
               "This requires historical prediction data storage.")
        
        # Placeholder for time series
        dates = pd.date_range(end=datetime.now(), periods=24, freq='1H')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'probability': np.random.uniform(0.1, 0.9, 24)
        })
        
        fig = px.line(
            sample_data,
            x='timestamp',
            y='probability',
            title="Attack Probability Trend (Sample Data)",
            labels={'probability': 'Attack Probability', 'timestamp': 'Time'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
