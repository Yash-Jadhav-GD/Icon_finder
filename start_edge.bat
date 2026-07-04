@echo off
echo Force closing Edge...
taskkill /F /IM msedge.exe >nul 2>&1

echo Starting Edge with remote debugging enabled...
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9223

echo Edge launched! You can now run the Python script.
exit
