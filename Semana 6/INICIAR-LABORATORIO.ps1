$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host "Crea el entorno con py -m venv .venv e instala requirements.txt."
    exit 1
}
Write-Host "Portal: http://127.0.0.1:8096/"
Write-Host "Administrador: http://127.0.0.1:8096/admin/"
& $pythonPath manage.py runserver 127.0.0.1:8096
