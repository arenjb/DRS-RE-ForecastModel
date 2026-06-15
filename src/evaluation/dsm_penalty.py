import numpy as np
import pandas as pd

def compute_dsm_penalty(scheduled_mw, actual_mw, site_type, penalty_slab=None):
    """
    Compute DSM penalty for a single 15-min block.
    
    Args:
        scheduled_mw: scheduled generation (MW)
        actual_mw: actual generation (MW)
        site_type: "solar" or "wind"
        penalty_slab: dict with deviation % ranges (optional)
    
    Returns:
        dict with penalty_inr, deviation_percent, within_band
    """
    if penalty_slab is None:
        penalty_slab = {
            0: 0,      # 0-5%: ₹0
            15: 0.50,  # 5-15%: ₹0.50/kWh
            25: 1.00,  # 15-25%: ₹1.00/kWh
            100: 1.50  # >25%: ₹1.50/kWh
        }
    
    # Tolerance bands
    if site_type == "solar":
        tolerance_pct = 5.0
    elif site_type == "wind":
        tolerance_pct = 10.0
    else:
        raise ValueError("site_type must be 'solar' or 'wind'")
    
    # Avoid division by zero
    if scheduled_mw < 0.1:
        return {'penalty_inr': 0, 'deviation_pct': 0, 'within_band': True}
    
    deviation_pct = abs(actual_mw - scheduled_mw) / scheduled_mw * 100
    within_band = deviation_pct <= tolerance_pct
    
    if within_band:
        penalty_per_kwh = 0
    else:
        # Find penalty tier
        excess_deviation = deviation_pct - tolerance_pct
        penalty_per_kwh = 1.50  # Default to highest tier
        for threshold in sorted(penalty_slab.keys()):
            if excess_deviation <= threshold:
                penalty_per_kwh = penalty_slab[threshold]
                break
    
    penalty_inr = penalty_per_kwh * actual_mw * 0.25  # 15 min = 0.25 hour
    
    return {
        'penalty_inr': penalty_inr,
        'deviation_pct': deviation_pct,
        'within_band': within_band
    }

def summarize_penalties(scheduled_series, actual_series, site_type):
    """
    Summarize penalties for entire period.
    
    Returns:
        dict with total_penalty_inr, percent_blocks_in_band, avg_deviation_pct
    """
    penalties = []
    for sched, actual in zip(scheduled_series, actual_series):
        p = compute_dsm_penalty(sched, actual, site_type)
        penalties.append(p)
    
    df = pd.DataFrame(penalties)
    total_penalty = df['penalty_inr'].sum()
    pct_in_band = (df['within_band'].sum() / len(df)) * 100
    avg_dev = df['deviation_pct'].mean()
    
    return {
        'total_penalty_inr': total_penalty,
        'percent_blocks_in_band': pct_in_band,
        'avg_deviation_pct': avg_dev
    }

if __name__ == "__main__":
    # Test: 100 MW solar scheduled, 95 MW actual (5% deviation = at boundary)
    result = compute_dsm_penalty(100, 95, "solar")
    print(f"Solar penalty: ₹{result['penalty_inr']:.2f}, deviation: {result['deviation_pct']:.2f}%, in-band: {result['within_band']}")
    
    # Test: 50 MW wind, 55 MW actual (10% deviation = at boundary)
    result = compute_dsm_penalty(50, 55, "wind")
    print(f"Wind penalty: ₹{result['penalty_inr']:.2f}, deviation: {result['deviation_pct']:.2f}%, in-band: {result['within_band']}")
