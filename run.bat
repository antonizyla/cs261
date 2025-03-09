@echo off
setlocal

:: Check if "venv" folder exists
if not exist venv (
    echo No venv found, creating one
    python -m venv venv

    echo Activating venv
    call venv\Scripts\activate

    echo Installing requirements
    pip install -r frontend\requirements.txt
    pip install -r backend\requirements.txt
) else (
    echo Activating venv
    call venv\Scripts\activate
)

echo Starting application
python frontend\frontend.py

echo Deactivating venv
deactivate

endlocal