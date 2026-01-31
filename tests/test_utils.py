"""Testes para o módulo de utilitários comuns."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.utils.common import (
    DataLineage,
    get_date_partition_path,
    get_partition_path,
    get_timestamp_str,
    load_config,
    setup_logging,
)


class TestLogging:
    """Testes para configuração de logging."""
    
    def test_setup_logging_default(self):
        """Testa configuração padrão de logging."""
        logger = setup_logging()
        assert logger is not None
        assert logger.name == "bh_mobilidade_pipeline"
    
    def test_setup_logging_with_file(self):
        """Testa configuração de logging com arquivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logging(log_level="DEBUG", log_file=log_file)
            
            logger.info("Teste de log")
            assert os.path.exists(log_file)


class TestPartitionPaths:
    """Testes para geração de caminhos particionados."""
    
    def test_get_partition_path(self):
        """Testa geração de caminho particionado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            timestamp = datetime(2024, 1, 15, 10, 30)
            path = get_partition_path(tmpdir, timestamp)
            
            assert "year=2024" in path
            assert "month=01" in path
            assert "day=15" in path
            assert os.path.exists(path)
    
    def test_get_date_partition_path(self):
        """Testa geração de caminho com data simplificada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            date = datetime(2024, 1, 15)
            path = get_date_partition_path(tmpdir, date)
            
            assert "date=2024-01-15" in path
            assert os.path.exists(path)


class TestTimestamp:
    """Testes para geração de timestamps."""
    
    def test_get_timestamp_str(self):
        """Testa geração de string timestamp."""
        ts = get_timestamp_str()
        assert len(ts) == 15  # YYYYMMDD_HHMMSS
        assert "_" in ts


class TestDataLineage:
    """Testes para rastreamento de linhagem."""
    
    def test_data_lineage_creation(self):
        """Testa criação de linhagem."""
        lineage = DataLineage(source="test_source", operation="test_op")
        assert lineage.source == "test_source"
        assert lineage.operation == "test_op"
        assert lineage.start_time is not None
    
    def test_data_lineage_metadata(self):
        """Testa adição de metadados."""
        lineage = DataLineage(source="test", operation="test")
        lineage.add_metadata("key1", "value1")
        lineage.add_metadata("key2", 123)
        
        assert lineage.metadata["key1"] == "value1"
        assert lineage.metadata["key2"] == 123
    
    def test_data_lineage_to_dict(self):
        """Testa conversão para dicionário."""
        lineage = DataLineage(source="test", operation="test")
        lineage.add_metadata("test_key", "test_value")
        
        result = lineage.to_dict()
        assert result["source"] == "test"
        assert result["operation"] == "test"
        assert "start_time" in result
        assert "end_time" in result
        assert "duration_seconds" in result
        assert result["metadata"]["test_key"] == "test_value"


class TestConfigLoading:
    """Testes para carregamento de configuração."""
    
    def test_load_config(self):
        """Testa carregamento de arquivo de configuração."""
        # Testa com o arquivo de config real do projeto
        config_path = "config/config.yaml"
        if os.path.exists(config_path):
            config = load_config(config_path)
            assert config is not None
            assert "pipeline" in config
            assert "layers" in config
