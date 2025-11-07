"""
Synthetic Data Generator for Predictive Cyber Attack Engine
Generates realistic network telemetry and attack patterns for demo purposes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_network_data(n_assets=10, days=30, attacks_per_day=2):
    """
    Generate synthetic network flow data with attack patterns
    
    Args:
        n_assets: Number of assets to simulate
        days: Number of days of data
        attacks_per_day: Average number of attacks per day
    """
    np.random.seed(42)
    random.seed(42)
    
    # Generate asset IPs
    base_ip = "192.168.1."
    assets = [f"{base_ip}{i}" for i in range(1, n_assets + 1)]
    
    # Generate time range
    start_time = datetime.now() - timedelta(days=days)
    end_time = datetime.now()
    
    # Generate normal traffic
    normal_flows = []
    current_time = start_time
    
    # External IPs (potential attackers)
    external_ips = [f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" 
                    for _ in range(100)]
    
    # Generate normal traffic
    while current_time < end_time:
        # Normal traffic: 5-20 flows per hour per asset
        flows_per_hour = np.random.randint(5, 20)
        
        for _ in range(flows_per_hour):
            src_ip = random.choice(external_ips + assets)
            dst_ip = random.choice(assets)
            
            # Normal traffic characteristics
            if src_ip in external_ips:
                # External to internal (normal web browsing, API calls)
                dst_port = random.choice([80, 443, 22, 3389])
                bytes_transferred = np.random.randint(1000, 100000)
                protocol = random.choice(['TCP', 'UDP'])
                flag = 'SYN' if protocol == 'TCP' else 'NONE'
                
                # Small chance of failed login (normal)
                failed_login = random.random() < 0.05
            else:
                # Internal to internal (normal)
                dst_port = random.choice([80, 443, 3306, 5432, 8080])
                bytes_transferred = np.random.randint(5000, 500000)
                protocol = 'TCP'
                flag = 'SYN'
                failed_login = False
            
            normal_flows.append({
                'timestamp': current_time + timedelta(minutes=random.randint(0, 59)),
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': random.randint(1024, 65535),
                'dst_port': dst_port,
                'bytes': bytes_transferred,
                'protocol': protocol,
                'flag': flag,
                'failed_login': failed_login,
                'attack': 0
            })
        
        current_time += timedelta(hours=1)
    
    # Generate attack traffic
    attack_flows = []
    attack_times = []
    
    for _ in range(int(days * attacks_per_day)):
        attack_time = start_time + timedelta(
            days=random.randint(0, days-1),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        target_asset = random.choice(assets)
        attacker_ip = random.choice(external_ips)
        attack_type = random.choice(['brute_force', 'port_scan', 'dos', 'data_exfil'])
        
        if attack_type == 'brute_force':
            # Many failed login attempts
            for i in range(50, 200):
                attack_flows.append({
                    'timestamp': attack_time + timedelta(seconds=i*2),
                    'src_ip': attacker_ip,
                    'dst_ip': target_asset,
                    'src_port': random.randint(1024, 65535),
                    'dst_port': 22,  # SSH
                    'bytes': np.random.randint(100, 1000),
                    'protocol': 'TCP',
                    'flag': 'SYN',
                    'failed_login': True,
                    'attack': 1
                })
        
        elif attack_type == 'port_scan':
            # Scan many ports
            ports_to_scan = random.sample(range(1, 1024), 50)
            for i, port in enumerate(ports_to_scan):
                attack_flows.append({
                    'timestamp': attack_time + timedelta(seconds=i),
                    'src_ip': attacker_ip,
                    'dst_ip': target_asset,
                    'src_port': random.randint(1024, 65535),
                    'dst_port': port,
                    'bytes': np.random.randint(50, 500),
                    'protocol': 'TCP',
                    'flag': 'SYN',
                    'failed_login': False,
                    'attack': 1
                })
        
        elif attack_type == 'dos':
            # High volume of requests
            for i in range(1000):
                attack_flows.append({
                    'timestamp': attack_time + timedelta(seconds=i*0.1),
                    'src_ip': attacker_ip,
                    'dst_ip': target_asset,
                    'src_port': random.randint(1024, 65535),
                    'dst_port': 80,
                    'bytes': np.random.randint(100, 1000),
                    'protocol': 'TCP',
                    'flag': 'SYN',
                    'failed_login': False,
                    'attack': 1
                })
        
        elif attack_type == 'data_exfil':
            # Large data transfers
            for i in range(10):
                attack_flows.append({
                    'timestamp': attack_time + timedelta(minutes=i),
                    'src_ip': target_asset,
                    'dst_ip': attacker_ip,
                    'src_port': random.randint(1024, 65535),
                    'dst_port': random.randint(1024, 65535),
                    'bytes': np.random.randint(1000000, 10000000),
                    'protocol': 'TCP',
                    'flag': 'ACK',
                    'failed_login': False,
                    'attack': 1
                })
        
        attack_times.append({
            'incident_ts': attack_time,
            'dst_ip': target_asset,
            'attack_type': attack_type
        })
    
    # Combine flows
    all_flows = normal_flows + attack_flows
    df_flows = pd.DataFrame(all_flows)
    df_flows = df_flows.sort_values('timestamp').reset_index(drop=True)
    
    # Create incidents dataframe
    df_incidents = pd.DataFrame(attack_times)
    df_incidents['incident_ts'] = pd.to_datetime(df_incidents['incident_ts'])
    
    return df_flows, df_incidents, assets

def generate_asset_inventory(assets):
    """Generate asset inventory with vulnerabilities"""
    asset_data = []
    
    os_list = ['Linux', 'Windows Server 2019', 'Windows 10', 'Ubuntu 20.04', 'CentOS 7']
    services = {
        'Linux': ['SSH', 'HTTP', 'MySQL'],
        'Windows Server 2019': ['RDP', 'IIS', 'MSSQL'],
        'Windows 10': ['RDP', 'SMB'],
        'Ubuntu 20.04': ['SSH', 'HTTP', 'PostgreSQL'],
        'CentOS 7': ['SSH', 'HTTP', 'MySQL']
    }
    
    for asset_ip in assets:
        os_type = random.choice(os_list)
        asset_data.append({
            'asset_ip': asset_ip,
            'os': os_type,
            'services': ', '.join(services[os_type]),
            'open_ports': ','.join([str(p) for p in random.sample([22, 80, 443, 3389, 3306, 5432], 3)]),
            'num_cves': random.randint(0, 5),
            'patch_age_days': random.randint(0, 90),
            'asset_criticality': random.choice(['Low', 'Medium', 'High', 'Critical'])
        })
    
    return pd.DataFrame(asset_data)

if __name__ == "__main__":
    print("Generating synthetic network data...")
    df_flows, df_incidents, assets = generate_synthetic_network_data(n_assets=10, days=30)
    
    print(f"Generated {len(df_flows)} network flows")
    print(f"Generated {len(df_incidents)} attack incidents")
    print(f"Assets: {assets}")
    
    # Save to CSV
    df_flows.to_csv('PCAE/data/netflow.csv', index=False)
    df_incidents.to_csv('PCAE/data/incidents.csv', index=False)
    
    # Generate asset inventory
    df_inventory = generate_asset_inventory(assets)
    df_inventory.to_csv('PCAE/data/asset_inventory.csv', index=False)
    
    print("\nData saved to:")
    print("  - PCAE/data/netflow.csv")
    print("  - PCAE/data/incidents.csv")
    print("  - PCAE/data/asset_inventory.csv")

