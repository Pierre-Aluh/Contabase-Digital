param(
    [string]$BackupDir = "backups"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dbPath = Join-Path $root "banco_de_dados\contabase_digital.db"

if (-not (Test-Path $dbPath)) {
    throw "Banco nao encontrado em: $dbPath"
}

$targetDir = Join-Path $root $BackupDir
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$destPath = Join-Path $targetDir "contabase_digital_$timestamp.db"
Copy-Item -Path $dbPath -Destination $destPath -Force

Write-Host "Backup criado com sucesso: $destPath"
