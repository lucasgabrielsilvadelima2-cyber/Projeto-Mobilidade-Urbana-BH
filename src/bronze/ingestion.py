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
from curl_cffi import requests
from curl_cffi.requests import Session

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
    
    def _create_session(self) -> Session:
        """
        Cria uma sessão HTTP com curl_cffi para emulação de navegador.
        
        Usa curl_cffi ao invés de requests padrão para contornar fingerprinting
        TLS/SSL que bloqueia requisições Python. Emula perfeitamente navegadores
        reais, funcionando em qualquer plataforma (Windows, Linux, macOS, Docker).
        
        Returns:
            Sessão configurada com browser impersonation
        """
        session = Session()
        
        # Headers básicos - curl_cffi já emula headers de navegador
        session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Referer': 'https://temporeal.pbh.gov.br/',
        })
        
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
    
    def _fetch_data(self) -> str:
        """
        Faz requisição à API com emulação de navegador real.
        
        Usa curl_cffi para emular fingerprint TLS de navegadores reais,
        contornando proteções WAF de forma legítima e portável.
        Funciona em qualquer plataforma (Windows, Linux, macOS, Docker).
        
        Estratégia: Tenta múltiplos perfis de navegador até encontrar um que funcione.
        
        Returns:
            Conteúdo da resposta como string
            
        Raises:
            Exception: Se falhar após todas tentativas
        """
        # Lista de impersonations para tentar (em ordem de compatibilidade)
        impersonations = [
            "chrome110",   # Chrome moderno
            "chrome107",   # Chrome um pouco mais antigo
            "safari15_5",  # Safari (bom para APIs Apple-friendly)
            "firefox109",  # Firefox alternativo
        ]
        
        last_error = None
        
        for impersonate in impersonations:
            try:
                logger.info(f"🔄 Tentando acessar API (emulando {impersonate})...")
                
                response = requests.get(
                    self.api_url,
                    impersonate=impersonate,
                    timeout=30
                )
                
                # Verifica status code
                if response.status_code == 200:
                    logger.info(f"✅ Sucesso com {impersonate} (status: {response.status_code})")
                    return response.text
                else:
                    logger.warning(f"⚠️ Status {response.status_code} com {impersonate}, tentando próximo...")
                    last_error = f"HTTP {response.status_code}"
                    continue
                
            except Exception as e:
                logger.warning(f"⚠️ Erro com {impersonate}: {e}")
                last_error = e
                continue
        
        # Se todas tentativas falharem
        error_msg = f"Não foi possível acessar API após tentar {len(impersonations)} navegadores diferentes"
        logger.error(f"❌ {error_msg}. Último erro: {last_error}")
        raise Exception(f"{error_msg}: {last_error}")
    
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
            
            # Usa método robusto com emulação de navegador
            text_content = self._fetch_data()
            lineage.add_metadata("method", "curl_cffi_browser_impersonation")
            
            logger.debug(f"✓ Dados recebidos com sucesso")
        
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados: {e}")
            lineage.add_metadata("error", str(e))
            raise
        
        # Parse do formato customizado da PBH
        # Formato: <EV=105;HR=...;LT=...>
        try:
            if not text_content:
                raise ValueError("Nenhum conteúdo recebido da API")
            
            records = []
            
            for line in text_content.strip().split('\n'):
                line = line.strip()
                if not line or not line.startswith('<'):
                    continue
                    
                # Remove < e >
                line = line.strip('<>')
                
                # Parse dos campos CAMPO=VALOR
                record = {}
                for field in line.split(';'):
                    if '=' in field:
                        key, value = field.split('=', 1)
                        record[key.strip()] = value.strip()
                
                if record:
                    records.append(record)
            
            df = pd.DataFrame(records)
            
            if df.empty:
                logger.warning("⚠️ Nenhum dado retornado pela API")
                # Retorna DataFrame vazio com estrutura esperada
                df = pd.DataFrame(columns=['evento', 'horario', 'latitude', 'longitude', 
                                          'numero_veiculo', 'velocidade', 'numero_linha',
                                          'direcao', 'status_veiculo', 'distancia'])
            else:
                # Renomeia colunas para nomes mais descritivos
                column_mapping = {
                    'EV': 'evento',
                    'HR': 'horario',
                    'LT': 'latitude',
                    'LG': 'longitude',
                    'NV': 'numero_veiculo',
                    'VL': 'velocidade',
                    'NL': 'numero_linha',
                    'DG': 'direcao',
                    'SV': 'status_veiculo',
                    'DT': 'distancia'
                }
                df = df.rename(columns=column_mapping)
                
                # Converte tipos de dados numéricos
                numeric_columns = ['latitude', 'longitude', 'velocidade', 'numero_veiculo',
                                  'numero_linha', 'direcao', 'status_veiculo', 'distancia', 'evento']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Adiciona metadados de ingestão
            df["_ingestion_timestamp"] = datetime.now()
            df["_source"] = "api_tempo_real"
            
            lineage.add_metadata("records_extracted", len(df))
            logger.info(f"✅ Extraídos {len(df)} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse dos dados: {e}")
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
