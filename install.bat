@echo off
setlocal

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...

    set "PYTHON_INSTALLER=https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe"
    set "INSTALLER_NAME=python-3.12.5-amd64.exe"

    powershell -Command "Invoke-WebRequest -Uri %PYTHON_INSTALLER% -OutFile %INSTALLER_NAME%"

    start /wait %INSTALLER_NAME% /quiet InstallAllUsers=1 PrependPath=1

    del %INSTALLER_NAME%
) else (
    echo Python is already installed.
)

endlocal

echo Installing required Python libraries...
pip install pip install pyftpdlib
