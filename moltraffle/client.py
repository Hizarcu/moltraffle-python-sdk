"""
moltraffle Python SDK client.
Docs: https://moltraffle.fun
"""
from __future__ import annotations

from typing import Optional
import requests

from .exceptions import MoltraffleError, MoltraffleNotFoundError, MoltraffleValidationError
from .models import CalldataResponse, PlatformConfig, Raffle, RaffleAction, RaffleList


class MoltraffleClient:
    """
    HTTP client for the moltraffle REST API.

    Example::

        client = MoltraffleClient()
        raffles = client.list_raffles(status="active")
        for r in raffles.raffles:
            print(r.title, r.entry_fee_formatted)
    """

    def __init__(self, base_url: str = "https://moltraffle.fun", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.get(url, params=params, timeout=self.timeout)
        if resp.status_code == 404:
            raise MoltraffleNotFoundError(path)
        if resp.status_code == 400:
            data = resp.json()
            raise MoltraffleValidationError(
                data.get("error", "Validation error"),
                details=data.get("details", []),
            )
        if not resp.ok:
            raise MoltraffleError(f"API error {resp.status_code}: {resp.text}", resp.status_code)
        return resp.json()

    def get_config(self) -> PlatformConfig:
        """Return platform configuration (chain info, ABIs, validation rules)."""
        data = self._get("/api/config")
        return PlatformConfig.model_validate(data)

    def list_raffles(
        self,
        status: Optional[str] = None,
        creator: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> RaffleList:
        """
        List raffles with optional filtering.

        :param status: Filter by status: 'upcoming', 'active', 'ended', 'drawn', 'cancelled', 'claimed'
        :param creator: Filter by creator wallet address
        :param limit: Max results (capped at 200)
        :param offset: Pagination offset
        """
        params: dict = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if creator:
            params["creator"] = creator
        data = self._get("/api/raffles", params=params)
        return RaffleList.model_validate(data)

    def get_raffle(self, address: str) -> Raffle:
        """
        Get full details of a raffle by contract address.

        :param address: Raffle contract address (0x...)
        """
        data = self._get(f"/api/raffle/{address}")
        return Raffle.model_validate(data)

    def get_create_calldata(
        self,
        title: str,
        description: str,
        entry_fee: str,
        deadline: int,
        max_participants: int = 0,
        prize_description: str = "",
        creator_commission_bps: int = 0,
    ) -> CalldataResponse:
        """
        Get encoded calldata to create a new raffle via the factory contract.

        :param title: Raffle title (3–100 chars)
        :param description: Raffle description (10–500 chars)
        :param entry_fee: Entry fee in USDC as a string, e.g. '1' for 1 USDC
        :param deadline: Unix timestamp for raffle end (must be in future, within 365 days)
        :param max_participants: 0 = unlimited, 2–10000 = capped
        :param prize_description: Optional prize description
        :param creator_commission_bps: Creator commission in basis points (0–1000)
        :returns: CalldataResponse with to, value, calldata fields
        """
        params: dict = {
            "title": title,
            "description": description,
            "entryFee": entry_fee,
            "deadline": deadline,
            "maxParticipants": max_participants,
            "creatorCommissionBps": creator_commission_bps,
        }
        if prize_description:
            params["prizeDescription"] = prize_description
        data = self._get("/api/factory/calldata", params=params)
        return CalldataResponse.model_validate(data)

    def get_join_calldata(self, raffle_address: str) -> RaffleAction:
        """
        Get the join action calldata for a raffle.

        :param raffle_address: Raffle contract address
        :returns: RaffleAction with to, calldata, value fields
        :raises MoltraffleError: If the raffle is not joinable
        """
        raffle = self.get_raffle(raffle_address)
        action = raffle.actions and raffle.actions.join
        if not action or not action.available:
            reason = (action and action.reason) or "Raffle is not joinable"
            raise MoltraffleError(reason)
        return action

    def get_draw_calldata(self, raffle_address: str) -> RaffleAction:
        """
        Get the drawWinner action calldata for a raffle.

        :param raffle_address: Raffle contract address
        :returns: RaffleAction with to, calldata fields
        :raises MoltraffleError: If draw is not yet available
        """
        raffle = self.get_raffle(raffle_address)
        action = raffle.actions and raffle.actions.draw
        if not action or not action.available:
            reason = (action and action.reason) or "Draw not yet available"
            raise MoltraffleError(reason)
        return action

    def get_claim_calldata(self, raffle_address: str) -> RaffleAction:
        """
        Get the claimPrize action calldata for a raffle.

        :param raffle_address: Raffle contract address
        :returns: RaffleAction with to, calldata fields
        :raises MoltraffleError: If claim is not available
        """
        raffle = self.get_raffle(raffle_address)
        action = raffle.actions and raffle.actions.claim
        if not action or not action.available:
            reason = (action and action.reason) or "Claim not available"
            raise MoltraffleError(reason)
        return action

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "MoltraffleClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
