@echo off
REM SWAM MIDI Player Launcher
REM Starts Python WebSocket server and opens HTML player in browser

echo.
echo ========================================
echo   SWAM MIDI Player
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
python -c "import websockets; import mido" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Installing required packages...
    pip install websockets
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Dependencies ready
echo.

REM Start Python server (HTTP + WebSocket) in background
echo Starting MIDI server (HTTP + WebSocket)...
echo Server will stay running until you close this window
echo.
start /MIN "SWAM MIDI Server" python scripts\midi_websocket_server.py

REM Wait for server to initialize
timeout /t 3 /nobreak >nul

REM Open HTML player in Chrome (not Edge)
echo Opening player in Chrome...
echo.

REM Try to find and launch Chrome
set "CHROME_PATH="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%LocalAppData%\Google\Chrome\Application\chrome.exe"
)

if defined CHROME_PATH (
    start "" "%CHROME_PATH%" http://localhost:8000/swam_violin_player_v2.html
    echo [OK] Chrome opened
) else (
    echo [WARNING] Chrome not found, opening default browser...
    echo           If it opens Edge, Edge may not support Web MIDI properly.
    echo           Please install Chrome or manually open in Chrome.
    start http://localhost:8000/swam_violin_player_v2.html
)

echo.
echo ========================================
echo   SWAM MIDI Player is running!
echo ========================================
echo.
echo   URL: http://localhost:8000/swam_violin_player_v2.html
echo.
echo   If "No MIDI output found" appears:
echo     1. Make sure you're using Chrome (not Edge)
echo     2. Refresh the page (F5)
echo.
echo   To STOP the server:
echo     - Close this window, OR
echo     - Find "SWAM MIDI Server" window and close it
echo.
echo ========================================
echo.
echo Press any key to stop the server...
pause >nul

echo.
echo Stopping server...
taskkill /FI "WINDOWTITLE eq SWAM MIDI Server*" /F >nul 2>&1
echo Server stopped.
timeout /t 2 /nobreak >nul
echo ========================================
echo.

REM Keep window open (server runs in background)
pause

REM Cleanup: Kill Python server when user closes
taskkill /FI "WINDOWTITLE eq midi_websocket_server*" /F >nul 2>&1
echo.
echo Server stopped. Goodbye!
