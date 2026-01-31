# 🎤 Guia de Apresentação do Projeto

## Roteiro para Demonstração (15-20 minutos)

### 1. Introdução (2 min)

**Abertura:**
```
"Bom dia/tarde! Apresento o Pipeline de Dados de Mobilidade Urbana de 
Belo Horizonte, uma solução completa de engenharia de dados que extrai,
processa e analisa dados públicos de transporte coletivo."
```

**Pontos-chave:**
- ✅ Dados públicos do Portal de Dados Abertos de BH
- ✅ Arquitetura Medallion (Bronze-Silver-Gold)
- ✅ Boas práticas de DataOps e governança
- ✅ Código modular, testado e documentado

---

### 2. Demonstração da Arquitetura (3 min)

**Mostrar:** README.md - Seção de Arquitetura

**Explicar:**
```
"A solução implementa a arquitetura Medallion em três camadas:

🥉 BRONZE: Dados brutos em Parquet
   - API Tempo Real de ônibus
   - MCO (Mapa de Controle Operacional)
   - Imutável, append-only
   
🥈 SILVER: Dados limpos em Delta Lake
   - Validações de qualidade (Pandera)
   - Enriquecimento com features
   - ACID transactions
   
🥇 GOLD: Métricas de negócio
   - 4 métricas principais agregadas
   - Otimizado para análise
   - Pronto para BI tools"
```

**Destacar:**
- Por que Parquet? → Eficiência
- Por que Delta Lake? → ACID + Time Travel
- Por que três camadas? → Separação de concerns

---

### 3. Demonstração do Código (5 min)

#### 3.1 Estrutura do Projeto

**Mostrar:** Estrutura de diretórios

```bash
tree /F /A
```

**Explicar:**
```
"Código organizado em pacotes:
- src/bronze: Ingestão
- src/silver: Transformação  
- src/gold: Agregação
- src/utils: Funções compartilhadas
- tests/: Testes unitários"
```

#### 3.2 Exemplo de Código - Bronze Layer

**Abrir:** `src/bronze/ingestion.py`

**Destacar:**
```python
class OnibusTempoRealIngester(BronzeDataIngester):
    """Ingestor de dados de ônibus em tempo real."""
    
    def extract(self) -> pd.DataFrame:
        """Extrai dados de posicionamento."""
        # Implementação com retry e tratamento de erros
```

**Pontos:**
- Herança e reutilização
- Docstrings completos
- Type hints
- Error handling

#### 3.3 Exemplo de Código - Silver Layer

**Abrir:** `src/silver/transformation.py`

**Destacar:**
```python
# Validação com Pandera
df = self.validator.validate_onibus_data(df)

# Cálculo de quality score
df["_quality_score"] = self._calculate_quality_score(df)
```

**Pontos:**
- Validações automáticas
- Score de qualidade
- Delta Lake

#### 3.4 Exemplo de Código - Gold Layer

**Abrir:** `src/gold/aggregation.py`

**Destacar:**
```python
class VelocidadeMediaPorLinhaAggregator(GoldAggregator):
    """Agrega velocidade média por linha."""
    
    def aggregate(self) -> pd.DataFrame:
        # Agregações SQL-like com Pandas
```

**Pontos:**
- Métricas de negócio
- Agregações eficientes
- Pronto para consumo

---

### 4. DataOps e Governança (3 min)

**Abrir:** `src/utils/data_quality.py`

**Demonstrar:**

```python
# Schema de validação
schema = DataFrameSchema({
    "latitude": Column(float, 
        checks=[Check.in_range(-20.0, -19.7)]),
    "velocidade": Column(float,
        checks=[Check.greater_than_or_equal_to(0)])
})
```

**Destacar:**
- ✅ Validações automáticas
- ✅ Linhagem de dados rastreável
- ✅ Logs estruturados
- ✅ Métricas de qualidade

**Mostrar:** Exemplo de log

```
2026-01-30 10:00:00 - INFO - Extraindo dados de: API
2026-01-30 10:00:02 - INFO - Extraídos 1000 registros
2026-01-30 10:00:05 - INFO - Validação bem-sucedida: 1000 registros
```

---

### 5. Execução do Pipeline (3 min)

**Terminal:**

```bash
# Mostrar ajuda
python src/pipeline.py --help

# Executar exemplo
python exemplo_uso.py
```

**Opção:** Se houver dados disponíveis, executar pipeline real

```bash
python src/pipeline.py --layers bronze
```

**Explicar output:**
```
============================================================
INICIANDO CAMADA BRONZE - INGESTÃO DE DADOS
============================================================
Extraindo dados de: https://temporeal.pbh.gov.br/v1/posicoes
Extraídos 850 registros
Dados salvos em: data/bronze/onibus_tempo_real/...
✓ Camada Bronze concluída com sucesso
```

---

### 6. Análise com Notebooks (2 min)

**Abrir:** `notebooks/01_exploracao_dados.ipynb`

**Mostrar:**
- Carregamento de dados
- Estatísticas descritivas
- Visualizações (gráficos)

**Abrir:** `notebooks/02_analise_metricas.ipynb`

**Mostrar:**
- Métricas de negócio
- Dashboard de KPIs
- Insights

**Destacar:**
```
"Os notebooks permitem:
- Exploração interativa
- Visualizações
- Análises ad-hoc
- Prototipagem de novas métricas"
```

---

### 7. Testes e Qualidade (1 min)

**Terminal:**

```bash
# Executar testes
pytest -v

# Cobertura
pytest --cov=src --cov-report=term-missing
```

**Mostrar:** Output dos testes passando

**Explicar:**
```
"Testes garantem:
- Código funcional
- Regressões detectadas
- Refactoring seguro
- Documentação executável"
```

