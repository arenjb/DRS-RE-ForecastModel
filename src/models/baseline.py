import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def persistence_baseline(generation_series):
    """
    Persistence baseline: forecast = last observed generation.
    Returns predictions shifted forward by 1 block.
    """
    return generation_series.shift(1)

def same_block_yesterday_baseline(generation_series):
    """
    Same-block-yesterday: forecast = generation from 24h ago (96 blocks).
    """
    return generation_series.shift(96)

def nwp_baseline(site_name):
    """
    Raw NWP baseline: use synthetic generation directly (no ML refinement).
    
    Args:
        site_name: "bhadla" or "muppandal"
    
    Returns:
        pandas Series of generation_mw from synthetic parquet
    """
    path = PROJECT_ROOT / "data" / "synthetic" / f"{site_name}_generation.parquet"
    df = pd.read_parquet(path)
    return df['generation_mw']

if __name__ == "__main__":
    # Test: load Bhadla generation and compute baselines
    gen = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / "bhadla_generation.parquet")['generation_mw']
    
    persistence = persistence_baseline(gen)
    yesterday = same_block_yesterday_baseline(gen)
    nwp = nwp_baseline("bhadla")
    
    print(f"Generation shape: {gen.shape}")
    print(f"Persistence forecast (first 5): {persistence.head().values}")
    print(f"Same-block-yesterday forecast (first 5): {yesterday.head().values}")
    print(f"NWP baseline (first 5): {nwp.head().values}")
