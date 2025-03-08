@echo off
echo Creating virtual environment...
python -m venv dutyflow-env

echo Activating virtual environment...
call dutyflow-env\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete! Virtual environment 'dutyflow-env' is now active.
echo To activate this environment in the future, run: dutyflow-env\Scripts\activate 