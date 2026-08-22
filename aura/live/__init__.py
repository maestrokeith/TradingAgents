"""Human-confirmed live-trading boundary.

This package deliberately requires an explicit human confirmation token before
any broker adapter is allowed to submit a live order.
"""

from .models import LiveOrderIntent, Confirmation, ExecutionResult
from .gateway import HumanConfirmedGateway

__all__ = ["LiveOrderIntent", "Confirmation", "ExecutionResult", "HumanConfirmedGateway"]
