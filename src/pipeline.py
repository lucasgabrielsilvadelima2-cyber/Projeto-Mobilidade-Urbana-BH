"""
Pipeline Principal - Orquestração ETL.

Este módulo orquestra a execução completa do pipeline de dados,
integrando as camadas Bronze, Silver e Gold.
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .bronze import ingest_all_sources
from .gold import aggregate_all_metrics
from .silver import transform_all_sources
from .utils import load_config, load_environment, setup_logging

logger = logging.getLogger(__name__)


class DataPipeline:
    """Orquestrador do pipeline de dados."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa o pipeline.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Raises:
            FileNotFoundError: Se o arquivo de configuração não existir
        """
        load_environment()
        
        # Valida existência do arquivo de configuração
        import os
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {config_path}\n"
                f"Certifique-se de criar o arquivo a partir de config.yaml.example"
            )
        
        self.config = load_config(config_path)
        
        # Configura logging
        log_config = self.config.get("logging", {})
        self.logger = setup_logging(
            log_level=log_config.get("level", "INFO"),
            log_file=log_config.get("file")
        )
        
        self.execution_start = datetime.now()
        self.results: Dict[str, Any] = {
            "execution_id": self.execution_start.strftime("%Y%m%d_%H%M%S"),
            "start_time": self.execution_start.isoformat(),
            "layers": {}
        }
    
    def run_bronze_layer(self) -> bool:
        """
        Executa a camada Bronze (ingestão).
        
        Returns:
            True se bem-sucedido, False caso contrário
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO CAMADA BRONZE - INGESTÃO DE DADOS")
        self.logger.info("=" * 60)
        
        try:
            bronze_results = ingest_all_sources(self.config)
            self.results["layers"]["bronze"] = bronze_results
            
            # Verifica se houve erros
            errors = [k for k, v in bronze_results.items() if str(v).startswith("ERROR")]
            if errors:
                self.logger.warning(f"Ingestão com erros em: {errors}")
                return False
            
            self.logger.info("✓ Camada Bronze concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Erro na camada Bronze: {e}", exc_info=True)
            self.results["layers"]["bronze"] = {"error": str(e)}
            return False
    
    def run_silver_layer(self) -> bool:
        """
        Executa a camada Silver (transformação).
        
        Returns:
            True se bem-sucedido, False caso contrário
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO CAMADA SILVER - TRANSFORMAÇÃO DE DADOS")
        self.logger.info("=" * 60)
        
        try:
            silver_results = transform_all_sources(self.config)
            self.results["layers"]["silver"] = silver_results
            
            # Verifica se houve erros
            errors = [k for k, v in silver_results.items() if str(v).startswith("ERROR")]
            if errors:
                self.logger.warning(f"Transformação com erros em: {errors}")
                return False
            
            self.logger.info("✓ Camada Silver concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Erro na camada Silver: {e}", exc_info=True)
            self.results["layers"]["silver"] = {"error": str(e)}
            return False
    
    def run_gold_layer(self) -> bool:
        """
        Executa a camada Gold (agregação).
        
        Returns:
            True se bem-sucedido, False caso contrário
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO CAMADA GOLD - AGREGAÇÕES E MÉTRICAS")
        self.logger.info("=" * 60)
        
        try:
            gold_results = aggregate_all_metrics(self.config)
            self.results["layers"]["gold"] = gold_results
            
            # Verifica se houve erros
            errors = [k for k, v in gold_results.items() if str(v).startswith("ERROR")]
            if errors:
                self.logger.warning(f"Agregação com erros em: {errors}")
                return False
            
            self.logger.info("✓ Camada Gold concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Erro na camada Gold: {e}", exc_info=True)
            self.results["layers"]["gold"] = {"error": str(e)}
            return False
    
    def run(
        self,
        layers: Optional[list] = None,
        skip_bronze: bool = False
    ) -> Dict[str, Any]:
        """
        Executa o pipeline completo ou camadas específicas.
        
        Args:
            layers: Lista de camadas para executar (bronze, silver, gold)
            skip_bronze: Se True, pula a camada Bronze
        
        Returns:
            Dicionário com resultados da execução
        """
        if layers is None:
            layers = ["bronze", "silver", "gold"]
        
        if skip_bronze and "bronze" in layers:
            layers.remove("bronze")
        
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PIPELINE DE DADOS - BH MOBILIDADE URBANA")
        self.logger.info(f"Execution ID: {self.results['execution_id']}")
        self.logger.info(f"Camadas: {', '.join(layers).upper()}")
        self.logger.info("=" * 60)
        
        success = True
        
        # Executa camadas na ordem
        if "bronze" in layers:
            if not self.run_bronze_layer():
                success = False
                if not self._should_continue_on_error():
                    return self._finalize_execution(success)
        
        if "silver" in layers:
            if not self.run_silver_layer():
                success = False
                if not self._should_continue_on_error():
                    return self._finalize_execution(success)
        
        if "gold" in layers:
            if not self.run_gold_layer():
                success = False
        
        return self._finalize_execution(success)
    
    def _should_continue_on_error(self) -> bool:
        """Verifica se deve continuar após erro."""
        # Por padrão, continua (pode ser configurado)
        return True
    
    def _finalize_execution(self, success: bool) -> Dict[str, Any]:
        """
        Finaliza a execução e retorna resultados.
        
        Args:
            success: Se a execução foi bem-sucedida
        
        Returns:
            Dicionário com resultados completos
        """
        execution_end = datetime.now()
        duration = (execution_end - self.execution_start).total_seconds()
        
        self.results.update({
            "end_time": execution_end.isoformat(),
            "duration_seconds": duration,
            "success": success,
            "status": "COMPLETED" if success else "FAILED"
        })
        
        self.logger.info("=" * 60)
        self.logger.info(f"PIPELINE {'CONCLUÍDO' if success else 'FALHOU'}")
        self.logger.info(f"Duração: {duration:.2f} segundos")
        self.logger.info("=" * 60)
        
        return self.results


def main():
    """Função principal - ponto de entrada do pipeline."""
    parser = argparse.ArgumentParser(
        description="Pipeline de Dados de Mobilidade Urbana de Belo Horizonte"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Caminho para o arquivo de configuração"
    )
    
    parser.add_argument(
        "--layers",
        type=str,
        nargs="+",
        choices=["bronze", "silver", "gold"],
        help="Camadas específicas para executar"
    )
    
    parser.add_argument(
        "--skip-bronze",
        action="store_true",
        help="Pula a camada Bronze (útil para re-processar dados existentes)"
    )
    
    args = parser.parse_args()
    
    try:
        pipeline = DataPipeline(config_path=args.config)
        results = pipeline.run(
            layers=args.layers,
            skip_bronze=args.skip_bronze
        )
        
        # Exit code baseado no sucesso
        sys.exit(0 if results["success"] else 1)
        
    except Exception as e:
        logger.error(f"Erro fatal no pipeline: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
