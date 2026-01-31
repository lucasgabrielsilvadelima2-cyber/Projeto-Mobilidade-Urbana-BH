# Guia de Instalação e Configuração

## 📋 Pré-requisitos Detalhados

### Requisitos de Sistema

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| Python | 3.11 | 3.11+ |
| RAM | 4GB | 8GB |
| Disco | 2GB | 5GB |
| Processador | Dual-core | Quad-core |
| OS | Windows 10, Linux, macOS | Qualquer |

### Conhecimentos Necessários

- **Essencial**: Python básico, linha de comando
- **Desejável**: Pandas, SQL, conceitos de ETL
- **Opcional**: PySpark, Delta Lake, Databricks

## 🚀 Instalação Passo a Passo

### Opção 1: Instalação Rápida (Recomendada)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/bh-mobilidade-pipeline.git
cd bh-mobilidade-pipeline

# 2. Execute o script de setup
python setup_project.py
```

### Opção 2: Instalação Manual

#### Passo 1: Clone o Repositório

```bash
git clone https://github.com/seu-usuario/bh-mobilidade-pipeline.git
cd bh-mobilidade-pipeline
```

#### Passo 2: Crie o Ambiente Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### Passo 3: Instale as Dependências

```bash
# Instalar dependências principais
pip install -r requirements.txt

# Instalar o projeto em modo de desenvolvimento
pip install -e .

# (Opcional) Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt
```

#### Passo 4: Configure o Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas configurações (opcional)
# notepad .env  # Windows
# nano .env     # Linux/Mac
```

#### Passo 5: Verifique a Instalação

```bash
# Verifique a versão do Python
python --version

# Execute os testes
pytest

# Execute o exemplo
python exemplo_uso.py
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Ambiente
ENVIRONMENT=development  # development, staging, production

# APIs
BH_ONIBUS_TEMPO_REAL_URL=https://temporeal.pbh.gov.br/v1/posicoes
BH_MCO_URL=https://dados.pbh.gov.br/dataset/mco

# Caminhos de Dados
DATA_BRONZE_PATH=./data/bronze
DATA_SILVER_PATH=./data/silver
DATA_GOLD_PATH=./data/gold

# Logs
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_PATH=./logs

# Qualidade
ENABLE_DATA_QUALITY_CHECKS=true
ENABLE_DATA_LINEAGE=true

# Agendamento (opcional)
SCHEDULE_ENABLED=false
SCHEDULE_INTERVAL_MINUTES=15
```

### Arquivo de Configuração (config/config.yaml)

O arquivo principal já está configurado com valores padrão sensatos. Ajuste conforme necessário:

```yaml
# Principais configurações a ajustar:
data_sources:
  onibus_tempo_real:
    enabled: true  # false para desabilitar
  mco:
    enabled: true

layers:
  bronze:
    retention_days: 90  # Ajuste conforme necessidade
  silver:
    retention_days: 180
  gold:
    retention_days: 365
```

## 🔧 Configurações Avançadas

### Para Produção

1. **Ajuste o nível de log**:
```yaml
logging:
  level: "WARNING"  # Menos verboso
```

2. **Configure rotação de logs**:
```yaml
logging:
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

3. **Ajuste performance**:
```yaml
performance:
  chunk_size: 50000  # Para datasets maiores
  max_workers: 8     # Aumentar em máquinas mais potentes
```

### Para Desenvolvimento

1. **Ative logs de debug**:
```bash
LOG_LEVEL=DEBUG
```

2. **Desabilite validações pesadas**:
```bash
ENABLE_DATA_QUALITY_CHECKS=false
```

### Para Ambientes Cloud

#### AWS
```yaml
layers:
  bronze:
    path: "s3://seu-bucket/bronze"
  silver:
    path: "s3://seu-bucket/silver"
  gold:
    path: "s3://seu-bucket/gold"
```

#### Azure
```yaml
layers:
  bronze:
    path: "abfss://container@storage.dfs.core.windows.net/bronze"
```

#### GCP
```yaml
layers:
  bronze:
    path: "gs://seu-bucket/bronze"
```

## 📦 Dependências Opcionais

### PySpark (Para Big Data)

```bash
pip install pyspark==3.5.0
```

### Databricks (Para Cloud)

```bash
pip install databricks-connect==13.0
```

### Visualização Avançada

```bash
pip install plotly seaborn folium
```

## ✅ Verificação da Instalação

Execute este checklist para garantir que tudo está funcionando:

```python
# verification_script.py
import sys
print(f"✓ Python version: {sys.version}")

try:
    import pandas
    print(f"✓ Pandas: {pandas.__version__}")
except ImportError:
    print("✗ Pandas não instalado")

try:
    import pyarrow
    print(f"✓ PyArrow: {pyarrow.__version__}")
except ImportError:
    print("✗ PyArrow não instalado")

try:
    from deltalake import DeltaTable
    print("✓ Delta Lake instalado")
except ImportError:
    print("✗ Delta Lake não instalado")

try:
    import pandera
    print(f"✓ Pandera: {pandera.__version__}")
except ImportError:
    print("✗ Pandera não instalado")

print("\n✅ Instalação verificada!")
```

Execute:
```bash
python verification_script.py
```

## 🐛 Troubleshooting

### Erro: "Module not found"

**Solução**:
```bash
pip install -r requirements.txt --upgrade
```

### Erro: "Permission denied"

**Solução**:
```bash
# Windows (execute como Administrador)
# Linux/Mac
chmod +x run_pipeline.sh
```

### Erro: "Delta Lake not found"

**Solução**:
```bash
pip uninstall deltalake
pip install deltalake --no-cache-dir
```

### Erro de memória

**Solução**:
Reduza o `chunk_size` no `config.yaml`:
```yaml
performance:
  chunk_size: 5000  # Menor para máquinas com menos RAM
```

### APIs não respondem

**Solução**:
1. Verifique sua conexão com internet
2. Verifique se as URLs estão corretas
3. Teste manualmente:
```bash
curl https://temporeal.pbh.gov.br/v1/posicoes
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique a [FAQ](#) no repositório
2. Busque em [Issues](https://github.com/seu-usuario/bh-mobilidade-pipeline/issues)
3. Abra uma nova issue com:
   - Versão do Python
   - Sistema operacional
   - Erro completo
   - Passos para reproduzir

## 🎓 Próximos Passos

Após a instalação:

1. ✅ Execute o exemplo básico: `python exemplo_uso.py`
2. ✅ Explore os notebooks: `jupyter notebook notebooks/`
3. ✅ Execute o pipeline completo: `python src/pipeline.py`
4. ✅ Leia a documentação: [docs/](docs/)
5. ✅ Execute os testes: `pytest`

---

**Instalação concluída! Você está pronto para começar! 🚀**
