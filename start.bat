@echo off
echo ========================================
echo   Automated Book Generation System
echo ========================================
echo.

echo 🔄 Step 1: Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found!
    echo 📝 Please run: python -m venv venv
    pause
    exit /b 1
)

echo.
echo 🔄 Step 2: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo 🔄 Step 3: Starting the system...
echo 🚀 This will set up the database and start the server
echo.
python start.py

pause