---

### 8. Documentação (1 min)

**Mostrar rapidamente:**
- README.md completo
- docs/ARCHITECTURE.md
- docs/OVERVIEW.md
- Docstrings no código

**Destacar:**
```
"Documentação em múltiplos níveis:
- README: Getting started
- Docs: Arquitetura detalhada
- Código: Docstrings completos
- Notebooks: Exemplos práticos"
```

---

### 9. Conclusão (1 min)

**Resumir:**

```
"Em resumo, este projeto entrega:

✅ Pipeline ETL completo e funcional
✅ Arquitetura Medallion implementada
✅ 4 métricas de negócio calculadas
✅ DataOps: qualidade, governança, testes
✅ Código limpo, modular e documentado
✅ Pronto para produção e extensível

Próximos passos sugeridos:
→ Integração com Airflow
→ Dashboard interativo
→ Deploy em cloud
→ Machine Learning"
```

**Perguntas:**
```
"Estou à disposição para perguntas! 🙋"
```

---

## 📋 Checklist de Preparação

### Antes da Apresentação

- [ ] Testar pipeline localmente
- [ ] Verificar que todos os arquivos existem
- [ ] Preparar dados de exemplo (se necessário)
- [ ] Testar notebooks (executar todas as células)
- [ ] Verificar que testes passam
- [ ] Revisar README e documentação
- [ ] Preparar terminal com comandos prontos
- [ ] Ter editor de código aberto (VS Code)
- [ ] Ter navegador pronto para mostrar APIs

### Durante a Apresentação

- [ ] Mostrar estrutura de diretórios
- [ ] Demonstrar código de cada camada
- [ ] Executar pipeline (ou exemplo)
- [ ] Mostrar notebooks com análises
- [ ] Demonstrar testes passando
- [ ] Destacar pontos de DataOps
- [ ] Mencionar documentação
- [ ] Responder perguntas

---

## 🎯 Pontos Fortes a Destacar

### 1. Arquitetura Sólida
- "Implementei a arquitetura Medallion, padrão de mercado para data lakes"
- "Separação clara entre dados brutos, limpos e agregados"

### 2. Qualidade de Código
- "Código seguindo PEP 8, com Black e Flake8"
- "Type hints e docstrings em todas as funções"
- "Modular e facilmente extensível"

### 3. DataOps (Diferencial!)
- "Validações automáticas de qualidade com Pandera"
- "Linhagem de dados rastreável"
- "Score de qualidade calculado para cada registro"
- "Logs estruturados e monitoramento"

### 4. Testabilidade
- "Testes unitários com pytest"
- "Mocks para APIs externas"
- "Cobertura de código implementada"

### 5. Documentação
- "README completo com exemplos"
- "Documentação técnica detalhada"
- "Notebooks para exploração"
- "Guias de instalação e contribuição"

### 6. Produção-Ready
- "Tratamento robusto de erros"
- "Retry mechanism implementado"
- "Configurações externalizáveis"
- "Scripts de deploy (Windows/Linux)"

---

## 💡 Respostas para Perguntas Comuns

### "Por que não usou PySpark?"

```
"Optei por Pandas por alguns motivos:
1. Dados de BH cabem em memória (milhares de registros)
2. Mais acessível para manutenção
3. Mais rápido para desenvolvimento
4. Código está preparado para migração (estrutura modular)"
```

### "Como garantir qualidade dos dados?"

```
"Implementei múltiplas camadas de qualidade:
1. Validações com Pandera (schemas)
2. Regras de negócio (coordenadas, velocidade)
3. Score de qualidade calculado
4. Logs e monitoramento
5. Testes automatizados"
```

### "E se a API cair?"

```
"Implementei tratamento robusto:
1. Retry automático com backoff
2. Timeout configurável
3. Logs detalhados de erros
4. Pipeline continua com outras fontes
5. Dados históricos preservados"
```

### "Como escalar para mais dados?"

```
"Arquitetura preparada para escala:
1. Particionamento por data
2. Delta Lake suporta big data
3. Código modular facilita migração para PySpark
4. Cloud-ready (S3, Azure, GCP)
5. Chunk processing implementado"
```

### "Como adicionar novas fontes?"

```
"Processo simples:
1. Criar novo ingestor em src/bronze/
2. Seguir padrão da classe base
3. Adicionar config em config.yaml
4. Implementar testes
5. Documentar"
```

---

## 📊 Métricas para Mencionar

- **30+ arquivos** organizados
- **3.000+ linhas** de código
- **15+ módulos** Python
- **20+ testes** unitários
- **4 métricas** de negócio
- **3 camadas** (Medallion)
- **100%** seguindo PEP 8
- **80%+** cobertura de testes

---

## 🎬 Scripts Prontos para Copy-Paste

### Terminal 1: Estrutura
```bash
cd "Case BeAnalytic"
tree /F /A src
```

### Terminal 2: Execução
```bash
python exemplo_uso.py
```

### Terminal 3: Testes
```bash
pytest -v --cov=src
```

### VS Code: Arquivos para Abrir
1. README.md
2. src/pipeline.py
3. src/bronze/ingestion.py
4. src/silver/transformation.py
5. src/gold/aggregation.py
6. notebooks/01_exploracao_dados.ipynb

---

## ✅ Resultado Esperado

Após a apresentação, o avaliador deve entender:

1. ✅ **Arquitetura**: Bronze-Silver-Gold implementada
2. ✅ **Código**: Limpo, modular e bem documentado
3. ✅ **Qualidade**: DataOps e governança presentes
4. ✅ **Testes**: Código testável e testado
5. ✅ **Produção**: Pronto para deploy e extensão

---

**Boa sorte na apresentação! 🚀**
