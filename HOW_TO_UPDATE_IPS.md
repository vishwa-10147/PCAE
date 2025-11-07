# 📍 How to Update IP Addresses - Complete Guide

## 🔍 What IP Addresses Does This System Monitor?

**This system monitors NETWORK ASSETS (servers, devices, computers) - NOT emails.**

The system tracks:
- ✅ **Server IP addresses** (e.g., `192.168.1.100`, `10.0.0.50`)
- ✅ **Device IP addresses** (workstations, IoT devices)
- ✅ **Network infrastructure** (routers, switches with IPs)

The system does **NOT** monitor:
- ❌ Email addresses
- ❌ Email content
- ❌ Email servers (unless you add their IP as an asset)

---

## 📂 Where IP Addresses Are Stored

The system reads IP addresses from these files:

### Primary Location:
**`data/processed/assets.csv`** - This is the main file the system uses

### Source Files:
1. **`data/raw/assets.csv`** - Original asset inventory (created by data generator)
2. **`data/processed/assets.csv`** - Processed assets (used by API and Dashboard)

---

## 🔧 How to Update/Change IP Addresses

### Method 1: Edit the Assets CSV File (Recommended)

**Step 1:** Open the assets file:
```powershell
# Navigate to the file
cd D:\cybersecurity\PCAE
notepad data\processed\assets.csv
```

**Step 2:** Edit the file. It should look like this:
```csv
asset_ip
192.168.1.100
192.168.1.101
192.168.1.102
10.0.0.50
10.0.0.51
```

**Step 3:** Add or remove IP addresses:
```csv
asset_ip
192.168.1.100
192.168.1.101
192.168.1.102
10.0.0.50
10.0.0.51
172.16.0.10    ← Add your new IP here
172.16.0.11    ← Add another IP here
```

**Step 4:** Save the file and refresh the dashboard

---

### Method 2: Edit the Source Data File

**Step 1:** Edit the raw assets file:
```powershell
notepad data\raw\assets.csv
```

**Step 2:** The file should have more details:
```csv
asset_ip,os,services,cves,patch_status,criticality
192.168.1.100,Windows Server 2019,RDP,HTTP,HTTPS,CVE-2023-1234,outdated,high
192.168.1.101,Ubuntu 20.04,SSH,HTTP,HTTPS,CVE-2023-9012,current,medium
...
```

**Step 3:** Add your new assets with all required fields:
```csv
asset_ip,os,services,cves,patch_status,criticality
192.168.1.100,Windows Server 2019,RDP,HTTP,HTTPS,CVE-2023-1234,outdated,high
172.16.0.10,Linux,SSH,HTTP,MySQL,,current,high    ← Add your new IP
```

**Step 4:** Re-run preprocessing:
```powershell
python src/preprocess.py
```

---

### Method 3: Modify the Data Generator Script

If you want to permanently change which IPs are generated:

**Step 1:** Open the script:
```powershell
notepad src\create_sample_data.py
```

**Step 2:** Find line 18 (around line 18-25) and modify:
```python
# Original:
assets = ['192.168.1.100', '192.168.1.101', '192.168.1.102', '10.0.0.50', '10.0.0.51']

# Change to your IPs:
assets = ['192.168.1.100', '172.16.0.10', '172.16.0.11', '10.0.0.50', '10.0.0.51', 'YOUR_IP_HERE']
```

**Step 3:** Also update the asset inventory (around line 81-122):
```python
assets = [
    {
        'asset_ip': '192.168.1.100',  # Keep existing
        'os': 'Windows Server 2019',
        ...
    },
    {
        'asset_ip': '172.16.0.10',  # Add your new IP
        'os': 'Linux',
        'services': 'SSH,HTTP',
        'cves': '',
        'patch_status': 'current',
        'criticality': 'high'
    },
    # Add more assets...
]
```

**Step 4:** Regenerate data:
```powershell
python src/create_sample_data.py
python src/preprocess.py
```

---

## 📋 Current IP Addresses Being Monitored

Based on your current setup, these IPs are being monitored:

1. `192.168.1.100` - Windows Server 2019
2. `192.168.1.101` - Ubuntu 20.04
3. `192.168.1.102` - Windows 10
4. `10.0.0.50` - CentOS 7
5. `10.0.0.51` - Debian 11
6. `0.0.0.0` - (This might be an error, you may want to remove it)

