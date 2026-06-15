from windpowerlib import WindTurbine, ModelChain
import pandas as pd
import numpy as np

MUPPANDAL_LATITUDE = 8.12
MUPPANDAL_LONGITUDE = 77.55
TURBINE_TYPE = "V80/2000"
HUB_HEIGHT = 80  # meters
N_TURBINES = 25

def simulate_wind_power(df_weather):

    # Computing wind speed magnitude from u and v components
    ws_10m = np.sqrt(df_weather['u10']**2 + df_weather['v10']**2)
    ws_100m = np.sqrt(df_weather['u100']**2 + df_weather['v100']**2)

    # Buildl windpowerlib weather dataframe
    weather = pd.DataFrame({
        ('wind_speed', 10): ws_10m,
        ('wind_speed', 100): ws_100m,
        ('temperature', 2): df_weather['t2m'],  # Convert from Kelvin to Celsius
        ('pressure', 0): df_weather['sp']  # surface pressure
    }, index=df_weather.index)

    weather.columns = pd.MultiIndex.from_tuples(weather.columns)

    # Create turbine and plant objects
    turbine = WindTurbine(turbine_type = TURBINE_TYPE, hub_height = HUB_HEIGHT)
    mc = ModelChain(turbine, wind_speed_model = 'interpolation_extrapolation').run_model(weather)

    # Scale the power output by the number of turbines
    generation_mw = (mc.power_output * N_TURBINES / 1e6).clip(lower=0)  # Convert W to MW and ensure non-negative
    return pd.DataFrame({
        'generation_mw': generation_mw
    }, index=df_weather.index)