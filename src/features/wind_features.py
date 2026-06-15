import pandas as pd 
import numpy as np

HUB_HEIGHT = 80  # meters

def add_wind_features(df):

    df['wind_speed_hub'] = df['wind_speed_10m'] * (HUB_HEIGHT / 10) ** df['wind_shear_exponent']
    
    # Wind direction binned into 8 compass sectors
    df['wind_direction_bin'] = (df['wind_direction'] // 45).astype(int)
    
    # Turbulence intensity (rolling std / rolling mean over 1 hour)
    ws = df['wind_speed_10m']
    df['turbulence_intensity'] = ws.rolling(4).std() / ws.rolling(4).mean().clip(lower=0.1)
    return df
    
