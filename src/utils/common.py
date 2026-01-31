"""
BH Mobilidade Urbana Pipeline - Utilitários Comuns.

Este módulo contém funções utilitárias compartilhadas entre as diferentes
camadas do pipeline.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configura o sistema de logging do pipeline.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("bh_mobilidade_pipeline")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Formato do log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Carrega configurações do arquivo YAML.
    
    Args:
        config_path: Caminho para o arquivo de configuração
    
    Returns:
        Dicionário com as configurações
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def load_environment() -> None:
    """Carrega variáveis de ambiente do arquivo .env."""
    load_dotenv()


def get_partition_path(
    base_path: str,
    timestamp: Optional[datetime] = None
) -> str:
    """
    Gera o caminho particionado por data.
    
    Args:
        base_path: Caminho base do diretório
        timestamp: Data/hora para particionamento (padrão: agora)
    
    Returns:
        Caminho particionado (base_path/year=YYYY/month=MM/day=DD)
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    partition_path = os.path.join(
        base_path,
        f"year={timestamp.year}",
        f"month={timestamp.month:02d}",
        f"day={timestamp.day:02d}"
    )
    
    os.makedirs(partition_path, exist_ok=True)
    return partition_path


def get_date_partition_path(
    base_path: str,
    date: Optional[datetime] = None
) -> str:
    """
    Gera o caminho particionado por data (formato simplificado).
    
    Args:
        base_path: Caminho base do diretório
        date: Data para particionamento (padrão: hoje)
    
    Returns:
        Caminho particionado (base_path/date=YYYY-MM-DD)
    """
    if date is None:
        date = datetime.now()
    
    partition_path = os.path.join(
        base_path,
        f"date={date.strftime('%Y-%m-%d')}"
    )
    
    os.makedirs(partition_path, exist_ok=True)
    return partition_path


def create_directory_structure(base_path: str) -> None:
    """
    Cria a estrutura de diretórios necessária para o pipeline.
    
    Args:
        base_path: Diretório base do projeto
    """
    directories = [
        "data/bronze",
        "data/silver",
        "data/gold",
        "logs",
        "config",
    ]
    
    for directory in directories:
        path = os.path.join(base_path, directory)
        os.makedirs(path, exist_ok=True)


def get_timestamp_str() -> str:
    """
    Retorna timestamp formatado para nomes de arquivo.
    
    Returns:
        String no formato YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class DataLineage:
    """Classe para rastreamento de linhagem de dados."""
    
    def __init__(self, source: str, operation: str):
        """
        Inicializa rastreamento de linhagem.
        
        Args:
            source: Fonte dos dados
            operation: Operação sendo realizada
        """
        self.source = source
        self.operation = operation
        self.start_time = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Adiciona metadados à linhagem."""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte linhagem para dicionário."""
        return {
            "source": self.source,
            "operation": self.operation,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "metadata": self.metadata
        }
