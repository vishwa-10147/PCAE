"""
Auto-run script: runs pipeline, then launches API and Dashboard.
Windows-friendly (opens API and Dashboard in new consoles).
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent


def run_quick_start() -> bool:
	print("=" * 60)
	print("Running quick_start.py (data -> preprocess -> features -> train)")
	print("=" * 60)
	proc = subprocess.run([sys.executable, str(ROOT / "quick_start.py")])
	return proc.returncode == 0


def start_api() -> subprocess.Popen:
	api_dir = ROOT / "api"
	cmd = f"cd /d {api_dir} && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
	print("Starting API server...")
	return subprocess.Popen(
		["powershell", "-NoExit", "-Command", cmd],
		creationflags=subprocess.CREATE_NEW_CONSOLE
	)


def start_dashboard() -> subprocess.Popen:
	db_dir = ROOT / "dashboard"
	cmd = f"cd /d {db_dir} && streamlit run app.py"
	print("Starting Dashboard...")
	return subprocess.Popen(
		["powershell", "-NoExit", "-Command", cmd],
		creationflags=subprocess.CREATE_NEW_CONSOLE
	)


def main():
	os.chdir(ROOT)
	ok = run_quick_start()
	if not ok:
		print("quick_start failed. Fix errors above, then re-run this script.")
		sys.exit(1)
	api_proc = start_api()
	db_proc = start_dashboard()
	print("\nAPI and Dashboard launched in new windows.")
	print("API: http://localhost:8000/docs")
	print("Dashboard: http://localhost:8501")
	print("\nPress Ctrl+C here to exit (services continue in their own consoles).")
	try:
		api_proc.wait()
		db_proc.wait()
	except KeyboardInterrupt:
		print("Exiting controller. API/Dashboard remain open in their consoles.")


if __name__ == "__main__":
	main()
