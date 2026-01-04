@echo off
echo 🚀 Starting Job Radar ID Setup (Windows)...

:: 1. Check Venv
IF EXIST "venv" (
    echo ✅ Virtual Environment found.
) ELSE (
    echo 📦 Creating new Virtual Environment...
    python -m venv venv
)

:: 2. Activate & Install
echo ⬇️  Installing Dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

echo 🎉 Setup Complete! 
echo Type "venv\Scripts\activate" to start coding.
pause