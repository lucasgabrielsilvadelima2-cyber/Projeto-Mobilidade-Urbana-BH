"""
Script de Exemplo - Execução Rápida do Pipeline.

Este script demonstra como usar o pipeline programaticamente.
"""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline import DataPipeline


def exemplo_basico():
    """Exemplo básico de execução do pipeline."""
    print("=" * 60)
    print("EXEMPLO BÁSICO - PIPELINE COMPLETO")
    print("=" * 60)
    
    try:
        # Cria e executa o pipeline
        pipeline = DataPipeline(config_path="config/config.yaml")
        results = pipeline.run()
    except FileNotFoundError as e:
        print(f"\n❌ Erro: Arquivo de configuração não encontrado: {e}")
        print("Certifique-se de que o arquivo config/config.yaml existe.")
        return
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Mostra resultados
    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"Status: {results['status']}")
    print(f"Duração: {results['duration_seconds']:.2f} segundos")
    print(f"\nCamadas processadas:")
    for layer, data in results['layers'].items():
        print(f"  - {layer.upper()}: {data}")


def exemplo_por_camadas():
    """Exemplo de execução de camadas específicas."""
    print("\n" + "=" * 60)
    print("EXEMPLO - APENAS CAMADA SILVER E GOLD")
    print("=" * 60)
    
    pipeline = DataPipeline()
    results = pipeline.run(layers=["silver", "gold"])
    
    print(f"\nStatus: {results['status']}")


def exemplo_reprocessamento():
    """Exemplo de reprocessamento de dados existentes."""
    print("\n" + "=" * 60)
    print("EXEMPLO - REPROCESSAMENTO (SKIP BRONZE)")
    print("=" * 60)
    
    pipeline = DataPipeline()
    results = pipeline.run(skip_bronze=True)
    
    print(f"\nStatus: {results['status']}")


if __name__ == "__main__":
    print("\n🚀 Exemplos de Uso do Pipeline\n")
    
    # Escolha qual exemplo executar
    print("Escolha um exemplo:")
    print("1. Pipeline completo (Bronze + Silver + Gold)")
    print("2. Apenas Silver e Gold")
    print("3. Reprocessamento (skip Bronze)")
    print("0. Sair")
    
    try:
        choice = input("\nDigite o número: ").strip()
        
        if choice == "1":
            exemplo_basico()
        elif choice == "2":
            exemplo_por_camadas()
        elif choice == "3":
            exemplo_reprocessamento()
        elif choice == "0":
            print("Saindo...")
        else:
            print("Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
