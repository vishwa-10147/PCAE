"""Data preprocessing script for PCAE."""
import pandas as pd
import numpy as np
import argparse
import os
from pathlib import Path
from utils import ensure_dir, load_config


def load_netflow_data(file_path: str) -> pd.DataFrame:
    """Load netflow/log data from CSV file."""
    required_columns = ['timestamp', 'src_ip', 'dst_ip']
    
    try:
        df = pd.read_csv(file_path)
        
        # Check for required columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}, will create with defaults")
            for col in missing_cols:
                if col == 'timestamp':
                    df['timestamp'] = pd.date_range(start='2024-01-01', periods=len(df), freq='1min')
                else:
                    df[col] = '0.0.0.0'
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add default columns if missing
        if 'src_port' not in df.columns:
            df['src_port'] = 0
        if 'dst_port' not in df.columns:
            df['dst_port'] = 0
        if 'bytes' not in df.columns:
            df['bytes'] = 0
        if 'protocol' not in df.columns:
            df['protocol'] = 'TCP'
        if 'flag' not in df.columns:
            df['flag'] = 'SYN'
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()


def preprocess_netflow(df: pd.DataFrame, window_size: str = '1H') -> pd.DataFrame:
    """Preprocess netflow data into time windows."""
    df = df.sort_values('timestamp')
    
    # Create time windows
    df['window'] = df['timestamp'].dt.floor(window_size)
    
    # Aggregate by window and destination IP (asset)
    agg = df.groupby(['window', 'dst_ip']).agg({
        'src_ip': lambda s: s.nunique(),  # Unique source IPs
        'bytes': 'sum',  # Total bytes
        'dst_port': lambda s: s.nunique(),  # Unique destination ports
        'flag': lambda s: (s == 'SYN').sum(),  # SYN flags (connection attempts)
        'timestamp': 'count'  # Total connections
    }).reset_index()
    
    agg.columns = ['window', 'asset_ip', 'unique_src_ips', 'total_bytes', 
                   'unique_dst_ports', 'syn_count', 'total_connections']
    
    return agg


def load_incidents(file_path: str) -> pd.DataFrame:
    """Load incident/attack labels."""
    try:
        df = pd.read_csv(file_path)
        df['incident_ts'] = pd.to_datetime(df['incident_ts'])
        return df
    except Exception as e:
        print(f"Warning: Could not load incidents file: {e}")
        return pd.DataFrame(columns=['incident_ts', 'dst_ip', 'attack_type'])


def create_labels(agg_df: pd.DataFrame, incidents_df: pd.DataFrame, 
                  window_size: str = '1H') -> pd.DataFrame:
    """Create labels for each window/asset combination."""
    if incidents_df.empty:
        # If no incidents, create all zeros
        agg_df['label'] = 0
        return agg_df
    
    # Create window column for incidents
    incidents_df['window'] = incidents_df['incident_ts'].dt.floor(window_size)
    
    # Merge to create labels
    labeled_df = agg_df.merge(
        incidents_df[['window', 'dst_ip']].drop_duplicates(),
        left_on=['window', 'asset_ip'],
        right_on=['window', 'dst_ip'],
        how='left',
        indicator=True
    )
    
    labeled_df['label'] = (labeled_df['_merge'] == 'both').astype(int)
    labeled_df = labeled_df.drop(['_merge', 'dst_ip'], axis=1, errors='ignore')
    
    return labeled_df


def main():
    parser = argparse.ArgumentParser(description='Preprocess data for PCAE')
    parser.add_argument('--input', type=str, default='data/raw/', 
                       help='Input directory with raw data')
    parser.add_argument('--output', type=str, default='data/processed/',
                       help='Output directory for processed data')
    parser.add_argument('--window', type=str, default='1H',
                       help='Time window size (e.g., 1H, 24H)')
    
    args = parser.parse_args()
    
    ensure_dir(args.output)
    config = load_config()
    window_size = config.get('window_size', args.window)
    
    # Load netflow data
    netflow_files = list(Path(args.input).glob('*netflow*.csv')) + \
                   list(Path(args.input).glob('*.csv'))
    
    if not netflow_files:
        print(f"No CSV files found in {args.input}")
        print("Creating sample data structure...")
        # Create sample structure
        sample_df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=1000, freq='1min'),
            'src_ip': [f'10.0.{i%255}.{j%255}' for i, j in zip(range(1000), range(500, 1500))],
            'dst_ip': ['192.168.1.100'] * 1000,
            'src_port': np.random.randint(1024, 65535, 1000),
            'dst_port': np.random.choice([22, 80, 443, 3389], 1000),
            'bytes': np.random.randint(100, 10000, 1000),
            'protocol': np.random.choice(['TCP', 'UDP'], 1000),
            'flag': np.random.choice(['SYN', 'ACK', 'FIN'], 1000)
        })
        netflow_files = [Path(args.input) / 'sample_netflow.csv']
        sample_df.to_csv(netflow_files[0], index=False)
        print(f"Created sample data: {netflow_files[0]}")
    
    all_agg = []
    
    for file_path in netflow_files:
        print(f"Processing {file_path}...")
        df = load_netflow_data(str(file_path))
        if df.empty:
            continue
        agg = preprocess_netflow(df, window_size)
        all_agg.append(agg)
    
    if not all_agg:
        print("No data processed. Exiting.")
        return
    
    combined_agg = pd.concat(all_agg, ignore_index=True)
    
    # Load incidents if available
    incidents_file = Path(args.input) / 'incidents.csv'
    incidents_df = load_incidents(str(incidents_file)) if incidents_file.exists() else pd.DataFrame()
    
    # Create labels
    labeled_df = create_labels(combined_agg, incidents_df, window_size)
    
    # Save processed data
    output_file = Path(args.output) / 'processed_data.csv'
    labeled_df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    print(f"Total records: {len(labeled_df)}")
    print(f"Attack labels: {labeled_df['label'].sum()} ({labeled_df['label'].mean()*100:.2f}%)")
    
    # Save asset list
    asset_file = Path(args.output) / 'assets.csv'
    assets = labeled_df[['asset_ip']].drop_duplicates()
    assets.to_csv(asset_file, index=False)
    print(f"Asset list saved to {asset_file}")


if __name__ == '__main__':
    main()

