$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host "No se encontro el entorno virtual. Ejecuta primero:" -ForegroundColor Yellow
    Write-Host "  py -m venv .venv"
    Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

Set-Location -LiteralPath $projectRoot
Write-Host "Catalogo:       http://127.0.0.1:8095/" -ForegroundColor Cyan
Write-Host "Administrador:  http://127.0.0.1:8095/admin/" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor." -ForegroundColor DarkGray

Start-Process "http://127.0.0.1:8095/"
& $pythonPath manage.py runserver 127.0.0.1:8095
