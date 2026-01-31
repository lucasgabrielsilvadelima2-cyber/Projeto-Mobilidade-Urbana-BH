"""
Camada Gold - Agregações e Métricas de Negócio.

Este módulo cria tabelas analíticas agregadas com métricas de negócio
otimizadas para análise e visualização.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from deltalake import DeltaTable, write_deltalake

from ..utils.common import DataLineage

logger = logging.getLogger(__name__)


class GoldAggregator:
    """Classe base para agregações da camada Gold."""
    
    def __init__(
        self,
        silver_path: str = "./data/silver",
        gold_path: str = "./data/gold"
    ):
        """
        Inicializa o agregador Gold.
        
        Args:
            silver_path: Caminho da camada Silver
            gold_path: Caminho da camada Gold
        """
        self.silver_path = silver_path
        self.gold_path = gold_path
        os.makedirs(gold_path, exist_ok=True)
    
    def _read_silver_table(self, table_name: str) -> pd.DataFrame:
        """
        Lê tabela Delta da camada Silver.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            DataFrame com os dados
        """
        table_path = os.path.join(self.silver_path, table_name)
        
        try:
            dt = DeltaTable(table_path)
            df = dt.to_pandas()
            logger.info(f"Lida tabela Silver: {table_name} ({len(df)} registros)")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler tabela {table_name}: {e}")
            raise
    
    def _save_to_delta(
        self,
        data: pd.DataFrame,
        table_name: str,
        mode: str = "overwrite"
    ) -> str:
        """
        Salva dados em formato Delta Lake.
        
        Args:
            data: DataFrame a ser salvo
            table_name: Nome da tabela Delta
            mode: Modo de escrita ('append', 'overwrite')
        
        Returns:
            Caminho da tabela Delta
        """
        table_path = os.path.join(self.gold_path, table_name)
        
        write_deltalake(
            table_path,
            data,
            mode=mode,
            engine="pyarrow"
        )
        
        logger.info(f"Tabela Gold criada: {table_path}")
        logger.info(f"Total de registros: {len(data)}")
        
        return table_path


class VelocidadeMediaPorLinhaAggregator(GoldAggregator):
    """Agrega velocidade média por linha de ônibus."""
    
    def aggregate(self) -> pd.DataFrame:
        """
        Calcula velocidade média por linha.
        
        Returns:
            DataFrame com agregações
        """
        lineage = DataLineage(
            source="Silver: onibus_posicoes",
            operation="aggregate_velocidade_por_linha"
        )
        
        try:
            df = self._read_silver_table("onibus_posicoes")
            lineage.add_metadata("input_records", len(df))
            
            # Verifica colunas necessárias
            required_cols = ["data", "velocidade"]
            if "numero_linha" in df.columns:
                required_cols.append("numero_linha")
            
            # Filtra registros válidos
            df_valid = df[df["velocidade"].notna()].copy()
            
            # Agrupamento
            group_cols = ["data"]
            if "numero_linha" in df.columns:
                group_cols.insert(0, "numero_linha")
            
            agg_df = df_valid.groupby(group_cols).agg(
                velocidade_media=("velocidade", "mean"),
                velocidade_mediana=("velocidade", "median"),
                velocidade_max=("velocidade", "max"),
                velocidade_min=("velocidade", "min"),
                total_registros=("velocidade", "count"),
                desvio_padrao=("velocidade", "std")
            ).reset_index()
            
            # Arredonda valores
            agg_df["velocidade_media"] = agg_df["velocidade_media"].round(2)
            agg_df["velocidade_mediana"] = agg_df["velocidade_mediana"].round(2)
            agg_df["desvio_padrao"] = agg_df["desvio_padrao"].round(2)
            
            # Adiciona metadados
            agg_df["_created_at"] = datetime.now()
            
            lineage.add_metadata("output_records", len(agg_df))
            logger.info(f"Agregação concluída: {len(agg_df)} grupos")
            
            return agg_df
            
        except Exception as e:
            logger.error(f"Erro na agregação: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """Carrega dados agregados na Gold."""
        return self._save_to_delta(data, "velocidade_media_por_linha")


class OnibusAtivosPorPeriodoAggregator(GoldAggregator):
    """Agrega total de ônibus ativos por período."""
    
    def aggregate(self) -> pd.DataFrame:
        """
        Calcula total de ônibus ativos por período.
        
        Returns:
            DataFrame com agregações
        """
        lineage = DataLineage(
            source="Silver: onibus_posicoes",
            operation="aggregate_onibus_ativos"
        )
        
        try:
            df = self._read_silver_table("onibus_posicoes")
            lineage.add_metadata("input_records", len(df))
            
            # Agrupamento por data e hora
            group_cols = ["data", "hora"]
            if "periodo_dia" in df.columns:
                group_cols.append("periodo_dia")
            
            if "codigo_veiculo" in df.columns:
                agg_df = df.groupby(group_cols).agg(
                    total_onibus_unicos=("codigo_veiculo", "nunique"),
                    total_registros=("codigo_veiculo", "count")
                ).reset_index()
            else:
                agg_df = df.groupby(group_cols).agg(
                    total_registros=("latitude", "count")
                ).reset_index()
                agg_df["total_onibus_unicos"] = None
            
            # Adiciona dia da semana
            if "dia_semana" in df.columns:
                day_mapping = df.groupby(group_cols)["dia_semana"].first()
                agg_df = agg_df.merge(
                    day_mapping.reset_index(),
                    on=group_cols,
                    how="left"
                )
            
            # Adiciona metadados
            agg_df["_created_at"] = datetime.now()
            
            lineage.add_metadata("output_records", len(agg_df))
            logger.info(f"Agregação concluída: {len(agg_df)} períodos")
            
            return agg_df
            
        except Exception as e:
            logger.error(f"Erro na agregação: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """Carrega dados agregados na Gold."""
        return self._save_to_delta(data, "onibus_ativos_por_periodo")


class CoberturaGeograficaAggregator(GoldAggregator):
    """Analisa cobertura geográfica das linhas."""
    
    def aggregate(self) -> pd.DataFrame:
        """
        Calcula métricas de cobertura geográfica.
        
        Returns:
            DataFrame com agregações
        """
        lineage = DataLineage(
            source="Silver: onibus_posicoes",
            operation="aggregate_cobertura_geografica"
        )
        
        try:
            df = self._read_silver_table("onibus_posicoes")
            lineage.add_metadata("input_records", len(df))
            
            # Filtra coordenadas válidas
            df_valid = df[
                df["latitude"].notna() & 
                df["longitude"].notna()
            ].copy()
            
            # Agrupamento por linha (se disponível)
            if "numero_linha" in df.columns:
                group_col = "numero_linha"
            else:
                group_col = None
            
            if group_col:
                agg_df = df_valid.groupby(group_col).agg(
                    lat_min=("latitude", "min"),
                    lat_max=("latitude", "max"),
                    lon_min=("longitude", "min"),
                    lon_max=("longitude", "max"),
                    lat_media=("latitude", "mean"),
                    lon_media=("longitude", "mean"),
                    total_pontos=("latitude", "count")
                ).reset_index()
                
                # Calcula área de cobertura aproximada (graus²)
                agg_df["area_cobertura"] = (
                    (agg_df["lat_max"] - agg_df["lat_min"]) *
                    (agg_df["lon_max"] - agg_df["lon_min"])
                ).round(6)
            else:
                # Agregação geral
                agg_df = pd.DataFrame([{
                    "lat_min": df_valid["latitude"].min(),
                    "lat_max": df_valid["latitude"].max(),
                    "lon_min": df_valid["longitude"].min(),
                    "lon_max": df_valid["longitude"].max(),
                    "lat_media": df_valid["latitude"].mean(),
                    "lon_media": df_valid["longitude"].mean(),
                    "total_pontos": len(df_valid),
                    "area_cobertura": (
                        (df_valid["latitude"].max() - df_valid["latitude"].min()) *
                        (df_valid["longitude"].max() - df_valid["longitude"].min())
                    )
                }])
            
            # Adiciona metadados
            agg_df["_created_at"] = datetime.now()
            
            lineage.add_metadata("output_records", len(agg_df))
            logger.info(f"Agregação concluída: {len(agg_df)} grupos")
            
            return agg_df
            
        except Exception as e:
            logger.error(f"Erro na agregação: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """Carrega dados agregados na Gold."""
        return self._save_to_delta(data, "cobertura_geografica")


class PontosCriticosVelocidadeAggregator(GoldAggregator):
    """Identifica pontos críticos com baixa velocidade."""
    
    def aggregate(self, threshold_velocity: float = 10.0) -> pd.DataFrame:
        """
        Identifica pontos com velocidade abaixo do limite.
        
        Args:
            threshold_velocity: Velocidade limite (km/h)
        
        Returns:
            DataFrame com pontos críticos
        """
        lineage = DataLineage(
            source="Silver: onibus_posicoes",
            operation="identify_pontos_criticos"
        )
        
        try:
            df = self._read_silver_table("onibus_posicoes")
            lineage.add_metadata("input_records", len(df))
            
            # Filtra velocidades baixas
            df_slow = df[
                (df["velocidade"].notna()) &
                (df["velocidade"] < threshold_velocity)
            ].copy()
            
            # Arredonda coordenadas para criar "grids"
            df_slow["lat_grid"] = (df_slow["latitude"] * 100).round() / 100
            df_slow["lon_grid"] = (df_slow["longitude"] * 100).round() / 100
            
            # Agrega por grid
            agg_df = df_slow.groupby(["lat_grid", "lon_grid"]).agg(
                ocorrencias=("velocidade", "count"),
                velocidade_media=("velocidade", "mean"),
                velocidade_min=("velocidade", "min")
            ).reset_index()
            
            # Ordena por mais críticos
            agg_df = agg_df.sort_values("ocorrencias", ascending=False)
            
            # Adiciona severidade
            agg_df["severidade"] = pd.cut(
                agg_df["ocorrencias"],
                bins=[0, 10, 50, 100, float("inf")],
                labels=["baixa", "media", "alta", "critica"]
            )
            
            # Adiciona metadados
            agg_df["_created_at"] = datetime.now()
            agg_df["_threshold_velocity"] = threshold_velocity
            
            lineage.add_metadata("output_records", len(agg_df))
            lineage.add_metadata("threshold_velocity", threshold_velocity)
            logger.info(f"Identificados {len(agg_df)} pontos críticos")
            
            return agg_df
            
        except Exception as e:
            logger.error(f"Erro na agregação: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """Carrega dados agregados na Gold."""
        return self._save_to_delta(data, "pontos_criticos_velocidade")


def aggregate_all_metrics(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Executa todas as agregações da camada Gold.
    
    Args:
        config: Dicionário de configuração
    
    Returns:
        Dicionário com caminhos das tabelas criadas
    """
    results = {}
    silver_path = config["layers"]["silver"]["path"]
    gold_path = config["layers"]["gold"]["path"]
    
    # Velocidade média por linha
    try:
        agg = VelocidadeMediaPorLinhaAggregator(silver_path, gold_path)
        df = agg.aggregate()
        results["velocidade_media_por_linha"] = agg.load(df)
    except Exception as e:
        logger.error(f"Falha na agregação de velocidade: {e}")
        results["velocidade_media_por_linha"] = f"ERROR: {e}"
    
    # Ônibus ativos por período
    try:
        agg = OnibusAtivosPorPeriodoAggregator(silver_path, gold_path)
        df = agg.aggregate()
        results["onibus_ativos_por_periodo"] = agg.load(df)
    except Exception as e:
        logger.error(f"Falha na agregação de ônibus ativos: {e}")
        results["onibus_ativos_por_periodo"] = f"ERROR: {e}"
    
    # Cobertura geográfica
    try:
        agg = CoberturaGeograficaAggregator(silver_path, gold_path)
        df = agg.aggregate()
        results["cobertura_geografica"] = agg.load(df)
    except Exception as e:
        logger.error(f"Falha na agregação de cobertura: {e}")
        results["cobertura_geografica"] = f"ERROR: {e}"
    
    # Pontos críticos
    try:
        agg = PontosCriticosVelocidadeAggregator(silver_path, gold_path)
        df = agg.aggregate(threshold_velocity=10.0)
        results["pontos_criticos_velocidade"] = agg.load(df)
    except Exception as e:
        logger.error(f"Falha na agregação de pontos críticos: {e}")
        results["pontos_criticos_velocidade"] = f"ERROR: {e}"
    
    return results
