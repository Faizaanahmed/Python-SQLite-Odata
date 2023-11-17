@ECHO OFF
REM This script attempts to find Conda in common installation paths, create a new environment, and install requirements

REM Set the environment name and Python version
SET ENV_NAME=pythonOdata
SET PYTHON_VERSION=3.7

REM Attempt to find Conda in common installation paths
SET CONDA_PATH=
IF EXIST "C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat" SET CONDA_PATH=C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat
IF EXIST "C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat" SET CONDA_PATH=C:\Users\%USERNAME%\miniconda3\Scripts\activate.bat
IF EXIST "C:\Anaconda3\Scripts\activate.bat" SET CONDA_PATH=C:\Anaconda3\Scripts\activate.bat
IF EXIST "C:\Miniconda3\Scripts\activate.bat" SET CONDA_PATH=C:\Miniconda3\Scripts\activate.bat

IF "%CONDA_PATH%"=="" (
    ECHO Conda executable not found. Please ensure Conda is installed.
    PAUSE
    EXIT
)

REM Find requirements.txt in the current directory
SET REQUIREMENTS_PATH=%~dp0requirements.txt
IF NOT EXIST "%REQUIREMENTS_PATH%" (
    ECHO requirements.txt not found in the current directory.
    PAUSE
    EXIT
)

REM Activate Conda and create a new environment
CALL "%CONDA_PATH%" && conda create --name %ENV_NAME% python=%PYTHON_VERSION% -y

REM Activate the new environment and install requirements
CALL conda activate %ENV_NAME% && pip install -r %REQUIREMENTS_PATH%

REM Any additional setup commands can be added here

ECHO Environment setup complete.
PAUSE
