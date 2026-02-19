# 📖 Dicionário de Dados - Camada Gold

## Visão Geral

Este documento detalha o schema e descrição de todas as tabelas da **Camada Gold**, prontas para consumo em ferramentas de BI (Power BI, Tableau, Looker) e modelos de Machine Learning.

**Formato**: Delta Lake  
**Localização**: `data/gold/`  
**Atualização**: A cada execução do pipeline (~tempo real)

---

## 📊 Tabelas Disponíveis

1. [velocidade_media_por_linha](#1-velocidade_media_por_linha)
2. [onibus_ativos_por_periodo](#2-onibus_ativos_por_periodo)
3. [cobertura_geografica](#3-cobertura_geografica)
4. [pontos_criticos_velocidade](#4-pontos_criticos_velocidade)

---

## 1. velocidade_media_por_linha

**Descrição**: Métricas de velocidade agregadas por linha de ônibus e data.

**Caso de Uso**:
- Análise de desempenho operacional por linha
- Identificação de linhas lentas
- Comparação de velocidades entre linhas
- Inputs para modelos de previsão de tempo de viagem

**Schema**:

| Coluna | Tipo | Nulável | Descrição | Exemplo |
|--------|------|---------|-----------|---------|
| `numero_linha` | string | ❌ | Código identificador da linha | "6016", "870" |
| `data` | date | ❌ | Data da agregação | 2026-02-18 |
| `velocidade_media` | float | ❌ | Velocidade média em km/h | 25.5 |
| `velocidade_mediana` | float | ❌ | Velocidade mediana em km/h | 23.0 |
| `velocidade_max` | float | ❌ | Velocidade máxima registrada em km/h | 65.0 |
| `velocidade_min` | float | ❌ | Velocidade mínima registrada em km/h | 0.0 |
| `desvio_padrao` | float | ✅ | Desvio padrão da velocidade | 12.3 |
| `total_registros` | integer | ❌ | Quantidade de medições | 450 |
| `_created_at` | timestamp | ❌ | Timestamp de criação do registro | 2026-02-18 18:27:28 |

**Chave Primária**: (`numero_linha`, `data`)

**Exemplo de Query SQL**:
```sql
SELECT 
    numero_linha,
    velocidade_media,
    velocidade_max,
    total_registros
FROM velocidade_media_por_linha
WHERE data = CURRENT_DATE()
ORDER BY velocidade_media ASC
LIMIT 10;  -- Top 10 linhas mais lentas
```

**Exemplo de Uso em Python**:
```python
from deltalake import DeltaTable

# Ler tabela
dt = DeltaTable("data/gold/velocidade_media_por_linha")
df = dt.to_pandas()

# Análise
linhas_lentas = df[df['velocidade_media'] < 15]
print(f"Linhas com velocidade < 15 km/h: {len(linhas_lentas)}")
```

---

## 2. onibus_ativos_por_periodo

**Descrição**: Quantidade de ônibus ativos agregados por data, hora e período do dia.

**Caso de Uso**:
- Análise de disponibilidade de frota
- Planejamento de escalas
- Identificação de horários de pico
- Dimensionamento de frota

**Schema**:

| Coluna | Tipo | Nulável | Descrição | Exemplo |
|--------|------|---------|-----------|---------|
| `data` | date | ❌ | Data da agregação | 2026-02-18 |
| `hora` | integer | ❌ | Hora do dia (0-23) | 18 |
| `periodo_dia` | string | ✅ | Classificação de período | "tarde", "noite" |
| `total_onibus_unicos` | integer | ❌ | Quantidade de ônibus únicos ativos | 245 |
| `total_registros` | integer | ❌ | Total de registros GPS recebidos | 2450 |
| `dia_semana` | integer | ✅ | Dia da semana (0=Segunda, 6=Domingo) | 1 |
| `_created_at` | timestamp | ❌ | Timestamp de criação do registro | 2026-02-18 18:27:28 |

**Chave Primária**: (`data`, `hora`)

**Valores Possíveis**:
- `periodo_dia`: "madrugada" (0h-6h), "manha" (6h-12h), "tarde" (12h-18h), "noite" (18h-24h)
- `dia_semana`: 0-6 (0=Segunda, 1=Terça, ..., 6=Domingo)

**Exemplo de Query SQL**:
```sql
SELECT 
    hora,
    periodo_dia,
    AVG(total_onibus_unicos) as frota_media
FROM onibus_ativos_por_periodo
WHERE data >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY hora, periodo_dia
ORDER BY hora;
```

**Visualização Recomendada**: Gráfico de linha mostrando frota ativa ao longo do dia

---

## 3. cobertura_geografica

**Descrição**: Análise de cobertura geográfica por linha de ônibus.

**Caso de Uso**:
- Planejamento de rotas
- Análise de abrangência territorial
- Identificação de áreas não cobertas
- Otimização de linhas

**Schema**:

| Coluna | Tipo | Nulável | Descrição | Exemplo |
|--------|------|---------|-----------|---------|
| `numero_linha` | string | ❌ | Código identificador da linha | "6016" |
| `data` | date | ❌ | Data da agregação | 2026-02-18 |
| `latitude_min` | float | ❌ | Latitude mínima da rota | -20.05 |
| `latitude_max` | float | ❌ | Latitude máxima da rota | -19.85 |
| `longitude_min` | float | ❌ | Longitude mínima da rota | -44.10 |
| `longitude_max` | float | ❌ | Longitude máxima da rota | -43.90 |
| `latitude_centro` | float | ❌ | Latitude do ponto central | -19.95 |
| `longitude_centro` | float | ❌ | Longitude do ponto central | -44.00 |
| `area_cobertura_km2` | float | ✅ | Área aproximada de cobertura em km² | 25.5 |
| `pontos_unicos` | integer | ❌ | Quantidade de pontos únicos visitados | 450 |
| `_created_at` | timestamp | ❌ | Timestamp de criação do registro | 2026-02-18 18:27:28 |

**Chave Primária**: (`numero_linha`, `data`)

**Notas**:
- Coordenadas em formato decimal (WGS84)
- `area_cobertura_km2`: Calculada aproximadamente pelo bounding box

**Exemplo de Query SQL**:
```sql
SELECT 
    numero_linha,
    latitude_centro,
    longitude_centro,
    area_cobertura_km2,
    pontos_unicos
FROM cobertura_geografica
WHERE data = CURRENT_DATE()
ORDER BY area_cobertura_km2 DESC
LIMIT 10;  -- Linhas com maior cobertura
```

**Uso em Mapas**:
```python
import folium

# Criar mapa com coberturas
mapa = folium.Map(location=[-19.92, -43.93], zoom_start=12)

for _, linha in df.iterrows():
    folium.Marker(
        location=[linha['latitude_centro'], linha['longitude_centro']],
        popup=f"Linha {linha['numero_linha']}",
        icon=folium.Icon(color='blue')
    ).add_to(mapa)
```

---

## 4. pontos_criticos_velocidade

**Descrição**: Identificação de pontos geográficos com velocidade crítica (baixa).

**Caso de Uso**:
- Identificação de gargalos no trânsito
- Planejamento de infraestrutura
- Análise de congestionamentos
- Otimização de semáforos

**Schema**:

| Coluna | Tipo | Nulável | Descrição | Exemplo |
|--------|------|---------|-----------|---------|
| `grid_id` | string | ❌ | Identificador da célula do grid | "lat_-19.95_lon_-44.00" |
| `data` | date | ❌ | Data da agregação | 2026-02-18 |
| `latitude_grid` | float | ❌ | Latitude central do grid | -19.95 |
| `longitude_grid` | float | ❌ | Longitude central do grid | -44.00 |
| `velocidade_media` | float | ❌ | Velocidade média no grid em km/h | 8.5 |
| `classificacao` | string | ❌ | Classificação da severidade | "crítico" |
| `total_passagens` | integer | ❌ | Quantidade de ônibus que passaram | 120 |
| `hora_pico` | integer | ✅ | Hora com mais congestionamento | 18 |
| `_created_at` | timestamp | ❌ | Timestamp de criação do registro | 2026-02-18 18:27:28 |

**Chave Primária**: (`grid_id`, `data`)

**Valores Possíveis**:
- `classificacao`: 
  - "crítico" (velocidade < 10 km/h)
  - "alto" (10-15 km/h)
  - "moderado" (15-20 km/h)
  - "normal" (> 20 km/h)

**Grid**:
- Tamanho: ~0.01 graus (~1.1km)
- Formato ID: "lat_{lat}_lon_{lon}"

**Exemplo de Query SQL**:
```sql
SELECT 
    grid_id,
    latitude_grid,
    longitude_grid,
    velocidade_media,
    classificacao,
    total_passagens
FROM pontos_criticos_velocidade
WHERE data = CURRENT_DATE()
  AND classificacao IN ('crítico', 'alto')
ORDER BY velocidade_media ASC
LIMIT 20;  -- Top 20 pontos mais críticos
```

**Visualização em Mapa de Calor**:
```python
import folium
from folium.plugins import HeatMap

# Dados de pontos críticos
pontos = df[df['classificacao'] == 'crítico']

# Criar mapa de calor
heat_data = [[row['latitude_grid'], row['longitude_grid'], 
              1/row['velocidade_media']] for _, row in pontos.iterrows()]

mapa = folium.Map(location=[-19.92, -43.93], zoom_start=12)
HeatMap(heat_data).add_to(mapa)
mapa.save('pontos_criticos.html')
```

---

## 🔄 Atualização de Dados

**Frequência**: Cada execução do pipeline  
**Método**: Overwrite (substituição completa)  
**Histórico**: Dados anteriores não são mantidos por padrão

Para manter histórico:
```python
# Alterar mode em aggregation.py
write_deltalake(table_path, data, mode="append")  # ao invés de "overwrite"
```

---

## 📊 Relacionamentos

```
┌──────────────────────────┐
│ velocidade_media_por_linha│
└────────┬─────────────────┘
         │
         │ numero_linha
         │
         ▼
┌──────────────────────────┐
│ cobertura_geografica      │
└───────────────────────────┘

┌──────────────────────────┐
│ onibus_ativos_por_periodo │  (Agregação temporal)
└───────────────────────────┘

┌──────────────────────────┐
│ pontos_criticos_velocidade│  (Agregação geográfica)
└───────────────────────────┘
```

**Join Exemplo**:
```sql
SELECT 
    v.numero_linha,
    v.velocidade_media,
    c.area_cobertura_km2,
    c.pontos_unicos
FROM velocidade_media_por_linha v
JOIN cobertura_geografica c 
  ON v.numero_linha = c.numero_linha 
  AND v.data = c.data
WHERE v.data = CURRENT_DATE()
ORDER BY v.velocidade_media ASC;
```

---

## 🎯 Casos de Uso por Tabela

### Business Intelligence

| Tabela | Dashboard Recomendado |
|--------|----------------------|
| `velocidade_media_por_linha` | KPI: Velocidade média da frota, Comparativo de linhas |
| `onibus_ativos_por_periodo` | Gráfico: Frota ativa por hora do dia |
| `cobertura_geografica` | Mapa: Cobertura territorial por linha |
| `pontos_criticos_velocidade` | Mapa de calor: Gargalos de trânsito |

### Machine Learning

| Tabela | Modelo Sugerido |
|--------|----------------|
| `velocidade_media_por_linha` | Previsão de tempo de viagem |
| `onibus_ativos_por_periodo` | Otimização de escala de frota |
| `cobertura_geografica` | Planejamento de novas rotas |
| `pontos_criticos_velocidade` | Predição de congestionamentos |

---

## 📝 Notas Técnicas

1. **Formato Delta Lake**: Suporta ACID transactions, time travel, schema evolution
2. **Compressão**: Snappy (padrão Delta Lake)
3. **Particionamento**: Não particionado (volumes pequenos)
4. **Encoding**: UTF-8
5. **Timezone**: UTC para timestamps

---

## 🔗 Referências

- [Código fonte agregações](../src/gold/aggregation.py)
- [Arquitetura](ARCHITECTURE.md)
- [Portal Dados Abertos BH](https://dados.pbh.gov.br/group/mobilidade-urbana)

---

**Versão**: 1.0  
**Última atualização**: 18/02/2026  
**Contato**: Pipeline BH Mobilidade Team
