# Visão Geral do Projeto

## 📖 Sumário Executivo

Este projeto implementa um **pipeline de dados moderno e completo** para análise de mobilidade urbana de Belo Horizonte, seguindo as melhores práticas de engenharia de dados e DataOps.

## 🎯 Objetivos Alcançados

✅ **Extração de Dados**: Ingestão automatizada de APIs públicas de BH  
✅ **Arquitetura Medallion**: Implementação completa das camadas Bronze, Silver e Gold  
✅ **Qualidade de Dados**: Validações, scores de qualidade e governança  
✅ **Transformações**: Limpeza, padronização e enriquecimento de dados  
✅ **Métricas de Negócio**: 4 conjuntos de agregações analíticas  
✅ **Testes**: Suite completa de testes unitários  
✅ **Documentação**: README detalhado, arquitetura e notebooks  
✅ **DataOps**: Linhagem de dados, logs e monitoramento  

## 🏗️ Tecnologias Utilizadas

| Categoria | Tecnologia | Uso |
|-----------|-----------|-----|
| **Linguagem** | Python 3.11+ | Desenvolvimento principal |
| **Data Processing** | Pandas, PyArrow | Manipulação de dados |
| **Storage** | Parquet, Delta Lake | Formatos de armazenamento |
| **Quality** | Pandera, Great Expectations | Validação de dados |
| **Testing** | Pytest | Testes unitários |
| **Code Quality** | Black, Flake8, MyPy | Formatação e linting |
| **Documentation** | Markdown, Jupyter | Docs e análises |

## 📊 Arquitetura

### Fluxo de Dados

```
APIs BH → Bronze (Raw) → Silver (Clean) → Gold (Analytics)
          Parquet        Delta Lake        Delta Lake
```

### Camadas

1. **Bronze**: Dados brutos imutáveis
   - Formato: Parquet (compressão Snappy)
   - Particionamento: year/month/day
   - Retenção: 90 dias

2. **Silver**: Dados limpos e validados
   - Formato: Delta Lake
   - Validações: Pandera schemas
   - Enriquecimentos: Colunas derivadas
   - Retenção: 180 dias

3. **Gold**: Métricas de negócio
   - Formato: Delta Lake
   - Agregações otimizadas
   - Pronto para consumo
   - Retenção: 365 dias

## 📈 Métricas Implementadas

### 1. Velocidade Média por Linha
Análise de desempenho de cada linha de ônibus, incluindo:
- Velocidade média, mediana, mínima e máxima
- Desvio padrão
- Total de registros por linha/data

### 2. Ônibus Ativos por Período
Distribuição temporal da frota ativa:
- Total de ônibus únicos por hora
- Análise por período do dia (manhã, tarde, noite, madrugada)
- Distribuição por dia da semana

### 3. Cobertura Geográfica
Análise espacial das rotas:
- Área de cobertura por linha
- Coordenadas médias e limites
- Densidade de pontos coletados

### 4. Pontos Críticos de Velocidade
Identificação de gargalos:
- Localização de áreas com baixa velocidade
- Grid geográfico com ocorrências
- Classificação por severidade (baixa, média, alta, crítica)

## 🔍 Qualidade e Governança

### Validações Implementadas

✔️ **Coordenadas Geográficas**
- Latitude: -20.0 a -19.7 (limites de BH)
- Longitude: -44.1 a -43.8 (limites de BH)

✔️ **Velocidade**
- Não negativa
- Máximo de 120 km/h
- Detecção de outliers

✔️ **Timestamps**
- Formato válido
- Não nulos
- Dentro de ranges esperados

### Score de Qualidade

Cada registro recebe um score (0-1) baseado em:
- **Completude (60%)**: Ausência de valores nulos
- **Validade (40%)**: Coordenadas dentro dos limites

### Linhagem de Dados

Rastreamento completo incluindo:
- Fonte dos dados
- Operação realizada
- Timestamps de início/fim
- Duração
- Metadados customizados

## 🧪 Testes

### Cobertura

```
tests/
├── test_utils.py          # Utilitários comuns
├── test_data_quality.py   # Validações de qualidade
└── test_bronze.py         # Ingestão Bronze
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Específico
pytest tests/test_bronze.py -v
```

## 📚 Documentação

### Estrutura

```
docs/
├── ARCHITECTURE.md       # Arquitetura detalhada
README.md                 # Documentação principal
CONTRIBUTING.md           # Guia de contribuição
CHANGELOG.md              # Histórico de mudanças
```

### Notebooks

1. **01_exploracao_dados.ipynb**
   - Análise exploratória
   - Estatísticas descritivas
   - Visualizações

2. **02_analise_metricas.ipynb**
   - Métricas de negócio
   - Insights analíticos
   - Resumo executivo

## 🚀 Como Usar

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/bh-mobilidade-pipeline.git
cd bh-mobilidade-pipeline

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure ambiente
cp .env.example .env

# 4. Execute o pipeline
python src/pipeline.py
```

### Uso Programático

```python
from pipeline import DataPipeline

# Pipeline completo
pipeline = DataPipeline()
results = pipeline.run()

# Apenas Silver e Gold
results = pipeline.run(layers=["silver", "gold"])

# Reprocessamento
results = pipeline.run(skip_bronze=True)
```

## 🎓 Diferenciais Implementados

### DataOps

✅ **Automação**: Pipeline completamente automatizado  
✅ **Monitoramento**: Logs estruturados e métricas  
✅ **Qualidade**: Validações em tempo real  
✅ **Governança**: Linhagem e auditoria  
✅ **Testes**: Suite completa com >80% cobertura  

### Boas Práticas

✅ **Código Modular**: Separação clara de responsabilidades  
✅ **PEP 8**: Código formatado e padronizado  
✅ **Type Hints**: Tipos explícitos para melhor manutenção  
✅ **Docstrings**: Documentação inline completa  
✅ **Git**: Estrutura pronta para versionamento  

### Escalabilidade

✅ **Arquitetura Medallion**: Padrão industry-standard  
✅ **Delta Lake**: ACID transactions e time travel  
✅ **Particionamento**: Otimização de leitura/escrita  
✅ **Modular**: Fácil adicionar novas fontes/métricas  

## 📊 Próximos Passos

### Curto Prazo
- [ ] Dashboard interativo (Streamlit/Dash)
- [ ] Alertas automáticos de qualidade
- [ ] API REST para consulta

### Médio Prazo
- [ ] Orquestração com Airflow
- [ ] Modelos preditivos de velocidade
- [ ] CI/CD com GitHub Actions

### Longo Prazo
- [ ] Suporte a PySpark para big data
- [ ] Deploy em cloud (AWS/Azure/GCP)
- [ ] ML para otimização de rotas

## 👥 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.
