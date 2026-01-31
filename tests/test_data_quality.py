"""Testes para o módulo de validação de qualidade de dados."""

import pandas as pd
import pytest
import pandera as pa

from src.utils.data_quality import (
    DataQualityValidator,
    clean_column_names,
    remove_duplicates,
)


class TestDataQualityValidator:
    """Testes para o validador de qualidade de dados."""
    
    def test_validate_onibus_data_valid(self):
        """Testa validação com dados válidos."""
        validator = DataQualityValidator()
        
        df = pd.DataFrame({
            "latitude": [-19.9, -19.85, -19.8],
            "longitude": [-43.95, -43.9, -43.85],
            "velocidade": [30.0, 25.5, 40.0],
            "timestamp": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:05", "2024-01-01 10:10"])
        })
        
        validated_df = validator.validate_onibus_data(df)
        assert len(validated_df) == 3
    
    def test_validate_onibus_data_invalid_latitude(self):
        """Testa validação com latitude inválida."""
        validator = DataQualityValidator()
        
        df = pd.DataFrame({
            "latitude": [-25.0, -19.85, -19.8],  # Primeira latitude fora do range
            "longitude": [-43.95, -43.9, -43.85],
            "velocidade": [30.0, 25.5, 40.0],
            "timestamp": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:05", "2024-01-01 10:10"])
        })
        
        with pytest.raises(pa.errors.SchemaError):
            validator.validate_onibus_data(df)
    
    def test_validate_onibus_data_negative_velocity(self):
        """Testa validação com velocidade negativa."""
        validator = DataQualityValidator()
        
        df = pd.DataFrame({
            "latitude": [-19.9, -19.85, -19.8],
            "longitude": [-43.95, -43.9, -43.85],
            "velocidade": [-10.0, 25.5, 40.0],  # Velocidade negativa
            "timestamp": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:05", "2024-01-01 10:10"])
        })
        
        with pytest.raises(pa.errors.SchemaError):
            validator.validate_onibus_data(df)
    
    def test_check_data_quality(self):
        """Testa verificação geral de qualidade."""
        validator = DataQualityValidator()
        
        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": [5, None, 7, 8],
            "col3": [9, 10, 11, 12]
        })
        
        metrics = validator.check_data_quality(df, "test_dataset")
        
        assert metrics["dataset"] == "test_dataset"
        assert metrics["total_rows"] == 4
        assert metrics["total_columns"] == 3
        assert metrics["missing_values"]["col1"] == 1
        assert metrics["missing_values"]["col2"] == 1
        assert metrics["duplicates"] == 0


class TestColumnCleaning:
    """Testes para limpeza de nomes de colunas."""
    
    def test_clean_column_names(self):
        """Testa limpeza de nomes de colunas."""
        df = pd.DataFrame({
            "Column Name": [1, 2],
            "Another-Column": [3, 4],
            "column.with.dots": [5, 6],
            "UPPERCASE": [7, 8]
        })
        
        df_clean = clean_column_names(df)
        
        assert "column_name" in df_clean.columns
        assert "another_column" in df_clean.columns
        assert "column_with_dots" in df_clean.columns
        assert "uppercase" in df_clean.columns


class TestDuplicateRemoval:
    """Testes para remoção de duplicatas."""
    
    def test_remove_duplicates(self):
        """Testa remoção de duplicatas."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 2, 4],
            "value": [10, 20, 30, 20, 40]
        })
        
        df_clean = remove_duplicates(df)
        assert len(df_clean) == 4  # Uma linha removida
    
    def test_remove_duplicates_with_subset(self):
        """Testa remoção de duplicatas com subset."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 2, 4],
            "value": [10, 20, 30, 25, 40]  # Valores diferentes
        })
        
        df_clean = remove_duplicates(df, subset=["id"])
        assert len(df_clean) == 4  # Uma linha removida baseada no id
    
    def test_remove_duplicates_keep_last(self):
        """Testa remoção de duplicatas mantendo última."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 2, 4],
            "value": [10, 20, 30, 25, 40]
        })
        
        df_clean = remove_duplicates(df, subset=["id"], keep="last")
        
        # Verifica se manteve o último registro do id=2
        assert df_clean[df_clean["id"] == 2]["value"].values[0] == 25
