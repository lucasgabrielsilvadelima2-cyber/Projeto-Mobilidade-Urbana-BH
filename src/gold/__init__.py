"""Inicialização do pacote gold."""

from .aggregation import (
    CoberturaGeograficaAggregator,
    GoldAggregator,
    OnibusAtivosPorPeriodoAggregator,
    PontosCriticosVelocidadeAggregator,
    VelocidadeMediaPorLinhaAggregator,
    aggregate_all_metrics,
)

__all__ = [
    "GoldAggregator",
    "VelocidadeMediaPorLinhaAggregator",
    "OnibusAtivosPorPeriodoAggregator",
    "CoberturaGeograficaAggregator",
    "PontosCriticosVelocidadeAggregator",
    "aggregate_all_metrics",
]
