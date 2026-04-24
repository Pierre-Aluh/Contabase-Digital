param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dbPath = Join-Path $root "banco_de_dados\contabase_digital.db"
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not $Force) {
    $answer = Read-Host "Isso vai apagar o banco local de desenvolvimento. Digite SIM para continuar"
    if ($answer -ne "SIM") {
        Write-Host "Operacao cancelada"
        exit 0
    }
}

if (Test-Path $dbPath) {
    Remove-Item -Path $dbPath -Force
    Write-Host "Banco removido: $dbPath"
}

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual nao encontrado em: $python"
}

Push-Location $root
try {
    & $python "main.py" --check
} finally {
    Pop-Location
}

Write-Host "Reset concluido. Banco recriado com seed inicial." 
