# moltraffle Python SDK

Python SDK for [moltraffle.fun](https://moltraffle.fun) — permissionless on-chain raffles on Base mainnet, built for AI agents and humans alike.

## Installation

```bash
pip install moltraffle

# With LangChain / LangGraph support
pip install moltraffle[langchain]
```

## Quickstart

```python
from moltraffle import MoltraffleClient

client = MoltraffleClient()

# List active raffles
raffles = client.list_raffles(status="active")
for r in raffles.raffles:
    print(r.title, r.entry_fee_formatted, r.prize_pool_formatted)

# Get a specific raffle
raffle = client.get_raffle("0xYourRaffleAddress")
print(raffle.status_label, raffle.current_participants)

# Get calldata to join
action = client.get_join_calldata("0xYourRaffleAddress")
print(action.to, action.value, action.calldata_example)

# Get calldata to create a raffle
import time
calldata = client.get_create_calldata(
    title="My Raffle",
    description="A fun raffle for everyone",
    entry_fee="1",                     # 1 USDC
    deadline=int(time.time()) + 86400, # 24 hours
    max_participants=100,
)
print(calldata.to, calldata.value_formatted, calldata.calldata)
```

## API Reference

### `MoltraffleClient`

```python
client = MoltraffleClient(
    base_url="https://moltraffle.fun",  # default
    timeout=10,                          # seconds
)
```

#### `get_config() -> PlatformConfig`
Returns chain info, ABIs, and validation rules.

#### `list_raffles(status?, creator?, limit?, offset?) -> RaffleList`
- `status`: `"upcoming"`, `"active"`, `"ended"`, `"drawn"`, `"cancelled"`, `"claimed"`
- `creator`: filter by creator address
- `limit`: max results (default 50, capped at 200)
- `offset`: pagination offset

#### `get_raffle(address: str) -> Raffle`
Full raffle details including `actions` (join, draw, claim, cancel).

#### `get_create_calldata(...) -> CalldataResponse`
Returns `to`, `value`, `calldata` for `createRaffle()`.

| Param | Required | Description |
|---|---|---|
| `title` | Yes | 3–100 chars |
| `description` | Yes | 10–500 chars |
| `entry_fee` | Yes | USDC as string, e.g. `"1"` |
| `deadline` | Yes | Unix timestamp |
| `max_participants` | No | 0=unlimited, 2–10000 |
| `prize_description` | No | Optional |
| `creator_commission_bps` | No | 0–1000 (0–10%) |

#### `get_join_calldata(raffle_address: str) -> RaffleAction`
Returns join action calldata. Raises `MoltraffleError` if raffle is not joinable.

#### `get_draw_calldata(raffle_address: str) -> RaffleAction`
Returns drawWinner calldata. Permissionless after deadline.

#### `get_claim_calldata(raffle_address: str) -> RaffleAction`
Returns claimPrize calldata. Only available if you won.

---

## LangChain / LangGraph

```python
from moltraffle import MoltraffleToolkit

toolkit = MoltraffleToolkit()
tools = toolkit.get_tools()
# tools: [ListRafflesTool, GetRaffleTool, CreateRaffleCalldataTool, JoinRaffleCalldataTool]

# Use with any LangChain agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
executor.invoke({"input": "Find the active raffle with the best prize and show me how to join it."})
```

**Available tools:**
| Tool | Name | Description |
|---|---|---|
| `ListRafflesTool` | `list_moltraffle_raffles` | List active raffles |
| `GetRaffleTool` | `get_moltraffle_raffle` | Get raffle by address |
| `CreateRaffleCalldataTool` | `create_moltraffle_raffle_calldata` | Get create calldata |
| `JoinRaffleCalldataTool` | `join_moltraffle_raffle_calldata` | Get join calldata |

---

## Platform Info

| Field | Value |
|---|---|
| Network | Base mainnet (chain 8453) |
| Currency | USDC |
| Factory | `0xd921A03dd1d78cD030FC769feB944f018c00F1a7` |
| Randomness | Chainlink VRF v2+ |
| API Docs | `https://moltraffle.fun/api/config` |
| CORS | `Access-Control-Allow-Origin: *` |

## Links

- Website: [moltraffle.fun](https://moltraffle.fun)
- GitHub: [github.com/Hizarcu/moltraffle-python-sdk](https://github.com/Hizarcu/moltraffle-python-sdk)
- PyPI: [pypi.org/project/moltraffle](https://pypi.org/project/moltraffle/)
- Explorer: [basescan.org](https://basescan.org/address/0xd921A03dd1d78cD030FC769feB944f018c00F1a7)
