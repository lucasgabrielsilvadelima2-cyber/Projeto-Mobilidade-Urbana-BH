"""
Camada Silver - Limpeza, Padronização e Enriquecimento de Dados.

Este módulo transforma dados brutos da camada Bronze em dados limpos,
padronizados e enriquecidos na camada Silver usando formato Delta Lake.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from deltalake import DeltaTable, write_deltalake

from ..utils.common import DataLineage, get_date_partition_path
from ..utils.data_quality import (
    DataQualityValidator,
    clean_column_names,
    remove_duplicates,
)

logger = logging.getLogger(__name__)


class SilverTransformer:
    """Classe base para transformações da camada Silver."""
    
    def __init__(
        self,
        bronze_path: str = "./data/bronze",
        silver_path: str = "./data/silver"
    ):
        """
        Inicializa o transformador Silver.
        
        Args:
            bronze_path: Caminho da camada Bronze
            silver_path: Caminho da camada Silver
        """
        self.bronze_path = bronze_path
        self.silver_path = silver_path
        self.validator = DataQualityValidator()
        os.makedirs(silver_path, exist_ok=True)
    
    def _save_to_delta(
        self,
        data: pd.DataFrame,
        table_name: str,
        mode: str = "append",
        partition_cols: Optional[List[str]] = None
    ) -> str:
        """
        Salva dados em formato Delta Lake.
        
        Args:
            data: DataFrame a ser salvo
            table_name: Nome da tabela Delta
            mode: Modo de escrita ('append', 'overwrite')
            partition_cols: Colunas para particionamento
        
        Returns:
            Caminho da tabela Delta
        """
        table_path = os.path.join(self.silver_path, table_name)
        
        write_deltalake(
            table_path,
            data,
            mode=mode,
            partition_by=partition_cols
        )
        
        logger.info(f"Dados salvos na tabela Delta: {table_path}")
        logger.info(f"Total de registros: {len(data)}")
        
        return table_path
    
    def _read_latest_bronze(self, dataset_name: str) -> pd.DataFrame:
        """
        Lê os dados mais recentes da camada Bronze.
        
        Args:
            dataset_name: Nome do dataset
        
        Returns:
            DataFrame com os dados
        """
        dataset_path = os.path.join(self.bronze_path, dataset_name)
        
        # Busca todos os arquivos parquet recursivamente
        parquet_files = []
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(".parquet"):
                    parquet_files.append(os.path.join(root, file))
        
        if not parquet_files:
            raise FileNotFoundError(
                f"Nenhum arquivo encontrado em: {dataset_path}"
            )
        
        # Lê o arquivo mais recente
        latest_file = max(parquet_files, key=os.path.getmtime)
        logger.info(f"Lendo arquivo Bronze: {latest_file}")
        
        return pd.read_parquet(latest_file)


class OnibusTransformer(SilverTransformer):
    """Transformador para dados de ônibus em tempo real."""
    
    def transform(self) -> pd.DataFrame:
        """
        Transforma dados de ônibus da Bronze para Silver.
        
        Returns:
            DataFrame transformado
        """
        lineage = DataLineage(
            source="Bronze: onibus_tempo_real",
            operation="transform_to_silver"
        )
        
        try:
            # Lê dados da Bronze
            df = self._read_latest_bronze("onibus_tempo_real")
            lineage.add_metadata("input_records", len(df))
            
            # Limpa nomes de colunas
            df = clean_column_names(df)
            
            # Mapeamento de colunas (ajustar conforme estrutura real da API)
            column_mapping = {
                "lat": "latitude",
                "lon": "longitude",
                "vel": "velocidade",
                "linha": "numero_linha",
                "timestamp": "timestamp",
                "veiculo": "codigo_veiculo",
            }
            
            # Renomeia colunas existentes
            existing_columns = {k: v for k, v in column_mapping.items() 
                              if k in df.columns}
            if existing_columns:
                df = df.rename(columns=existing_columns)
            
            # Conversões de tipo
            if "latitude" in df.columns:
                df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
            if "longitude" in df.columns:
                df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
            if "velocidade" in df.columns:
                df["velocidade"] = pd.to_numeric(df["velocidade"], errors="coerce")
            
            # Converte timestamp
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            else:
                df["timestamp"] = df["_ingestion_timestamp"]
            
            # Remove valores nulos críticos
            initial_count = len(df)
            df = df.dropna(subset=["latitude", "longitude", "timestamp"])
            dropped = initial_count - len(df)
            if dropped > 0:
                logger.warning(f"Removidos {dropped} registros com valores nulos críticos")
            
            # Remove coordenadas inválidas (0.0, ou fora da região de BH)
            initial_count = len(df)
            df = df[
                (df["latitude"] != 0.0) & 
                (df["longitude"] != 0.0) &
                (df["latitude"].between(-20.1, -19.7)) &
                (df["longitude"].between(-44.15, -43.8))
            ]
            dropped_coords = initial_count - len(df)
            if dropped_coords > 0:
                logger.warning(f"Removidos {dropped_coords} registros com coordenadas inválidas")
            
            # Remove duplicatas
            df = remove_duplicates(
                df,
                subset=["codigo_veiculo", "timestamp"] 
                      if "codigo_veiculo" in df.columns else None
            )
            
            # Adiciona colunas derivadas
            df["data"] = df["timestamp"].dt.date
            df["hora"] = df["timestamp"].dt.hour
            df["dia_semana"] = df["timestamp"].dt.dayofweek
            df["periodo_dia"] = df["hora"].apply(self._classify_period)
            
            # Valida dados se as colunas necessárias existirem
            required_cols = ["latitude", "longitude", "velocidade", "timestamp"]
            has_required = all(col in df.columns for col in required_cols)
            
            if has_required:
                logger.info("🔍 Executando validações de qualidade de dados...")
                df = self.validator.validate_onibus_data(df)
                logger.info("✓ Validações concluídas com sucesso")
            else:
                missing = [col for col in required_cols if col not in df.columns]
                logger.warning(f"⚠️  Colunas ausentes para validação completa: {missing}")
            
            # Adiciona metadados de transformação
            df["_processed_timestamp"] = datetime.now()
            df["_quality_score"] = self._calculate_quality_score(df)
            
            lineage.add_metadata("output_records", len(df))
            lineage.add_metadata("dropped_records", dropped)
            
            logger.info(f"Transformação concluída: {len(df)} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na transformação: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """
        Carrega dados transformados na camada Silver.
        
        Args:
            data: DataFrame transformado
        
        Returns:
            Caminho da tabela Delta
        """
        return self._save_to_delta(
            data,
            "onibus_posicoes",
            mode="append",
            partition_cols=["data"]
        )
    
    @staticmethod
    def _classify_period(hour: int) -> str:
        """Classifica período do dia baseado na hora."""
        if 5 <= hour < 12:
            return "manha"
        elif 12 <= hour < 18:
            return "tarde"
        elif 18 <= hour < 22:
            return "noite"
        else:
            return "madrugada"
    
    @staticmethod
    def _calculate_quality_score(df: pd.DataFrame) -> float:
        """
        Calcula score de qualidade dos dados.
        
        Args:
            df: DataFrame a ser avaliado
        
        Returns:
            Score de qualidade (0-1)
        """
        # Verifica completude
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        
        # Verifica coordenadas válidas (dentro de BH)
        if "latitude" in df.columns and "longitude" in df.columns:
            valid_coords = (
                (df["latitude"].between(-20.0, -19.7)) &
                (df["longitude"].between(-44.1, -43.8))
            ).mean()
        else:
            valid_coords = 0.5
        
        # Score combinado
        score = (completeness * 0.6 + valid_coords * 0.4)
        return round(score, 3)


class MCOTransformer(SilverTransformer):
    """Transformador para dados do MCO."""
    
    def transform(self) -> pd.DataFrame:
        """
        Transforma dados do MCO da Bronze para Silver.
        
        Returns:
            DataFrame transformado
        """
        lineage = DataLineage(
            source="Bronze: mco",
            operation="transform_to_silver"
        )
        
        try:
            # Lê dados da Bronze
            df = self._read_latest_bronze("mco")
            lineage.add_metadata("input_records", len(df))
            
            # Limpa nomes de colunas
            df = clean_column_names(df)
            
            # Remove duplicatas
            df = remove_duplicates(df)
            
            # Valida dados
            df = self.validator.validate_mco_data(df)
            
            # Adiciona metadados de transformação
            df["_processed_timestamp"] = datetime.now()
            
            lineage.add_metadata("output_records", len(df))
            logger.info(f"Transformação MCO concluída: {len(df)} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na transformação MCO: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """
        Carrega dados transformados na camada Silver.
        
        Args:
            data: DataFrame transformado
        
        Returns:
            Caminho da tabela Delta
        """
        return self._save_to_delta(
            data,
            "mco_linhas",
            mode="overwrite"  # MCO é sobrescrito (dimensão)
        )


def transform_all_sources(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Executa transformação de todas as fontes de dados.
    
    Args:
        config: Dicionário de configuração
    
    Returns:
        Dicionário com caminhos das tabelas Delta criadas
    """
    results = {}
    
    # Transformação de ônibus (somente se habilitado)
    if config.get("data_sources", {}).get("onibus_tempo_real", {}).get("enabled", False):
        try:
            onibus_transformer = OnibusTransformer(
                bronze_path=config["layers"]["bronze"]["path"],
                silver_path=config["layers"]["silver"]["path"]
            )
            df_onibus = onibus_transformer.transform()
            results["onibus_posicoes"] = onibus_transformer.load(df_onibus)
        except Exception as e:
            logger.error(f"Falha na transformação de ônibus: {e}")
            results["onibus_posicoes"] = f"ERROR: {e}"
    else:
        logger.info("Transformação de ônibus desabilitada na configuração")
    
    # Transformação do MCO (somente se habilitado)
    if config.get("data_sources", {}).get("mco", {}).get("enabled", False):
        try:
            mco_transformer = MCOTransformer(
                bronze_path=config["layers"]["bronze"]["path"],
                silver_path=config["layers"]["silver"]["path"]
            )
            df_mco = mco_transformer.transform()
            results["mco_linhas"] = mco_transformer.load(df_mco)
        except Exception as e:
            logger.error(f"Falha na transformação do MCO: {e}")
            results["mco_linhas"] = f"ERROR: {e}"
    else:
        logger.info("Transformação do MCO desabilitada na configuração")
    
    return results
