$chromePath="C:\Program Files\Google\Chrome\Application\chrome.exe"

$url="https://www.baidu.com"

Start-Process $chromePath -ArgumentList "--start-maximized", $url

Start-Sleep -Seconds 1

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('{F11}')
