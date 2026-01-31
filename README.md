# Pipeline de Dados de Mobilidade Urbana - Belo Horizonte

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Auditoria](https://img.shields.io/badge/auditoria-9.2%2F10-success.svg)](AUDITORIA_TECNICA.md)
[![Status](https://img.shields.io/badge/status-pronto%20para%20produ%C3%A7%C3%A3o-brightgreen.svg)](CHECKLIST_FINAL.md)

Pipeline de dados moderno para extração, transformação e análise de dados de mobilidade urbana de Belo Horizonte, implementando arquitetura Medallion (Bronze-Silver-Gold) com boas práticas de DataOps.

## 📋 Visão Geral

Este projeto implementa um pipeline ETL completo que:

- **Extrai** dados públicos de mobilidade urbana de Belo Horizonte
- **Armazena** em data lake com arquitetura Medallion
- **Transforma** e limpa os dados com validações de qualidade
- **Carrega** em data warehouse otimizado para análises
- **Automatiza** todo o processo com boas práticas de DataOps

## 🏗️ Arquitetura

### Arquitetura Medallion

```
📊 Fontes de Dados (APIs Dados Abertos BH)
    ↓
🥉 BRONZE LAYER (Dados Brutos - Parquet)
    ├── onibus_tempo_real/
    └── mco/
    ↓
🥈 SILVER LAYER (Dados Limpos - Delta Lake)
    ├── onibus_posicoes/
    └── mco_linhas/
    ↓
🥇 GOLD LAYER (Métricas de Negócio - Delta Lake)
    ├── velocidade_media_por_linha/
    ├── onibus_ativos_por_periodo/
    ├── cobertura_geografica/
    └── pontos_criticos_velocidade/
```

### Componentes Principais

- **Bronze**: Dados brutos imutáveis (Parquet, compressão Snappy)
- **Silver**: Dados validados e limpos (Delta Lake)
- **Gold**: Agregações e KPIs (Delta Lake)

Para mais detalhes, consulte [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🚀 Quick Start

### Pré-requisitos

**Sistema**:
- Python 3.11 ou superior
- pip ou conda
- 4GB RAM mínimo (recomendado 8GB)
- 2GB espaço em disco

**Conhecimentos**:
- Python básico
- Conceitos de ETL
- SQL/Pandas (desejável)

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/bh-mobilidade-pipeline.git
cd bh-mobilidade-pipeline
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

### Uso Básico

#### Executar pipeline completo

```bash
python src/pipeline.py
```

#### Executar camadas específicas

```bash
# Apenas Bronze (ingestão)
python src/pipeline.py --layers bronze

# Silver e Gold (sem ingestão)
python src/pipeline.py --layers silver gold

# Reprocessar dados existentes
python src/pipeline.py --skip-bronze
```

#### Executar com configuração customizada

```bash
python src/pipeline.py --config config/config.yaml
```

## 📁 Estrutura do Projeto

```
bh-mobilidade-pipeline/
├── config/                  # Configurações
│   └── config.yaml          # Config principal
├── data/                    # Dados (local)
│   ├── bronze/              # Camada Bronze
│   ├── silver/              # Camada Silver
│   └── gold/                # Camada Gold
├── docs/                    # Documentação
│   └── ARCHITECTURE.md      # Arquitetura detalhada
├── logs/                    # Arquivos de log
├── notebooks/               # Jupyter Notebooks
│   ├── 01_exploracao.ipynb
│   └── 02_analise.ipynb
├── src/                     # Código-fonte
│   ├── bronze/              # Ingestão de dados
│   │   ├── __init__.py
│   │   └── ingestion.py
│   ├── silver/              # Transformações
│   │   ├── __init__.py
│   │   └── transformation.py
│   ├── gold/                # Agregações
│   │   ├── __init__.py
│   │   └── aggregation.py
│   ├── utils/               # Utilitários
│   │   ├── __init__.py
│   │   ├── common.py
│   │   └── data_quality.py
│   ├── __init__.py
│   └── pipeline.py          # Orquestrador principal
├── tests/                   # Testes
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_bronze.py
│   ├── test_data_quality.py
│   └── test_utils.py
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── pyproject.toml           # Configuração do projeto
├── requirements.txt         # Dependências
├── setup.py                 # Setup do pacote
└── README.md                # Este arquivo
```

## 🔧 Configuração

### Arquivo `config/config.yaml`

```yaml
pipeline:
  name: "bh_mobilidade_urbana_pipeline"
  version: "1.0.0"

data_sources:
  onibus_tempo_real:
    url: "https://temporeal.pbh.gov.br/v1/posicoes"
    enabled: true
  mco:
    url: "https://dados.pbh.gov.br/dataset/mco"
    enabled: true

layers:
  bronze:
    path: "./data/bronze"
    format: "parquet"
  silver:
    path: "./data/silver"
    format: "delta"
  gold:
    path: "./data/gold"
    format: "delta"
```

### Variáveis de Ambiente

```bash
# .env
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_DATA_QUALITY_CHECKS=true
ENABLE_DATA_LINEAGE=true
```

## 📊 Métricas de Negócio (Gold Layer)

### 1. Velocidade Média por Linha
- Velocidade média, mediana, máxima e mínima
- Desvio padrão
- Agregado por linha e data

### 2. Ônibus Ativos por Período
- Total de ônibus únicos
- Distribuição por hora do dia
- Análise por dia da semana

### 3. Cobertura Geográfica
- Área de cobertura por linha
- Coordenadas centrais
- Densidade de pontos

### 4. Pontos Críticos de Velocidade
- Identificação de gargalos
- Grid geográfico com baixa velocidade
- Classificação por severidade

## 🧪 Testes

### Executar todos os testes

```bash
pytest
```

### Executar com cobertura

```bash
pytest --cov=src --cov-report=html
```

### Executar testes específicos

```bash
pytest tests/test_bronze.py
pytest tests/test_data_quality.py -v
```

## 🔍 Qualidade de Dados

### Validações Implementadas

- **Coordenadas geográficas**: Dentro dos limites de BH
- **Velocidade**: Não negativa e < 120 km/h
- **Timestamps**: Formato válido e não nulo
- **Duplicatas**: Identificação e remoção

### Framework de Validação

- **Pandera**: Schemas e validações em tempo real
- **Great Expectations**: Suítes de testes de qualidade
- **Custom Validators**: Regras de negócio específicas

### Score de Qualidade

Cada registro recebe um score de qualidade baseado em:
- Completude dos dados (60%)
- Validação de coordenadas (40%)

## 📈 DataOps e Governança

### Linhagem de Dados

- Rastreamento completo de origem a destino
- Metadados de transformações
- Timestamps de processamento

### Monitoramento

- Logs estruturados por nível
- Métricas de execução
- Alertas de falhas

### Auditoria

- Histórico de validações
- Registro de erros
- Relatórios de qualidade

## 🔄 Agendamento

### Usando Schedule (Python)

```python
import schedule
import time

def job():
    # Executa o pipeline
    pass

schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Usando Cron (Linux)

```bash
# Executar a cada 15 minutos
*/15 * * * * cd /path/to/project && python src/pipeline.py
```

### Usando Airflow

```python
from airflow import DAG
from airflow.operators.bash import BashOperator

dag = DAG('bh_mobilidade', schedule_interval='*/15 * * * *')

run_pipeline = BashOperator(
    task_id='run_pipeline',
    bash_command='python /path/to/src/pipeline.py',
    dag=dag
)
```

## 🚀 Deploy

### Opções de Plataforma

1. **Local Development**
   - Python standalone
   - Arquivo local storage

2. **Cloud Platforms**
   - **AWS**: S3 + Glue + Lambda
   - **Azure**: Blob Storage + Databricks + Functions
   - **GCP**: Cloud Storage + Dataproc + Cloud Functions

3. **Databricks**
   - Notebooks nativos
   - Delta Lake otimizado
   - Cluster management

## 🔐 Segurança

- Credenciais em variáveis de ambiente
- `.env` não versionado
- Dados públicos (sem informações sensíveis)
- Logs sem informações confidenciais

## 📝 Desenvolvimento

### Code Style

```bash
# Formatar código
black src/ tests/

# Verificar estilo
flake8 src/ tests/

# Type checking
mypy src/
```

### Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📚 Recursos

### APIs Utilizadas

- [Portal Dados Abertos BH](https://dados.pbh.gov.br)
- [API Tempo Real - Ônibus BH](https://temporeal.pbh.gov.br)

### Documentação Técnica

- [Python Pandas](https://pandas.pydata.org/)
- [Delta Lake](https://delta.io/)
- [Pandera](https://pandera.readthedocs.io/)
- [Great Expectations](https://greatexpectations.io/)

