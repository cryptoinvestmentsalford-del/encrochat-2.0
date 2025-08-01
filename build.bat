@echo off
echo Building Platinum Secure Flasher...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install pyinstaller

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --name "PlatinumSecureFlasher" platinum_secure_flasher.py

REM Copy assets to dist folder
echo Copying assets...
xcopy /E /I scripts dist\scripts
xcopy /E /I assets dist\assets
mkdir dist\license
mkdir dist\logs

echo Build complete! Executable is in the dist folder.
pause