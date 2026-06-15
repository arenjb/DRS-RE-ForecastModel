import pandas as pd
import numpy as np
from pathlib import Path
from features.solar_features import add_solar_features
from features.wind_features import add_wind_features

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def add_calendar_features(df):
    df['hour'] =  df.index.hour
    df['minute'] = df.index.minute
    df['day_of_week'] = df.index.dayofweek
    df['day_of_year'] = df.index.dayofyear
    df['month'] = df.index.month
    df['block_of_day'] = df.index.hour *  4 + df.index.minute // 15
    df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
    df['season'] = (df.index.month).map({
        12: 'winter', 1: 'winter', 2: 'winter',
        3: 'summer', 4: 'summer', 5: 'summer',
        6: 'monsoon', 7: 'monsoon', 8: 'monsoon', 9: 'monsoon',
        10: 'post_monsoon', 11: 'post_monsoon'
    })
    return df

def add_weather_derivatives(df):
    ghi = (df['ssrd'] / 3600).clip(lower=0)  # Convert from J/m² to W/m² and ensure non-negative
    df['ghi'] = ghi
    df['ghi_ramp_1h'] = ghi - ghi.shift(4)  # 4 blocks of 15 minutes = 1 hour
    df['cloud_cover_change_3h'] = df['tcc'] - df['tcc'].shift(12)  # 12 blocks of 15 minutes = 3 hours
    df['relative_humidity'] = 100 * (
        np.exp((17.625 * (df['d2m'] - 273.15)) / (243.04 + (df['d2m'] - 273.15))) /
        np.exp((17.625 * (df['t2m'] - 273.15)) / (243.04 + (df['t2m'] - 273.15)))
    )
    df['wind_speed_10m'] = np.sqrt(df['u10']**2 + df['v10']**2)
    df['wind_speed_100m'] = np.sqrt(df['u100']**2 + df['v100']**2)
    df['wind_direction'] = np.degrees(np.arctan2(df['u10'], df['v10'])) % 360
    df['wind_shear_exponent'] = (np.log(df['wind_speed_100m'] / df['wind_speed_10m'].clip(lower=0.1)) / np.log(100 / 10))
    df['air_density'] = df['sp'] / (287.05 * df['t2m'])
    return df

def add_lag_features(df, generation):
    df['gen_t1'] = generation.shift(1)
    df['gen_t4'] = generation.shift(4)
    df['gen_t96'] = generation.shift(96)
    gen_lagged = generation.shift(1)
    for window in [4, 16, 96]:
        df[f"gen_roll_mean_{window}"] = gen_lagged.rolling(window=window).mean()
        df[f"gen_roll_std_{window}"] = gen_lagged.rolling(window=window).std()
    return df

def build_features(df_weather, generation, site_type):
    
    df = df_weather.copy()
    df = add_calendar_features(df)
    df = add_weather_derivatives(df)
    if site_type == "solar":
        df = add_solar_features(df)
    elif site_type == "wind":
        df = add_wind_features(df)
    df = add_lag_features(df, generation)
    df.dropna(inplace=True)  # Drop rows with NaN values resulting from lag features
    return df