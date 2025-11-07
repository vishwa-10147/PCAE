"""Create sample data for testing and demonstration."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from utils import ensure_dir


def create_sample_netflow(output_file: str, n_records: int = 10000):
    """Create sample netflow data."""
    print(f"Creating sample netflow data with {n_records} records...")
    
    start_date = datetime.now() - timedelta(days=7)
    timestamps = pd.date_range(start_date, periods=n_records, freq='1min')
    
    # Define assets
    assets = ['192.168.1.100', '192.168.1.101', '192.168.1.102', '10.0.0.50', '10.0.0.51', '93.184.216.34','23.227.38.65', '142.251.10.26']
    
    # Normal traffic
    normal_data = {
        'timestamp': timestamps[:int(n_records * 0.9)],
        'src_ip': [f'10.0.{np.random.randint(0,255)}.{np.random.randint(1,255)}' 
                  for _ in range(int(n_records * 0.9))],
        'dst_ip': np.random.choice(assets, int(n_records * 0.9)),
        'src_port': np.random.randint(1024, 65535, int(n_records * 0.9)),
        'dst_port': np.random.choice([22, 80, 443, 3389, 8080], int(n_records * 0.9)),
        'bytes': np.random.randint(100, 10000, int(n_records * 0.9)),
        'protocol': np.random.choice(['TCP', 'UDP'], int(n_records * 0.9)),
        'flag': np.random.choice(['SYN', 'ACK', 'FIN'], int(n_records * 0.9))
    }
    
    # Attack traffic (port scans, brute force)
    attack_start = int(n_records * 0.85)
    attack_data = {
        'timestamp': timestamps[attack_start:],
        'src_ip': [f'172.16.{np.random.randint(0,255)}.{np.random.randint(1,255)}' 
                  for _ in range(len(timestamps[attack_start:]))],
        'dst_ip': np.random.choice(assets[:2], len(timestamps[attack_start:])),  # Target specific assets
        'src_port': np.random.randint(1024, 65535, len(timestamps[attack_start:])),
        'dst_port': np.random.choice([22, 3389, 80], len(timestamps[attack_start:])),  # Common attack ports
        'bytes': np.random.randint(50, 500, len(timestamps[attack_start:])),
        'protocol': ['TCP'] * len(timestamps[attack_start:]),
        'flag': ['SYN'] * len(timestamps[attack_start:])  # Many SYN packets
    }
    
    df_normal = pd.DataFrame(normal_data)
    df_attack = pd.DataFrame(attack_data)
    df = pd.concat([df_normal, df_attack], ignore_index=True)
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    df.to_csv(output_file, index=False)
    print(f"Sample netflow data saved to {output_file}")


def create_sample_incidents(output_file: str):
    """Create sample incident labels."""
    print("Creating sample incident data...")
    
    start_date = datetime.now() - timedelta(days=5)
    incidents = []
    
    # Create incidents during attack periods
    for i in range(10):
        incident_time = start_date + timedelta(days=i*0.5, hours=np.random.randint(10, 20))
        incidents.append({
            'incident_ts': incident_time,
            'dst_ip': np.random.choice(['192.168.1.100', '192.168.1.101']),
            'attack_type': np.random.choice(['port_scan', 'brute_force', 'data_exfil'])
        })
    
    df = pd.DataFrame(incidents)
    df.to_csv(output_file, index=False)
    print(f"Sample incidents saved to {output_file}")


def create_sample_assets(output_file: str):
    """Create sample asset inventory."""
    print("Creating sample asset inventory...")
    
    assets = [
        {
            'asset_ip': '192.168.1.100',
            'os': 'Windows Server 2019',
            'services': 'RDP,HTTP,HTTPS',
            'cves': 'CVE-2023-1234,CVE-2023-5678',
            'patch_status': 'outdated',
            'criticality': 'high'
        },
        {
            'asset_ip': '192.168.1.101',
            'os': 'Ubuntu 20.04',
            'services': 'SSH,HTTP,HTTPS',
            'cves': 'CVE-2023-9012',
            'patch_status': 'current',
            'criticality': 'medium'
        },
        {
            'asset_ip': '192.168.1.102',
            'os': 'Windows 10',
            'services': 'RDP',
            'cves': '',
            'patch_status': 'current',
            'criticality': 'low'
        },
        {
            'asset_ip': '10.0.0.50',
            'os': 'CentOS 7',
            'services': 'SSH,HTTP',
            'cves': 'CVE-2023-3456',
            'patch_status': 'outdated',
            'criticality': 'medium'
        },
        {
            'asset_ip': '10.0.0.51',
            'os': 'Debian 11',
            'services': 'SSH,HTTP,HTTPS,MySQL',
            'cves': '',
            'patch_status': 'current',
            'criticality': 'critical'
        },
        {
            'asset_ip': '93.184.216.34',
            'os': 'Linux',
            'services': 'HTTP,HTTPS',
            'cves': '',
            'patch_status': 'current',
            'criticality': 'high'
        },
        {
            'asset_ip': '23.227.38.65',
            'os': 'Linux',
            'services': 'HTTP,HTTPS',
            'cves': '',
            'patch_status': 'current',
            'criticality': 'high'
        },
        {
            'asset_ip': '142.251.10.26',
            'os': 'Linux',
            'services': 'HTTP,HTTPS',
            'cves': '',
            'patch_status': 'current',
            'criticality': 'high'
        }
    ]
    
    df = pd.DataFrame(assets)
    df.to_csv(output_file, index=False)
    print(f"Sample asset inventory saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Create sample data for PCAE')
    parser.add_argument('--output', type=str, default='data/raw/',
                       help='Output directory for sample data')
    parser.add_argument('--records', type=int, default=10000,
                       help='Number of netflow records to generate')
    
    args = parser.parse_args()
    
    ensure_dir(args.output)
    
    # Create sample data files
    create_sample_netflow(Path(args.output) / 'sample_netflow.csv', args.records)
    create_sample_incidents(Path(args.output) / 'incidents.csv')
    create_sample_assets(Path(args.output) / 'assets.csv')
    
    print("\n" + "="*50)
    print("Sample data creation complete!")
    print("="*50)
    print(f"\nFiles created in {args.output}:")
    print("  - sample_netflow.csv")
    print("  - incidents.csv")
    print("  - assets.csv")
    print("\nNext steps:")
    print("  1. Run: python src/preprocess.py")
    print("  2. Run: python src/feature_engineering.py")
    print("  3. Run: python src/train_model.py")


if __name__ == '__main__':
    main()

