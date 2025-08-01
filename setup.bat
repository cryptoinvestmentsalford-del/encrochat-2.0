@echo off
echo Setting up Platinum Secure Flasher environment...

REM Create necessary directories
mkdir license 2>nul
mkdir logs 2>nul
mkdir assets 2>nul

REM Check for ADB
adb version >nul 2>&1
if errorlevel 1 (
    echo WARNING: ADB not found in PATH
    echo Please install Android SDK Platform Tools
    echo Download from: https://developer.android.com/studio/releases/platform-tools
)

REM Check for Fastboot
fastboot --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Fastboot not found in PATH
    echo Please install Android SDK Platform Tools
)

echo Setup complete!
echo Run platinum_secure_flasher.py to start the application
pause