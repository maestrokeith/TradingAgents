"""AURA production hardening layer for TradingAgents.

This package is deliberately execution-agnostic: it converts TradingAgents
research into validated paper-trading artifacts without connecting to a live
broker.
"""

from .models import PaperOrder, RiskDecision, SignalSnapshot
from .paper import PaperBroker
from .risk import RiskEngine

__all__ = ["PaperBroker", "PaperOrder", "RiskDecision", "RiskEngine", "SignalSnapshot"]
