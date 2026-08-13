# PowerShell script to run the Samarth Aushadhalay project
# Run this from the project root: d:\Projects\samarth_aushadhalay\samarth_aushadhalay

Write-Host "Setting up virtual environment..."
python -m venv .venv
.venv\Scripts\activate

Write-Host "Upgrading pip..."
pip install -U pip

Write-Host "Installing requirements..."
pip install -r backend\requirements.txt

Write-Host "Creating database..."
python backend\create_db.py

Write-Host "Inserting sample data..."
python backend\insert_products.py

Write-Host "Starting Flask app..."
python backend\app.py