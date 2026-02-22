from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class RaffleAction(BaseModel):
    available: bool
    to: str | None = None
    function: str | None = None
    calldata: str | None = None
    calldata_example: str | None = None
    value: str | None = None
    note: str | None = None
    reason: str | None = None
    args: dict[str, Any] | None = None


class RaffleActions(BaseModel):
    join: RaffleAction | None = None
    draw: RaffleAction | None = None
    claim: RaffleAction | None = None
    cancel: RaffleAction | None = None
    withdraw_refund: RaffleAction | None = Field(None, alias="withdrawRefund")

    class Config:
        populate_by_name = True


class Raffle(BaseModel):
    address: str
    title: str
    description: str | None = None
    prize_description: str | None = Field(None, alias="prizeDescription")
    entry_fee: str = Field(alias="entryFee")
    entry_fee_formatted: str | None = Field(None, alias="entryFeeFormatted")
    deadline: int
    deadline_iso: str | None = Field(None, alias="deadlineISO")
    max_participants: int = Field(alias="maxParticipants")
    current_participants: int = Field(alias="currentParticipants")
    status: int
    status_label: str | None = Field(None, alias="statusLabel")
    creator: str
    winner: str | None = None
    creator_commission_bps: int = Field(0, alias="creatorCommissionBps")
    prize_pool: str | None = Field(None, alias="prizePool")
    prize_pool_formatted: str | None = Field(None, alias="prizePoolFormatted")
    participants: list[str] | None = None
    actions: RaffleActions | None = None

    class Config:
        populate_by_name = True


class RaffleList(BaseModel):
    raffles: list[Raffle]
    total: int
    limit: int
    offset: int


class PlatformConfig(BaseModel):
    chain_id: int = Field(alias="chainId")
    chain_name: str = Field(alias="chainName")
    factory_address: str = Field(alias="factoryAddress")
    rpc_url: str = Field(alias="rpcUrl")
    explorer_url: str = Field(alias="explorerUrl")
    status_enum: dict[str, str] = Field(alias="statusEnum")

    class Config:
        populate_by_name = True


class CalldataResponse(BaseModel):
    to: str
    value: str
    value_formatted: str | None = Field(None, alias="valueFormatted")
    calldata: str
    function: str
    args: dict[str, Any] | None = None
    estimated_gas: str | None = Field(None, alias="estimatedGas")

    class Config:
        populate_by_name = True
