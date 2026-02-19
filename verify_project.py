#!/usr/bin/env python3
"""
Script de verificação do projeto antes de publicar no Git.
Verifica se todos os arquivos necessários estão presentes e se o pipeline funciona.
"""

import os
import sys
from pathlib import Path


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_check(item: str, status: bool):
    """Imprime status de verificação."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {item}")
    return status


def check_file_exists(filepath: str, description: str) -> bool:
    """Verifica se arquivo existe."""
    exists = os.path.exists(filepath)
    print_check(f"{description}: {filepath}", exists)
    return exists


def verify_project_structure():
    """Verifica estrutura do projeto."""
    print_header("Verificando Estrutura do Projeto")
    
    all_ok = True
    
    # Arquivos essenciais
    essential_files = {
        "requirements.txt": "Dependências do projeto",
        "README.md": "Documentação principal",
        ".gitignore": "Arquivos a ignorar",
        ".env.example": "Template de variáveis de ambiente",
        "config/config.yaml": "Configuração do pipeline",
        "run_pipeline.bat": "Script Windows",
        "run_pipeline.sh": "Script Linux/Mac",
    }
    
    for file, desc in essential_files.items():
        all_ok &= check_file_exists(file, desc)
    
    # Diretórios essenciais
    essential_dirs = {
        "src": "Código fonte",
        "src/bronze": "Camada Bronze",
        "src/silver": "Camada Silver",
        "src/gold": "Camada Gold",
        "src/utils": "Utilitários",
        "docs": "Documentação",
        "tests": "Testes",
        "config": "Configurações",
    }
    
    for dir_path, desc in essential_dirs.items():
        all_ok &= check_file_exists(dir_path, desc)
    
    return all_ok


def verify_documentation():
    """Verifica documentação."""
    print_header("Verificando Documentação")
    
    all_ok = True
    
    docs = {
        "README.md": "Documentação principal",
        "docs/INSTALLATION.md": "Guia de instalação",
        "docs/ARCHITECTURE.md": "Arquitetura",
        "docs/CORRECOES_TECNICAS.md": "Correções técnicas",
        "docs/ANALISE_PROBLEMA_API.md": "Análise problema API",
        "docs/DICIONARIO_DADOS.md": "Dicionário de dados",
        "CONTRIBUTING.md": "Guia de contribuição",
        "CHANGELOG.md": "Histórico de mudanças",
    }
    
    for file, desc in docs.items():
        all_ok &= check_file_exists(file, desc)
    
    return all_ok


def verify_dependencies():
    """Verifica dependências no requirements.txt."""
    print_header("Verificando Dependências")
    
    all_ok = True
    
    required_packages = [
        "pandas",
        "pyarrow",
        "curl-cffi",  # Crucial!
        "deltalake",
        "pandera",
        "pyyaml",
        "pytest",
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read().lower()
            
        for package in required_packages:
            exists = package.lower() in content
            print_check(f"Pacote {package}", exists)
            all_ok &= exists
            
            if package == "curl-cffi" and exists:
                print("   ⭐ curl-cffi presente - solução portável OK!")
                
    except Exception as e:
        print_check(f"Erro ao ler requirements.txt: {e}", False)
        return False
    
    return all_ok


def verify_gitignore():
    """Verifica .gitignore."""
    print_header("Verificando .gitignore")
    
    all_ok = True
    
    patterns = [
        "__pycache__",
        ".venv",
        "venv/",
        ".env",
        "data/bronze/*",
        "data/silver/*",
        "data/gold/*",
        "*.log",
        "*.parquet",
    ]
    
    try:
        with open(".gitignore", "r") as f:
            content = f.read()
            
        for pattern in patterns:
            exists = pattern in content
            print_check(f"Ignora {pattern}", exists)
            all_ok &= exists
            
    except Exception as e:
        print_check(f"Erro ao ler .gitignore: {e}", False)
        return False
    
    return all_ok


def verify_readme():
    """Verifica conteúdo do README."""
    print_header("Verificando README.md")
    
    all_ok = True
    
    required_sections = [
        "Quick Start",
        "Instalação",
        "Arquitetura",
        "python -m src.pipeline",  # Comando correto
    ]
    
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        for section in required_sections:
            exists = section in content
            print_check(f"Seção/conteúdo: {section}", exists)
            all_ok &= exists
            
        # Verifica se não tem o comando ERRADO
        wrong_command = "python src/pipeline.py"
        has_wrong = wrong_command in content and "python -m src.pipeline" not in content
        if has_wrong:
            print_check("⚠️ README tem comando ERRADO (src/pipeline.py)", False)
            all_ok = False
        else:
            print_check("Comando correto (python -m src.pipeline)", True)
            
    except Exception as e:
        print_check(f"Erro ao ler README: {e}", False)
        return False
    
    return all_ok


def test_imports():
    """Testa se os imports principais funcionam."""
    print_header("Testando Imports")
    
    all_ok = True
    
    modules = [
        ("pandas", "Pandas"),
        ("pyarrow", "PyArrow"),
        ("curl_cffi", "curl_cffi (solução portável)"),
        ("deltalake", "Delta Lake"),
        ("pandera", "Pandera"),
        ("yaml", "PyYAML"),
    ]
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_check(f"Import {description}", True)
        except ImportError:
            print_check(f"Import {description}", False)
            all_ok = False
    
    return all_ok


def main():
    """Executa todas as verificações."""
    print_header("🔍 VERIFICAÇÃO DO PROJETO PARA GIT/GITHUB")
    
    results = {
        "Estrutura do Projeto": verify_project_structure(),
        "Documentação": verify_documentation(),
        "Dependências": verify_dependencies(),
        "Gitignore": verify_gitignore(),
        "README": verify_readme(),
        "Imports": test_imports(),
    }
    
    # Resumo
    print_header("📊 RESUMO")
    
    all_passed = all(results.values())
    
    for category, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {category}: {'OK' if status else 'FALHOU'}")
    
    print(f"\n{'=' * 70}")
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Projeto está pronto para ser publicado no Git/GitHub")
        print("\nPróximos passos:")
        print("1. git init (se ainda não fez)")
        print("2. git add .")
        print("3. git commit -m 'Initial commit'")
        print("4. git remote add origin <url>")
        print("5. git push -u origin main")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Corrija os problemas acima antes de publicar")
        sys.exit(1)
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
