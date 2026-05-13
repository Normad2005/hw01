# setup_demo.ps1
Write-Host "Setting up Python virtual environment..."
python -m venv venv
& .\venv\Scripts\Activate.ps1

Write-Host "Installing requirements..."
pip install -r requirements.txt

Write-Host "Starting Flask Backend on port 5000..."
Start-Process ".\venv\Scripts\python.exe" -ArgumentList "flask_backend.py" -WindowStyle Normal -PassThru

Write-Host "Starting ESP32 Simulator..."
Start-Process ".\venv\Scripts\python.exe" -ArgumentList "esp32_sim.py" -WindowStyle Normal -PassThru

Write-Host "Waiting 8 seconds for the simulator to send data..."
Start-Sleep -Seconds 8

Write-Host "Verifying SQLite database..."
.\venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect('aiotdb.db'); rows=c.execute('SELECT count(*) FROM sensor_data').fetchone()[0]; print(f'[Healthy] Database has {rows} rows.'); c.close()"

Write-Host "Starting Streamlit Frontend on port 8501..."
Start-Process ".\venv\Scripts\streamlit.exe" -ArgumentList "run streamlit_frontend.py" -WindowStyle Normal -PassThru

Write-Host "Setup complete. The demo components are running in separate windows."
