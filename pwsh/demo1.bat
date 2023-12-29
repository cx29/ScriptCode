@echo off

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "https://www.baidu.com"

timeout /t 5 /nobreak >nul

wscript "./test.vbs"
