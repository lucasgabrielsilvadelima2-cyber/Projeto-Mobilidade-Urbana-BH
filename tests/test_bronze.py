"""Testes para o módulo de ingestão Bronze."""

import os
import tempfile
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.bronze.ingestion import (
    BronzeDataIngester,
    MCOIngester,
    OnibusTempoRealIngester,
)


class TestBronzeDataIngester:
    """Testes para a classe base BronzeDataIngester."""
    
    def test_ingester_initialization(self):
        """Testa inicialização do ingestor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ingester = BronzeDataIngester(output_path=tmpdir)
            assert ingester.output_path == tmpdir
            assert ingester.session is not None
    
    def test_save_to_parquet(self):
        """Testa salvamento em formato Parquet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ingester = BronzeDataIngester(output_path=tmpdir)
            
            df = pd.DataFrame({
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"]
            })
            
            file_path = ingester._save_to_parquet(df, "test_dataset")
            
            assert os.path.exists(file_path)
            assert file_path.endswith(".parquet")
            
            # Verifica se pode ler o arquivo
            df_read = pd.read_parquet(file_path)
            assert len(df_read) == 3


class TestOnibusTempoRealIngester:
    """Testes para ingestão de dados de ônibus."""
    
    @patch("requests.Session.get")
    def test_extract_success(self, mock_get):
        """Testa extração bem-sucedida de dados."""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"lat": -19.9, "lon": -43.9, "vel": 30},
            {"lat": -19.85, "lon": -43.85, "vel": 25}
        ]
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ingester = OnibusTempoRealIngester(output_path=tmpdir)
            df = ingester.extract()
            
            assert len(df) == 2
            assert "_ingestion_timestamp" in df.columns
            assert "_source" in df.columns
    
    @patch("requests.Session.get")
    def test_extract_with_data_wrapper(self, mock_get):
        """Testa extração com dados em wrapper."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"lat": -19.9, "lon": -43.9, "vel": 30}
            ]
        }
        mock_response.content = b"test"
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ingester = OnibusTempoRealIngester(output_path=tmpdir)
            df = ingester.extract()
            
            assert len(df) == 1


class TestMCOIngester:
    """Testes para ingestão de dados do MCO."""
    
    def test_extract_from_local_file(self):
        """Testa extração de arquivo local."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Cria arquivo CSV de teste
            test_file = os.path.join(tmpdir, "test_mco.csv")
            test_df = pd.DataFrame({
                "linha": ["101", "102", "103"],
                "tipo_dia": ["util", "util", "sabado"]
            })
            test_df.to_csv(test_file, sep=";", index=False)
            
            ingester = MCOIngester(output_path=tmpdir)
            df = ingester.extract(file_path=test_file)
            
            assert len(df) == 3
            assert "_ingestion_timestamp" in df.columns
            assert "_source" in df.columns
    
    def test_extract_without_source(self):
        """Testa extração sem fonte especificada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ingester = MCOIngester(output_path=tmpdir)
            
            with pytest.raises(ValueError):
                ingester.extract()
