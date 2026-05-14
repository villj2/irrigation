# deploy.ps1 — Deploy watering_system_prod.py to Raspberry Pi
$PI_HOST = "vill@192.168.1.112"
$REMOTE_PATH = "/home/vill/Desktop/watering_system_prod.py"
$SCRIPT = "watering_system_prod.py"
$CREDENTIALS_PATH = "C:\Users\julie\OneDrive\Leisure\Irrigation\Mosquitto MQTT\credentials.json"
$TEMP_SCRIPT = "watering_system_prod.tmp.py"

# Credentials einlesen
$creds = Get-Content $CREDENTIALS_PATH | ConvertFrom-Json
$username = $creds.username
$password = $creds.password

# Temporäre Kopie mit echten Credentials erstellen
(Get-Content $SCRIPT) `
    -replace 'USERNAME = "<username>"', "USERNAME = `"$username`"" `
    -replace 'PASSWORD = "<password>"', "PASSWORD = `"$password`"" |
    Set-Content $TEMP_SCRIPT -Encoding utf8

Write-Host "Deploying $SCRIPT to $PI_HOST ..."
scp $TEMP_SCRIPT "${PI_HOST}:${REMOTE_PATH}"
Remove-Item $TEMP_SCRIPT
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: scp failed." -ForegroundColor Red
    exit 1
}

Write-Host "Restarting irrigation service ..."
ssh $PI_HOST "sudo systemctl restart irrigation"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: systemctl restart failed." -ForegroundColor Red
    exit 1
}

Write-Host "Done! Status:" -ForegroundColor Green
ssh $PI_HOST "sudo systemctl status irrigation --no-pager -l"
