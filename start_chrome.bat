@echo off
echo Force closing all Chrome processes...
taskkill /F /IM chrome.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting Chrome with remote debugging enabled...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223

echo Chrome launched! You can now run the Python script.
exit
