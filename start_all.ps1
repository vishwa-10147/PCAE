# Starts API and Dashboard. Optionally runs the pipeline first.
param(
	[switch]$RunPipeline
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if ($RunPipeline) {
	Write-Host "Running quick_start.py ..." -ForegroundColor Cyan
	python "$Root\quick_start.py"
}

# Start API (must run from PCAE root directory)
$apiCmd = "Set-Location `"$Root`"; python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process -FilePath powershell -ArgumentList "-NoExit", "-Command", $apiCmd
Write-Host "API started at http://localhost:8000" -ForegroundColor Green

# Start Dashboard (must run from PCAE root directory)
$dbCmd = "Set-Location `"$Root`"; streamlit run dashboard/app.py"
Start-Process -FilePath powershell -ArgumentList "-NoExit", "-Command", $dbCmd
Write-Host "Dashboard started at http://localhost:8501" -ForegroundColor Green

Write-Host "Both services launched in new windows." -ForegroundColor Yellow
Write-Host "`nAccess:" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Dashboard: http://localhost:8501" -ForegroundColor White
