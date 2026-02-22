"""Basic usage of the moltraffle Python SDK."""
from moltraffle import MoltraffleClient
import time

client = MoltraffleClient()

# 1. List active raffles
print("=== Active Raffles ===")
result = client.list_raffles(status="active")
print(f"Found {result.total} active raffle(s)\n")
for r in result.raffles[:5]:
    print(f"  {r.title}")
    print(f"  Address:      {r.address}")
    print(f"  Entry Fee:    {r.entry_fee_formatted} USDC")
    print(f"  Prize Pool:   {r.prize_pool_formatted} USDC")
    print(f"  Participants: {r.current_participants}")
    print()

# 2. Get single raffle detail (replace with a real address)
if result.raffles:
    raffle_address = result.raffles[0].address
    print(f"=== Raffle Detail: {raffle_address} ===")
    raffle = client.get_raffle(raffle_address)
    print(f"Status: {raffle.status_label}")
    if raffle.actions and raffle.actions.join and raffle.actions.join.available:
        print("Join action IS available")
        print(f"  to:       {raffle.actions.join.to}")
        print(f"  value:    {raffle.actions.join.value}")
        print(f"  calldata: {raffle.actions.join.calldata_example}")
    else:
        reason = raffle.actions and raffle.actions.join and raffle.actions.join.reason
        print(f"Join not available: {reason}")
    print()

# 3. Get calldata to create a raffle
print("=== Create Raffle Calldata ===")
deadline = int(time.time()) + 7 * 24 * 3600  # 7 days from now
calldata = client.get_create_calldata(
    title="My Test Raffle",
    description="A fun raffle open to everyone on Base mainnet",
    entry_fee="1",           # 1 USDC
    deadline=deadline,
    max_participants=50,
    prize_description="Winner takes the prize pool",
    creator_commission_bps=500,  # 5%
)
print(f"to:       {calldata.to}")
print(f"value:    {calldata.value_formatted}")
print(f"calldata: {calldata.calldata[:40]}...")
print(f"function: {calldata.function}")
