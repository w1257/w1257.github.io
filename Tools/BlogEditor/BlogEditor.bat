@echo off

SET VENV_DIR=.venv
SET PYTHON_SCRIPT=BlogEditor.py

REM --- Main Logic ---

REM Check if the virtual environment is already active in the parent shell
IF DEFINED VIRTUAL_ENV (
    REM Venv IS active: Run script and leave it active.
    ECHO Venv already active. Running script...
    ECHO.
    python %PYTHON_SCRIPT%
) ELSE (
    REM Venv is NOT active: Activate, run script, and ensure deactivation.
    ECHO Venv not active. Activating for temporary use...
    
    REM 1. Activate the venv
    CALL %VENV_DIR%\Scripts\activate.bat

    REM 2. Use a "fake" call to a second batch file to ensure the script runs 
    REM    within a disposable environment.
    IF EXIST %VENV_DIR%\Scripts\python.exe (
        ECHO Running Python script...
        ECHO.
        
        REM Start a new CMD instance to run the Python script.
        REM When this inner CMD instance closes, the venv deactivates naturally.
        REM /C means "carry out command and then terminate"
        start "" /B /WAIT cmd /C "python %PYTHON_SCRIPT%"

    ) ELSE (
        ECHO Error: Virtual environment not found or activation failed.
    )
    REM The 'deactivate' command is technically not required here 
    REM because the changes were isolated by the 'start cmd /C' sub-shell trick, 
    REM but it's good practice to try and clean up the current script's environment.
    deactivate
    ECHO.
    ECHO Deactivated temporary virtual environment.
)