#!/usr/bin/env python
# Test script for pyxatu connection and reorgs function

from pyxatu import PyXatu

# Initialize pyxatu client (will use ~/.pyxatu_config.json)
print("Testing pyxatu connection...")

# Using context manager to ensure proper connection handling
with PyXatu() as xatu:
    # Get reorgs from a recent range (last 1000 slots)
    current_slot = 12367819  # Approximate current slot
    start_slot = current_slot - 1000
    
    # Test using raw_query method
    reorg_query = f"""
    SELECT distinct
        slot - depth as slot,
        depth
    FROM beacon_api_eth_v1_events_chain_reorg
    WHERE slot BETWEEN {start_slot} AND {current_slot}
        AND meta_network_name = 'mainnet'
        AND meta_client_implementation != 'Contributoor'
    ORDER BY slot
    """
    
    print(f"Querying reorgs between slots {start_slot} and {current_slot}...")
    reorgs = xatu.raw_query(reorg_query)
    print(f"Found {len(reorgs)} reorgs")
    
    # Test get_missed_slots
    print("\nGetting missed slots...")
    missed = xatu.get_missed_slots(slot_range=[start_slot, current_slot])
    print(f"Found {len(missed)} missed slots")
    
    # Filter reorgs by missed slots
    reorgs_filtered = reorgs[reorgs["slot"].isin(missed)]
    print(f"Filtered to {len(reorgs_filtered)} reorgs at missed slots")
    
    if len(reorgs_filtered) > 0:
        print("\nSample reorg data:")
        print(reorgs_filtered.head())
    
    # Also test the built-in get_reorgs method
    print("\nTesting built-in get_reorgs method...")
    reorgs_builtin = xatu.get_reorgs(slot=[start_slot, current_slot])
    print(f"Built-in method found {len(reorgs_builtin)} reorgs")
    
    print("\nPyxatu test successful!")