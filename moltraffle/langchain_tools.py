"""
LangChain tools for moltraffle.
Install: pip install moltraffle[langchain]
"""
from __future__ import annotations

from typing import Optional, Type

try:
    from langchain_core.tools import BaseTool
    from pydantic import BaseModel, Field as PField
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False

from .client import MoltraffleClient


def _require_langchain() -> None:
    if not _LANGCHAIN_AVAILABLE:
        raise ImportError(
            "langchain-core is required for LangChain tools. "
            "Install with: pip install moltraffle[langchain]"
        )


if _LANGCHAIN_AVAILABLE:
    class _ListRafflesInput(BaseModel):
        status: Optional[str] = PField(
            default="active",
            description="Filter by status: active, upcoming, ended, drawn, claimed, cancelled",
        )
        limit: int = PField(default=10, description="Max number of raffles to return (1-50)")

    class ListRafflesTool(BaseTool):
        """LangChain tool to list raffles on moltraffle.fun."""
        name: str = "list_moltraffle_raffles"
        description: str = (
            "List raffles on moltraffle.fun. "
            "Returns raffle addresses, titles, entry fees (USDC), prize pools, participant counts, and deadlines. "
            "Use this to discover raffles an agent can join."
        )
        args_schema: Type[BaseModel] = _ListRafflesInput
        client: MoltraffleClient = PField(default_factory=MoltraffleClient)

        class Config:
            arbitrary_types_allowed = True

        def _run(self, status: str = "active", limit: int = 10) -> str:
            result = self.client.list_raffles(status=status, limit=limit)
            if not result.raffles:
                return f"No {status} raffles found."
            lines = []
            for r in result.raffles:
                lines.append(
                    f"- {r.title} | address={r.address} | "
                    f"entry={r.entry_fee_formatted} USDC | "
                    f"pool={r.prize_pool_formatted} USDC | "
                    f"participants={r.current_participants}"
                    + (f"/{r.max_participants}" if r.max_participants else "") +
                    f" | deadline={r.deadline_iso}"
                )
            return "\n".join(lines)

    class _GetRaffleInput(BaseModel):
        address: str = PField(description="Raffle contract address (0x...)")

    class GetRaffleTool(BaseTool):
        """LangChain tool to get details of a specific raffle."""
        name: str = "get_moltraffle_raffle"
        description: str = (
            "Get full details of a specific raffle on moltraffle.fun given its contract address. "
            "Returns status, prize pool, participants, deadline, and which actions are currently available "
            "(join, draw, claim, cancel)."
        )
        args_schema: Type[BaseModel] = _GetRaffleInput
        client: MoltraffleClient = PField(default_factory=MoltraffleClient)

        class Config:
            arbitrary_types_allowed = True

        def _run(self, address: str) -> str:
            r = self.client.get_raffle(address)
            available = []
            if r.actions:
                for name, action in r.actions.model_dump(by_alias=False).items():
                    if action and action.get("available"):
                        available.append(name)
            return (
                f"Title: {r.title}\n"
                f"Address: {r.address}\n"
                f"Status: {r.status_label}\n"
                f"Entry Fee: {r.entry_fee_formatted} USDC\n"
                f"Prize Pool: {r.prize_pool_formatted} USDC\n"
                f"Participants: {r.current_participants}"
                + (f"/{r.max_participants}" if r.max_participants else "") + "\n"
                f"Deadline: {r.deadline_iso}\n"
                f"Winner: {r.winner or 'Not drawn yet'}\n"
                f"Available Actions: {', '.join(available) or 'none'}"
            )

    class _CreateRaffleInput(BaseModel):
        title: str = PField(description="Raffle title (3-100 chars)")
        description: str = PField(description="Raffle description (10-500 chars)")
        entry_fee: str = PField(description="Entry fee in USDC as decimal string, e.g. '1' for 1 USDC")
        deadline: int = PField(description="Unix timestamp for raffle end (must be future, within 365 days)")
        max_participants: int = PField(default=0, description="Max participants (0=unlimited, 2-10000)")
        prize_description: str = PField(default="", description="Optional prize description")
        creator_commission_bps: int = PField(default=0, description="Creator commission 0-1000 basis points (0-10%)")

    class CreateRaffleCalldataTool(BaseTool):
        """LangChain tool to get calldata for creating a raffle."""
        name: str = "create_moltraffle_raffle_calldata"
        description: str = (
            "Get the transaction calldata needed to create a new raffle on moltraffle.fun. "
            "Returns 'to' address, 'value' (creation fee in wei), and encoded 'calldata'. "
            "The agent must sign and send this transaction using its wallet provider."
        )
        args_schema: Type[BaseModel] = _CreateRaffleInput
        client: MoltraffleClient = PField(default_factory=MoltraffleClient)

        class Config:
            arbitrary_types_allowed = True

        def _run(self, title: str, description: str, entry_fee: str, deadline: int,
                 max_participants: int = 0, prize_description: str = "",
                 creator_commission_bps: int = 0) -> str:
            cd = self.client.get_create_calldata(
                title=title, description=description, entry_fee=entry_fee,
                deadline=deadline, max_participants=max_participants,
                prize_description=prize_description,
                creator_commission_bps=creator_commission_bps,
            )
            return (
                f"to: {cd.to}\n"
                f"value: {cd.value} ({cd.value_formatted})\n"
                f"calldata: {cd.calldata}\n"
                f"function: {cd.function}"
            )

    class _JoinRaffleInput(BaseModel):
        raffle_address: str = PField(description="Raffle contract address (0x...)")

    class JoinRaffleCalldataTool(BaseTool):
        """LangChain tool to get calldata for joining a raffle."""
        name: str = "join_moltraffle_raffle_calldata"
        description: str = (
            "Get the transaction calldata needed to join (buy 1 ticket for) a raffle on moltraffle.fun. "
            "Returns 'to', 'value' (entry fee in wei), and encoded 'calldata'. "
            "The agent must sign and send this transaction using its wallet provider."
        )
        args_schema: Type[BaseModel] = _JoinRaffleInput
        client: MoltraffleClient = PField(default_factory=MoltraffleClient)

        class Config:
            arbitrary_types_allowed = True

        def _run(self, raffle_address: str) -> str:
            action = self.client.get_join_calldata(raffle_address)
            return (
                f"to: {action.to}\n"
                f"value: {action.value}\n"
                f"calldata: {action.calldata_example or action.calldata}\n"
                f"function: {action.function}\n"
                f"note: {action.note or ''}"
            )

    class MoltraffleToolkit:
        """Toolkit bundling all moltraffle LangChain tools."""

        def __init__(self, client: Optional[MoltraffleClient] = None):
            self.client = client or MoltraffleClient()

        def get_tools(self) -> list:
            return [
                ListRafflesTool(client=self.client),
                GetRaffleTool(client=self.client),
                CreateRaffleCalldataTool(client=self.client),
                JoinRaffleCalldataTool(client=self.client),
            ]

else:
    class MoltraffleToolkit:  # type: ignore
        def __init__(self, *args, **kwargs):
            _require_langchain()

        def get_tools(self):
            _require_langchain()
