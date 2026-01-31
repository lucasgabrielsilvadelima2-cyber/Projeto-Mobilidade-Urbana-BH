"""
Módulo de Validação e Qualidade de Dados.

Implementa validações e testes de qualidade usando Great Expectations e Pandera.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Validador de qualidade de dados."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o validador.
        
        Args:
            config: Configurações de validação
        """
        self.config = config or {}
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_onibus_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida dados de ônibus em tempo real.
        
        Args:
            df: DataFrame com dados de ônibus
        
        Returns:
            DataFrame validado
        
        Raises:
            pa.errors.SchemaError: Se os dados não passarem na validação
        """
        schema = DataFrameSchema({
            "latitude": Column(
                float,
                checks=[
                    Check.in_range(-20.0, -19.7),
                    Check(lambda s: ~s.isna(), error="Latitude não pode ser nula")
                ],
                nullable=False
            ),
            "longitude": Column(
                float,
                checks=[
                    Check.in_range(-44.1, -43.8),
                    Check(lambda s: ~s.isna(), error="Longitude não pode ser nula")
                ],
                nullable=False
            ),
            "velocidade": Column(
                float,
                checks=[
                    Check.greater_than_or_equal_to(0),
                    Check.less_than_or_equal_to(120)
                ],
                nullable=True
            ),
            "timestamp": Column(
                pa.DateTime,
                nullable=False
            ),
        })
        
        try:
            validated_df = schema.validate(df)
            logger.info(f"Validação bem-sucedida: {len(df)} registros")
            self._log_validation_success("onibus_tempo_real", len(df))
            return validated_df
        except pa.errors.SchemaError as e:
            logger.error(f"Erro de validação: {e}")
            self._log_validation_failure("onibus_tempo_real", str(e))
            raise
    
    def validate_mco_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida dados do MCO (Mapa de Controle Operacional).
        
        Args:
            df: DataFrame com dados do MCO
        
        Returns:
            DataFrame validado
        """
        # Schema básico para MCO
        schema = DataFrameSchema({
            "linha": Column(str, nullable=False),
            "tipo_dia": Column(str, nullable=True),
        }, strict=False)  # Permite colunas adicionais
        
        try:
            validated_df = schema.validate(df)
            logger.info(f"Validação MCO bem-sucedida: {len(df)} registros")
            self._log_validation_success("mco", len(df))
            return validated_df
        except pa.errors.SchemaError as e:
            logger.error(f"Erro de validação MCO: {e}")
            self._log_validation_failure("mco", str(e))
            raise
    
    def check_data_quality(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Realiza verificações gerais de qualidade de dados.
        
        Args:
            df: DataFrame a ser verificado
            dataset_name: Nome do dataset
        
        Returns:
            Dicionário com métricas de qualidade
        """
        quality_metrics = {
            "dataset": dataset_name,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicates": df.duplicated().sum(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        logger.info(f"Métricas de qualidade para {dataset_name}: {quality_metrics}")
        return quality_metrics
    
    def _log_validation_success(self, dataset: str, row_count: int) -> None:
        """Registra validação bem-sucedida."""
        self.validation_results.append({
            "dataset": dataset,
            "status": "success",
            "row_count": row_count,
            "timestamp": pd.Timestamp.now()
        })
    
    def _log_validation_failure(self, dataset: str, error: str) -> None:
        """Registra falha na validação."""
        self.validation_results.append({
            "dataset": dataset,
            "status": "failure",
            "error": error,
            "timestamp": pd.Timestamp.now()
        })
    
    def get_validation_report(self) -> pd.DataFrame:
        """
        Retorna relatório de todas as validações.
        
        Returns:
            DataFrame com histórico de validações
        """
        if not self.validation_results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.validation_results)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza nomes de colunas.
    
    Args:
        df: DataFrame original
    
    Returns:
        DataFrame com colunas renomeadas
    """
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(".", "_")
        .str.replace("/", "_")
    )
    return df


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = "first"
) -> pd.DataFrame:
    """
    Remove registros duplicados.
    
    Args:
        df: DataFrame original
        subset: Lista de colunas para considerar na duplicação
        keep: Qual duplicata manter ('first', 'last', False)
    
    Returns:
        DataFrame sem duplicatas
    """
    initial_count = len(df)
    df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
    removed_count = initial_count - len(df_cleaned)
    
    if removed_count > 0:
        logger.warning(f"Removidos {removed_count} registros duplicados")
    
    return df_cleaned
