@echo off
title HarvestIQ (AgroPredict) First-Time Setup
echo ======================================================
echo    Setting up HarvestIQ for First-Time Run...
echo ======================================================

echo [1/4] Installing Backend Node Dependencies...
cd backend
call npm install
cd ..

echo [2/4] Installing Frontend Node Dependencies...
cd frontend
call npm install
cd ..

echo [3/4] Setting up Python Virtual Environment & Installing ML Packages...
cd ml
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo [4/4] Creating Environment Files...
if not exist "backend\.env" (
    echo PORT=5000 > backend\.env
    echo MONGODB_URI=mongodb+srv://kunaalveera17_db_user:0QkPU847rDQdt084@harvestiq-db.dnmvebu.mongodb.net/harvestiq?retryWrites=true^&w=majority >> backend\.env
    echo ML_SERVICE_URL=http://localhost:5001 >> backend\.env
    echo GEMINI_API_KEY=AIzaSyDl4jor8NZv666NG5p8tn-oyY6GG9TNKT8 >> backend\.env
    echo GOOGLE_API_KEY=AIzaSyDl4jor8NZv666NG5p8tn-oyY6GG9TNKT8 >> backend\.env
    echo Created backend\.env
)

if not exist "ml\.env" (
    echo PORT=5001 > ml\.env
    echo GEMINI_API_KEY=AIzaSyDl4jor8NZv666NG5p8tn-oyY6GG9TNKT8 >> ml\.env
    echo GOOGLE_API_KEY=AIzaSyDl4jor8NZv666NG5p8tn-oyY6GG9TNKT8 >> ml\.env
    echo Created ml\.env
)

echo ======================================================
echo    SETUP COMPLETE! Double-click start.bat to run!
echo ======================================================
pause
