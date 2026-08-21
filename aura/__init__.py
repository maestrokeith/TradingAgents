"""AURA production hardening layer for TradingAgents.

This package is deliberately execution-agnostic: it converts TradingAgents
research into validated paper-trading artifacts without connecting to a live
broker.
"""

from .engine import AuraResearchEngine
from .models import PaperOrder, RiskDecision, SignalSnapshot
from .paper import PaperBroker
from .risk import RiskEngine, RiskLimits

__all__ = [
    "AuraResearchEngine",
    "PaperBroker",
    "PaperOrder",
    "RiskDecision",
    "RiskEngine",
    "RiskLimits",
    "SignalSnapshot",
]
