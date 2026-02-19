@echo off
REM Script para executar o pipeline no Windows

echo ============================================================
echo Pipeline de Dados - Mobilidade Urbana BH
echo ============================================================

REM Verifica qual ambiente virtual existe e usa
if exist .venv\Scripts\python.exe (
    echo Usando Python do ambiente virtual (.venv^)...
    echo.
    echo Executando pipeline...
    .venv\Scripts\python.exe -m src.pipeline %*
    goto :end
)

if exist venv\Scripts\python.exe (
    echo Usando Python do ambiente virtual (venv^)...
    echo.
    echo Executando pipeline...
    venv\Scripts\python.exe -m src.pipeline %*
    goto :end
)

echo AVISO: Ambiente virtual nao encontrado!
echo Tentando usar Python do sistema...
echo.
echo Executando pipeline...
python -m src.pipeline %*

:end
echo.
echo ============================================================
echo Pipeline concluido!
echo ============================================================
pause
