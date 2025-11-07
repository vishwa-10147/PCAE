"""Feature engineering for PCAE."""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from utils import ensure_dir, load_config, calculate_entropy, safe_divide


def load_asset_inventory(file_path: str) -> pd.DataFrame:
    """Load asset inventory with static features."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Warning: Could not load asset inventory: {e}")
        return pd.DataFrame()


def create_static_features(asset_inventory: pd.DataFrame) -> pd.DataFrame:
    """Create static features from asset inventory."""
    if asset_inventory.empty:
        # Create default static features if no inventory
        return pd.DataFrame()
    
    static_features = asset_inventory.copy()
    
    # Encode categorical features
    if 'os' in static_features.columns:
        static_features['os_encoded'] = pd.Categorical(static_features['os']).codes
    else:
        static_features['os_encoded'] = 0
    
    # Count CVEs
    if 'cves' in static_features.columns:
        static_features['cve_count'] = static_features['cves'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) else 0
        )
    else:
        static_features['cve_count'] = 0
    
    # Count services
    if 'services' in static_features.columns:
        static_features['service_count'] = static_features['services'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) else 0
        )
    else:
        static_features['service_count'] = 0
    
    # Encode criticality
    if 'criticality' in static_features.columns:
        criticality_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        static_features['criticality_encoded'] = static_features['criticality'].map(
            criticality_map
        ).fillna(1)
    else:
        static_features['criticality_encoded'] = 1
    
    return static_features[['asset_ip', 'os_encoded', 'cve_count', 
                           'service_count', 'criticality_encoded']]


def create_temporal_features(df: pd.DataFrame, window_size: str = '1H') -> pd.DataFrame:
    """Create temporal features from time series data."""
    features = df.copy()
    
    # Group by asset and sort by window
    features = features.sort_values(['asset_ip', 'window'])
    
    # Basic temporal features
    features['avg_packet_size'] = features['total_bytes'] / (features['total_connections'] + 1)
    features['bytes_per_src_ip'] = features['total_bytes'] / (features['unique_src_ips'] + 1)
    features['connection_rate'] = features['total_connections']
    
    # Calculate rolling statistics (last 3 windows)
    for asset in features['asset_ip'].unique():
        asset_mask = features['asset_ip'] == asset
        asset_data = features[asset_mask].sort_values('window')
        
        # Rolling means
        features.loc[asset_mask, 'rolling_unique_src_ips'] = asset_data['unique_src_ips'].rolling(
            window=3, min_periods=1
        ).mean().values
        
        features.loc[asset_mask, 'rolling_total_bytes'] = asset_data['total_bytes'].rolling(
            window=3, min_periods=1
        ).mean().values
        
        # Rolling standard deviations (anomaly indicators)
        features.loc[asset_mask, 'rolling_std_src_ips'] = asset_data['unique_src_ips'].rolling(
            window=3, min_periods=1
        ).std().fillna(0).values
        
        # Change from previous window
        features.loc[asset_mask, 'delta_unique_src_ips'] = asset_data['unique_src_ips'].diff().fillna(0).values
        features.loc[asset_mask, 'delta_total_bytes'] = asset_data['total_bytes'].diff().fillna(0).values
    
    # Time-based features
    features['hour_of_day'] = pd.to_datetime(features['window']).dt.hour
    features['day_of_week'] = pd.to_datetime(features['window']).dt.dayofweek
    features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
    
    # Ratio features
    features['syn_ratio'] = safe_divide(
        features.get('syn_count', 0),
        features['total_connections']
    )
    
    features['ports_per_connection'] = safe_divide(
        features['unique_dst_ports'],
        features['total_connections']
    )
    
    # Fill NaN values
    features = features.fillna(0)
    
    return features


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived/composite features."""
    features = df.copy()
    
    # Anomaly score (simple heuristic)
    features['anomaly_score'] = (
        (features['delta_unique_src_ips'] > features['rolling_unique_src_ips'] * 2).astype(int) +
        (features['delta_total_bytes'] > features['rolling_total_bytes'] * 2).astype(int) +
        (features['unique_dst_ports'] > 10).astype(int)
    ) / 3
    
    # Risk score (composite)
    features['risk_score'] = (
        features['unique_src_ips'] * 0.3 +
        features['unique_dst_ports'] * 0.2 +
        features['anomaly_score'] * 0.5
    )
    
    return features


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select final feature set for modeling."""
    # Static features (will be merged)
    static_cols = ['os_encoded', 'cve_count', 'service_count', 'criticality_encoded']
    
    # Temporal features
    temporal_cols = [
        'unique_src_ips', 'total_bytes', 'unique_dst_ports', 'total_connections',
        'rolling_unique_src_ips', 'rolling_total_bytes', 'rolling_std_src_ips',
        'delta_unique_src_ips', 'delta_total_bytes',
        'avg_packet_size', 'bytes_per_src_ip', 'connection_rate',
        'syn_ratio', 'ports_per_connection',
        'hour_of_day', 'day_of_week', 'is_weekend',
        'anomaly_score', 'risk_score'
    ]
    
    # Keep only available columns
    available_cols = [col for col in static_cols + temporal_cols if col in df.columns]
    
    # Keep metadata columns
    metadata_cols = ['window', 'asset_ip', 'label'] if 'label' in df.columns else ['window', 'asset_ip']
    
    return df[metadata_cols + available_cols]


def main():
    parser = argparse.ArgumentParser(description='Feature engineering for PCAE')
    parser.add_argument('--input', type=str, default='data/processed/',
                       help='Input directory with processed data')
    parser.add_argument('--output', type=str, default='data/features/',
                       help='Output directory for features')
    
    args = parser.parse_args()
    
    ensure_dir(args.output)
    config = load_config()
    
    # Load processed data
    processed_file = Path(args.input) / 'processed_data.csv'
    if not processed_file.exists():
        print(f"Error: Processed data not found at {processed_file}")
        print("Please run preprocess.py first")
        return
    
    df = pd.read_csv(processed_file)
    df['window'] = pd.to_datetime(df['window'])
    print(f"Loaded {len(df)} records")
    
    # Load asset inventory
    inventory_file = Path(args.input) / 'assets.csv'
    asset_inventory = load_asset_inventory(str(inventory_file))
    
    # Create static features
    if not asset_inventory.empty:
        static_features = create_static_features(asset_inventory)
        df = df.merge(static_features, on='asset_ip', how='left')
        df[['os_encoded', 'cve_count', 'service_count', 'criticality_encoded']] = \
            df[['os_encoded', 'cve_count', 'service_count', 'criticality_encoded']].fillna(0)
    else:
        # Add default static features
        df['os_encoded'] = 0
        df['cve_count'] = 0
        df['service_count'] = 0
        df['criticality_encoded'] = 1
    
    # Create temporal features
    df = create_temporal_features(df)
    
    # Create derived features
    df = create_derived_features(df)
    
    # Select final features
    df = select_features(df)
    
    # Split into train/test
    df = df.sort_values('window')
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    # Save features
    train_file = Path(args.output) / 'train.csv'
    test_file = Path(args.output) / 'test.csv'
    
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"Features saved:")
    print(f"  Train: {train_file} ({len(train_df)} records)")
    print(f"  Test: {test_file} ({len(test_df)} records)")
    print(f"  Feature count: {len(df.columns) - 3}")  # Exclude metadata columns


if __name__ == '__main__':
    main()
