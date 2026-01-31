@echo off
REM Script para executar o pipeline no Windows

echo ============================================================
echo Pipeline de Dados - Mobilidade Urbana BH
echo ============================================================

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Executa o pipeline
echo.
echo Executando pipeline...
python src\pipeline.py %*

echo.
echo ============================================================
echo Pipeline concluído!
echo ============================================================
pause
