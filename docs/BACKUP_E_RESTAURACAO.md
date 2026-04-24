# Backup e Restauracao do SQLite

Este projeto utiliza um unico arquivo de banco em `banco_de_dados/contabase_digital.db`.

## Backup rapido

```powershell
.\scripts\backup_db.ps1
```

Opcionalmente informe diretorio customizado:

```powershell
.\scripts\backup_db.ps1 -BackupDir "meus_backups"
```

Resultado esperado:
- cria uma copia versionada com timestamp em `backups/` (ou no diretorio informado)
- exemplo: `contabase_digital_20260424_143500.db`

## Restauracao

1. Feche a aplicacao.
2. Copie o arquivo de backup para `banco_de_dados/contabase_digital.db`.
3. Inicie novamente:

```powershell
.venv\Scripts\python.exe main.py --check
```

## Reset de desenvolvimento

Para resetar o ambiente local e recriar banco com seed inicial:

```powershell
.\scripts\reset_dev_db.ps1 -Force
```

Sem `-Force`, o script pede confirmacao interativa.
