"""
Camada Bronze - Ingestão de Dados Brutos.

Este módulo é responsável por extrair dados das APIs de dados abertos de
Belo Horizonte e salvá-los em formato Parquet na camada Bronze (dados imutáveis).
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.common import DataLineage, get_partition_path

logger = logging.getLogger(__name__)


class BronzeDataIngester:
    """Classe base para ingestão de dados na camada Bronze."""
    
    def __init__(self, output_path: str = "./data/bronze"):
        """
        Inicializa o ingestor de dados.
        
        Args:
            output_path: Caminho para salvar os dados brutos
        """
        self.output_path = output_path
        self.session = self._create_session()
        os.makedirs(output_path, exist_ok=True)
    
    def _create_session(self) -> requests.Session:
        """
        Cria uma sessão HTTP com retry automático.
        
        Returns:
            Sessão configurada
        """
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _save_to_parquet(
        self,
        data: pd.DataFrame,
        dataset_name: str,
        partition_by_date: bool = True
    ) -> str:
        """
        Salva dados em formato Parquet.
        
        Args:
            data: DataFrame a ser salvo
            dataset_name: Nome do dataset
            partition_by_date: Se True, particiona por data
        
        Returns:
            Caminho do arquivo salvo
        """
        if partition_by_date:
            partition_path = get_partition_path(
                os.path.join(self.output_path, dataset_name)
            )
        else:
            partition_path = os.path.join(self.output_path, dataset_name)
            os.makedirs(partition_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            partition_path,
            f"{dataset_name}_{timestamp}.parquet"
        )
        
        data.to_parquet(
            file_path,
            engine="pyarrow",
            compression="snappy",
            index=False
        )
        
        logger.info(f"Dados salvos em: {file_path}")
        logger.info(f"Total de registros: {len(data)}")
        
        return file_path


class OnibusTempoRealIngester(BronzeDataIngester):
    """Ingestor de dados de ônibus em tempo real."""
    
    def __init__(
        self,
        api_url: str = "https://temporeal.pbh.gov.br/v1/posicoes",
        output_path: str = "./data/bronze"
    ):
        """
        Inicializa o ingestor de dados de ônibus.
        
        Args:
            api_url: URL da API de tempo real
            output_path: Caminho de saída
        """
        super().__init__(output_path)
        self.api_url = api_url
    
    def extract(self) -> pd.DataFrame:
        """
        Extrai dados de posicionamento dos ônibus.
        
        Returns:
            DataFrame com os dados extraídos
        """
        lineage = DataLineage(
            source="PBH Tempo Real API",
            operation="extract_onibus_posicoes"
        )
        
        try:
            logger.info(f"🔄 Extraindo dados de: {self.api_url}")
            logger.debug(f"Tentando conexão com timeout de 30s...")
            response = self.session.get(self.api_url, timeout=30)
            response.raise_for_status()
            logger.debug(f"✓ Resposta recebida com status {response.status_code}")
            
            data = response.json()
            lineage.add_metadata("http_status", response.status_code)
            lineage.add_metadata("response_size_bytes", len(response.content))
            
            # Converte para DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                df = pd.DataFrame([data])
            
            # Adiciona metadados de ingestão
            df["_ingestion_timestamp"] = datetime.now()
            df["_source"] = "api_tempo_real"
            
            lineage.add_metadata("records_extracted", len(df))
            logger.info(f"Extraídos {len(df)} registros")
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao extrair dados: {e}")
            lineage.add_metadata("error", str(e))
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """
        Carrega dados na camada Bronze.
        
        Args:
            data: DataFrame a ser carregado
        
        Returns:
            Caminho do arquivo salvo
        """
        return self._save_to_parquet(data, "onibus_tempo_real")


class MCOIngester(BronzeDataIngester):
    """Ingestor de dados do Mapa de Controle Operacional (MCO)."""
    
    def __init__(
        self,
        data_url: Optional[str] = None,
        output_path: str = "./data/bronze"
    ):
        """
        Inicializa o ingestor de dados do MCO.
        
        Args:
            data_url: URL do dataset MCO (ou arquivo local)
            output_path: Caminho de saída
        """
        super().__init__(output_path)
        self.data_url = data_url
    
    def extract(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Extrai dados do MCO.
        
        Args:
            file_path: Caminho para arquivo CSV local (opcional)
        
        Returns:
            DataFrame com os dados extraídos
        """
        lineage = DataLineage(
            source="PBH MCO Dataset",
            operation="extract_mco"
        )
        
        try:
            if file_path:
                logger.info(f"Lendo arquivo local: {file_path}")
                df = pd.read_csv(file_path, encoding="utf-8", sep=";")
                lineage.add_metadata("source_type", "local_file")
            elif self.data_url:
                logger.info(f"Extraindo dados de: {self.data_url}")
                df = pd.read_csv(self.data_url, encoding="utf-8", sep=";")
                lineage.add_metadata("source_type", "url")
            else:
                raise ValueError("É necessário fornecer file_path ou data_url")
            
            # Adiciona metadados de ingestão
            df["_ingestion_timestamp"] = datetime.now()
            df["_source"] = "mco_dataset"
            
            lineage.add_metadata("records_extracted", len(df))
            logger.info(f"Extraídos {len(df)} registros do MCO")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do MCO: {e}")
            lineage.add_metadata("error", str(e))
            raise
    
    def load(self, data: pd.DataFrame) -> str:
        """
        Carrega dados na camada Bronze.
        
        Args:
            data: DataFrame a ser carregado
        
        Returns:
            Caminho do arquivo salvo
        """
        return self._save_to_parquet(data, "mco")


def ingest_all_sources(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Executa ingestão de todas as fontes de dados configuradas.
    
    Args:
        config: Dicionário de configuração
    
    Returns:
        Dicionário com caminhos dos arquivos salvos
    """
    results = {}
    
    # Ingestão de ônibus em tempo real
    if config.get("data_sources", {}).get("onibus_tempo_real", {}).get("enabled"):
        try:
            onibus_ingester = OnibusTempoRealIngester(
                api_url=config["data_sources"]["onibus_tempo_real"]["url"],
                output_path=config["layers"]["bronze"]["path"]
            )
            df_onibus = onibus_ingester.extract()
            results["onibus_tempo_real"] = onibus_ingester.load(df_onibus)
        except Exception as e:
            logger.error(f"Falha na ingestão de ônibus: {e}")
            results["onibus_tempo_real"] = f"ERROR: {e}"
    
    # Ingestão do MCO
    if config.get("data_sources", {}).get("mco", {}).get("enabled"):
        try:
            mco_ingester = MCOIngester(
                data_url=config["data_sources"]["mco"]["url"],
                output_path=config["layers"]["bronze"]["path"]
            )
            # Nota: MCO pode precisar de arquivo local, ajustar conforme necessário
            df_mco = mco_ingester.extract()
            results["mco"] = mco_ingester.load(df_mco)
        except Exception as e:
            logger.error(f"Falha na ingestão do MCO: {e}")
            results["mco"] = f"ERROR: {e}"
    
    return results