---

## 🎯 Quick Steps to Add Your Real IP Addresses

### Option A: Quick Add (Just IPs)

1. Open `data/processed/assets.csv`
2. Add your IP addresses (one per line):
   ```csv
   asset_ip
   192.168.1.100
   172.16.0.10    ← Your new IP
   172.16.0.11    ← Another new IP
   ```
3. Save and refresh dashboard

### Option B: Complete Add (With Details)

1. Open `data/raw/assets.csv`
2. Add complete asset information:
   ```csv
   asset_ip,os,services,cves,patch_status,criticality
   172.16.0.10,Linux,SSH,HTTP,MySQL,,current,high
   ```
3. Run: `python src/preprocess.py`
4. Refresh dashboard

---

## 🔄 After Updating IPs - What to Do

1. **If you edited `data/processed/assets.csv` directly:**
   - Just refresh the dashboard (click "🔄 Refresh Data" button)
   - The new IPs should appear immediately

2. **If you edited `data/raw/assets.csv`:**
   - Run preprocessing: `python src/preprocess.py`
   - Refresh the dashboard

3. **If you modified the generator script:**
   - Regenerate data: `python src/create_sample_data.py`
   - Run preprocessing: `python src/preprocess.py`
   - Refresh the dashboard

---

## 📊 How the System Uses IP Addresses

1. **Dashboard** reads from `data/processed/assets.csv` to show which assets to monitor
2. **API** uses the same file to list available assets
3. **Predictions** are made for each IP address in the assets file
4. **Network flow data** must include these IPs as `dst_ip` (destination IP) to generate predictions

---

## ⚠️ Important Notes

### IP Address Format
- Must be valid IPv4 format (e.g., `192.168.1.100`)
- IPv6 not currently supported
- No spaces or special characters

### Network Flow Data
- For predictions to work, your network flow data (`data/raw/sample_netflow.csv`) must contain traffic **TO** these IP addresses
- The `dst_ip` column in netflow data should match your asset IPs

### Example Netflow Entry:
```csv
timestamp,src_ip,dst_ip,src_port,dst_port,bytes,protocol,flag
2024-01-15 10:00:00,10.0.0.1,192.168.1.100,54321,80,1500,TCP,SYN
```
Here, `192.168.1.100` is the monitored asset (must be in assets.csv)

---

## 🛠️ Troubleshooting

### Problem: New IP doesn't appear in dashboard

**Solution:**
1. Check the IP is in `data/processed/assets.csv`
2. Make sure the file is saved
3. Click "🔄 Refresh Data" in dashboard
4. Check API: `http://localhost:8000/assets` - should list your IPs

### Problem: No predictions for new IP

**Solution:**
1. Make sure network flow data includes this IP as `dst_ip`
2. Regenerate data if needed: `python src/create_sample_data.py`
3. Re-run preprocessing: `python src/preprocess.py`

### Problem: Invalid IP address error

**Solution:**
- Check IP format (must be valid IPv4)
- No spaces, no special characters
- Example: `192.168.1.100` ✅ (correct)
- Example: `192.168.1.100 ` ❌ (has space)
- Example: `192.168.1` ❌ (incomplete)

---

## 📝 Example: Adding Your Company's Servers

Let's say you want to monitor:
- Web Server: `172.16.10.50`
- Database Server: `172.16.10.51`
- File Server: `172.16.10.52`

**Step 1:** Edit `data/processed/assets.csv`:
```csv
asset_ip
172.16.10.50
172.16.10.51
172.16.10.52
```

**Step 2:** Make sure your network flow data includes traffic to these IPs

**Step 3:** Refresh dashboard - you'll see these 3 new assets!

---

## 🎓 Summary

- **What it monitors:** Network asset IP addresses (servers, devices)
- **Where IPs are stored:** `data/processed/assets.csv`
- **How to update:** Edit the CSV file or modify the generator script
- **Not for emails:** This system doesn't check email addresses

**Quick Update:**
1. Open `data/processed/assets.csv`
2. Add your IP addresses
3. Save and refresh dashboard
4. Done! ✅

