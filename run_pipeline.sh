#!/bin/bash
# Script para executar o pipeline no Linux/Mac

echo "============================================================"
echo "Pipeline de Dados - Mobilidade Urbana BH"
echo "============================================================"

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Executa o pipeline
echo ""
echo "Executando pipeline..."
python src/pipeline.py "$@"

echo ""
echo "============================================================"
echo "Pipeline concluído!"
echo "============================================================"
