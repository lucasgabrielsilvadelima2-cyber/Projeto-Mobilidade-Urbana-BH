# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-01-30

### Adicionado

#### Arquitetura Medallion
- **Camada Bronze**: Ingestão de dados brutos em formato Parquet
  - Ingestor para API de ônibus em tempo real
  - Ingestor para Mapa de Controle Operacional (MCO)
  - Particionamento por year/month/day
  - Metadados de ingestão

- **Camada Silver**: Transformação e limpeza de dados em Delta Lake
  - Limpeza e padronização de nomes de colunas
  - Validação de dados com Pandera
  - Remoção de duplicatas
  - Enriquecimento com colunas derivadas (período do dia, dia da semana)
  - Score de qualidade de dados
  - Particionamento por data

- **Camada Gold**: Agregações e métricas de negócio
  - Velocidade média por linha
  - Ônibus ativos por período
  - Cobertura geográfica
  - Pontos críticos de velocidade
  - Tabelas otimizadas para análise

#### DataOps e Governança
- Framework de validação de qualidade de dados
- Rastreamento de linhagem de dados
- Sistema de logging estruturado
- Metadados de processamento
- Auditoria de execuções

#### Utilitários
- Funções de particionamento
- Gerenciamento de configurações
- Helpers de logging
- Validadores customizados

#### Pipeline
- Orquestrador principal integrando todas as camadas
- Suporte a execução por camadas específicas
- Modo de reprocessamento
- Tratamento de erros robusto
- CLI com argumentos

#### Testes
- Testes unitários para utilitários
- Testes de qualidade de dados
- Testes de ingestão Bronze
- Cobertura de código
- Mocks para APIs externas

#### Documentação
- README completo com instruções
- Documentação de arquitetura
- Guia de contribuição
- Notebooks de análise exploratória
- Notebooks de análise de métricas
- Exemplos de uso

#### Ferramentas
- Scripts de execução (Windows/Linux)
- Makefile com comandos comuns
- Configurações de ambiente
- Setup do projeto

### Recursos Técnicos

- Python 3.11+ support
- Pandas para manipulação de dados
- PyArrow para Parquet
- Delta Lake para ACID transactions
- Pandera para validação de schemas
- Great Expectations para qualidade
- Pytest para testes
- Black/Flake8 para code quality

### APIs Integradas

- Portal de Dados Abertos de Belo Horizonte
- API Tempo Real - Posicionamento de Ônibus
- Mapa de Controle Operacional (MCO)

### Estrutura do Projeto

```
├── config/              # Configurações
├── data/                # Data lake (Bronze/Silver/Gold)
├── docs/                # Documentação
├── logs/                # Logs de execução
├── notebooks/           # Jupyter notebooks
├── src/                 # Código-fonte
│   ├── bronze/          # Camada Bronze
│   ├── silver/          # Camada Silver
│   ├── gold/            # Camada Gold
│   └── utils/           # Utilitários
├── tests/               # Testes
├── requirements.txt     # Dependências
└── README.md            # Documentação principal
```

### Métricas de Negócio

1. **Velocidade Média por Linha**: Análise de desempenho por linha de ônibus
2. **Ônibus Ativos por Período**: Distribuição temporal da frota
3. **Cobertura Geográfica**: Análise espacial das rotas
4. **Pontos Críticos**: Identificação de gargalos de velocidade

### Qualidade e Governança

- Validação de coordenadas geográficas
- Validação de velocidades
- Score de qualidade por registro
- Linhagem de dados completa
- Logs estruturados
- Relatórios de validação

---

## [Unreleased]

### Planejado

- [ ] Integração com Apache Airflow para orquestração
- [ ] Dashboard interativo com Streamlit/Dash
- [ ] Modelos preditivos de velocidade
- [ ] Alertas automáticos de qualidade
- [ ] API REST para consulta de dados
- [ ] Exportação para formatos analíticos (Parquet, ORC)
- [ ] Suporte a PySpark para big data
- [ ] Deploy em cloud (AWS/Azure/GCP)
- [ ] CI/CD com GitHub Actions
- [ ] Documentação com Sphinx

---

## Legenda

- **Adicionado**: Novas funcionalidades
- **Modificado**: Mudanças em funcionalidades existentes
- **Descontinuado**: Funcionalidades que serão removidas
- **Removido**: Funcionalidades removidas
- **Corrigido**: Correções de bugs
- **Segurança**: Correções de vulnerabilidades
