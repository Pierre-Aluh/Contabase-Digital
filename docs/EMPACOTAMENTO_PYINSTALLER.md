# Empacotamento com PyInstaller

A entrega final usa `ContabaseDigital.spec` para padronizar o build.

## Pre-requisitos

1. Ambiente virtual criado
2. Dependencias instaladas

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Gerar executavel (onedir)

```powershell
.\scripts\build_pyinstaller.ps1 -Clean
```

Saida esperada:
- pasta `dist/ContabaseDigital/`
- executavel principal `ContabaseDigital.exe`

## Observacoes

- O build inclui `app/ui/styles/stylesheet.qss` e pasta `app/ui/assets`.
- O modo `onedir` foi escolhido por estabilidade com PySide6.
- Em caso de bloqueio por antivirus, assine o executavel e pasta de distribuicao antes da publicacao.
