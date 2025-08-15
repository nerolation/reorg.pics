#!/usr/bin/env python3
# Check depth reporting differences

from pyxatu import PyXatu
import pandas as pd

print("Analyzing depth reporting differences...")

with PyXatu() as xatu:
    # Get recent reorgs (last 7 days)
    from datetime import datetime
    current_time = datetime.utcnow()
    genesis_time = datetime(2020, 12, 1, 12, 0, 23)
    seconds_since_genesis = (current_time - genesis_time).total_seconds()
    current_slot = int(seconds_since_genesis / 12)
    start_slot = current_slot - (7 * 7200)
    
    print(f"Checking slots {start_slot} to {current_slot}")
    
    reorg_query = f"""
    SELECT 
        slot - depth as slot,
        depth
    FROM beacon_api_eth_v1_events_chain_reorg
    WHERE slot BETWEEN {start_slot} AND {current_slot}
        AND meta_network_name = 'mainnet'
    ORDER BY slot DESC
    """
    
    reorgs = xatu.raw_query(reorg_query)
    
    print(f"Found {len(reorgs)} reorg reports")
    
    if len(reorgs) > 0:
        # Find slots with multiple depth values
        slot_depths = reorgs.groupby('slot')['depth'].apply(list).to_dict()
        
        conflicts = {slot: depths for slot, depths in slot_depths.items() 
                    if len(set(depths)) > 1}
        
        print(f"\nTotal unique slots: {len(slot_depths)}")
        print(f"Slots with conflicting depths: {len(conflicts)}")
        
        if conflicts:
            print(f"\nExamples of conflicting depth reports:")
            for slot, depths in list(conflicts.items())[:5]:
                print(f"  Slot {slot}: depths reported = {depths}")
        
        # Show depth distribution
        print(f"\nDepth distribution (using minimum per slot):")
        min_depths = {slot: min(depths) for slot, depths in slot_depths.items()}
        depth_counts = pd.Series(min_depths).value_counts().sort_index()
        for depth, count in depth_counts.items():
            print(f"  Depth {depth}: {count} slots ({count/len(slot_depths)*100:.1f}%)")
        
        print(f"\nDepth distribution (using maximum per slot):")
        max_depths = {slot: max(depths) for slot, depths in slot_depths.items()}
        depth_counts_max = pd.Series(max_depths).value_counts().sort_index()
        for depth, count in depth_counts_max.items():
            print(f"  Depth {depth}: {count} slots ({count/len(slot_depths)*100:.1f}%)")