@echo off
REM Simple SWAM MIDI Player Launcher

echo Starting server...
start /MIN "SWAM Server" python scripts\midi_websocket_server.py
timeout /t 3 /nobreak >nul

echo Opening browser...
start chrome http://localhost:8000/swam_violin_player_v2.html

echo.
echo Server running! Press any key to stop...
pause >nul

taskkill /FI "WINDOWTITLE eq SWAM Server*" /F >nul 2>&1
