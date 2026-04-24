param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$spec = Join-Path $root "ContabaseDigital.spec"

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual nao encontrado em: $python"
}

if (-not (Test-Path $spec)) {
    throw "Arquivo spec nao encontrado em: $spec"
}

Push-Location $root
try {
    if ($Clean) {
        Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    }

    & $python -m PyInstaller --noconfirm --clean "$spec"
} finally {
    Pop-Location
}

Write-Host "Build concluido. Saida em: dist/ContabaseDigital"
