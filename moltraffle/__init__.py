"""
moltraffle Python SDK

On-chain raffles on Base mainnet — built for AI agents and humans.
https://moltraffle.fun
"""

from .client import MoltraffleClient
from .exceptions import MoltraffleError, MoltraffleNotFoundError, MoltraffleValidationError
from .models import CalldataResponse, PlatformConfig, Raffle, RaffleAction, RaffleList

try:
    from .langchain_tools import MoltraffleToolkit, ListRafflesTool, GetRaffleTool, CreateRaffleCalldataTool, JoinRaffleCalldataTool
    _langchain_exports = ["MoltraffleToolkit", "ListRafflesTool", "GetRaffleTool", "CreateRaffleCalldataTool", "JoinRaffleCalldataTool"]
except ImportError:
    _langchain_exports = []

__version__ = "0.1.0"
__all__ = [
    "MoltraffleClient",
    "MoltraffleError",
    "MoltraffleNotFoundError",
    "MoltraffleValidationError",
    "CalldataResponse",
    "PlatformConfig",
    "Raffle",
    "RaffleAction",
    "RaffleList",
] + _langchain_exports
