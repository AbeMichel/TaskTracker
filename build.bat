@echo off
REM Clean previous build/dist folders
rmdir /s /q build
rmdir /s /q dist

REM Remove previous spec file
if exist "Task Tracker.spec" del "Task Tracker.spec"

REM Run PyInstaller
pyinstaller --onefile --noconsole --name "Task Tracker" main.py

pause
