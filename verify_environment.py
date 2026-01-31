"""
Script de Verificação do Ambiente.

Verifica se todas as dependências estão instaladas corretamente
e se o ambiente está configurado adequadamente.
"""

import sys
from pathlib import Path


def check_python_version():
    """Verifica versão do Python."""
    version = sys.version_info
    print(f"\n🐍 Python Version:")
    print(f"   Versão: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("   ✅ Versão adequada (3.11+)")
        return True
    else:
        print("   ❌ Versão inadequada (requer 3.11+)")
        return False


def check_dependencies():
    """Verifica dependências instaladas."""
    print(f"\n📦 Dependências:")
    
    dependencies = {
        "pandas": "Manipulação de dados",
        "pyarrow": "I/O Parquet",
        "requests": "HTTP client",
        "deltalake": "Delta Lake",
        "pandera": "Validação de dados",
        "pytest": "Framework de testes",
        "pyyaml": "Configurações YAML"
    }
    
    all_ok = True
    for package, description in dependencies.items():
        try:
            mod = __import__(package)
            version = getattr(mod, "__version__", "?")
            print(f"   ✅ {package:15s} {version:10s} - {description}")
        except ImportError:
            print(f"   ❌ {package:15s} {'N/A':10s} - {description} (NÃO INSTALADO)")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """Verifica estrutura de diretórios."""
    print(f"\n📁 Estrutura do Projeto:")
    
    required_dirs = [
        "src",
        "src/bronze",
        "src/silver",
        "src/gold",
        "src/utils",
        "tests",
        "config",
        "data",
        "docs",
        "notebooks"
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            print(f"   ✅ {dir_name}")
        else:
            print(f"   ❌ {dir_name} (NÃO ENCONTRADO)")
            all_ok = False
    
    return all_ok


def check_config_files():
    """Verifica arquivos de configuração."""
    print(f"\n⚙️  Arquivos de Configuração:")
    
    config_files = {
        "config/config.yaml": "Configuração principal",
        ".env.example": "Exemplo de variáveis de ambiente",
        "requirements.txt": "Dependências Python",
        "setup.py": "Setup do projeto",
        "README.md": "Documentação principal"
    }
    
    all_ok = True
    for file_name, description in config_files.items():
        path = Path(file_name)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {file_name:25s} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {file_name:25s} - {description} (NÃO ENCONTRADO)")
            all_ok = False
    
    return all_ok


def check_env_variables():
    """Verifica variáveis de ambiente."""
    print(f"\n🔐 Variáveis de Ambiente:")
    
    import os
    
    env_vars = [
        "ENVIRONMENT",
        "LOG_LEVEL",
        "DATA_BRONZE_PATH",
        "DATA_SILVER_PATH",
        "DATA_GOLD_PATH"
    ]
    
    any_set = False
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
            any_set = True
        else:
            print(f"   ⚠️  {var}: não definido (opcional)")
    
    if not any_set:
        print("\n   ℹ️  Nenhuma variável de ambiente configurada.")
        print("      Copie .env.example para .env se necessário")
    
    return True  # Variáveis de ambiente são opcionais


def check_data_directories():
    """Verifica diretórios de dados."""
    print(f"\n💾 Diretórios de Dados:")
    
    data_dirs = [
        "data/bronze",
        "data/silver",
        "data/gold",
        "logs"
    ]
    
    for dir_name in data_dirs:
        path = Path(dir_name)
        if path.exists():
            files_count = len(list(path.rglob("*")))
            print(f"   ✅ {dir_name:15s} ({files_count} arquivos)")
        else:
            print(f"   ⚠️  {dir_name:15s} (será criado automaticamente)")
    
    return True


def check_import_modules():
    """Testa importação dos módulos do projeto."""
    print(f"\n🔧 Módulos do Projeto:")
    
    sys.path.insert(0, str(Path("src")))
    
    modules = [
        ("utils.common", "Utilitários comuns"),
        ("utils.data_quality", "Validação de qualidade"),
        ("bronze.ingestion", "Ingestão de dados"),
        ("silver.transformation", "Transformações"),
        ("gold.aggregation", "Agregações"),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name:30s} - {description}")
        except ImportError as e:
            print(f"   ❌ {module_name:30s} - {description} (ERRO: {e})")
            all_ok = False
    
    return all_ok


def run_basic_tests():
    """Executa testes básicos."""
    print(f"\n🧪 Testes Básicos:")
    
    try:
        import pytest
        print("   ✅ Pytest disponível")
        
        # Verifica se há testes
        test_files = list(Path("tests").glob("test_*.py"))
        print(f"   ✅ {len(test_files)} arquivos de teste encontrados")
        
        # Não executa os testes aqui, apenas verifica disponibilidade
        print("   ℹ️  Execute 'pytest' para rodar os testes")
        
        return True
    except ImportError:
        print("   ❌ Pytest não disponível")
        return False


def main():
    """Função principal."""
    print("=" * 70)
    print("🔍 VERIFICAÇÃO DO AMBIENTE - BH MOBILIDADE PIPELINE")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependências", check_dependencies),
        ("Estrutura do Projeto", check_project_structure),
        ("Arquivos de Configuração", check_config_files),
        ("Variáveis de Ambiente", check_env_variables),
        ("Diretórios de Dados", check_data_directories),
        ("Módulos do Projeto", check_import_modules),
        ("Framework de Testes", run_basic_tests)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n   ❌ Erro ao verificar {name}: {e}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("\n🎉 AMBIENTE CONFIGURADO CORRETAMENTE!")
        print("Você está pronto para executar o pipeline.")
        print("\nPróximos passos:")
        print("  1. python exemplo_uso.py")
        print("  2. python src/pipeline.py")
        print("  3. jupyter notebook notebooks/")
        return 0
    else:
        print("\n⚠️  ALGUMAS VERIFICAÇÕES FALHARAM")
        print("Por favor, corrija os problemas acima antes de continuar.")
        print("\nPara instalar dependências:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
