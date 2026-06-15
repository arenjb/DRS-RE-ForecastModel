import pandas as pd
from pathlib import Path
from solar_sim import simulate_solar_power
from wind_sim import simulate_wind_power

PROJECT_ROOT = Path(__file__).resolve().parents[2]

df_bhadla = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "bhadla_weather.parquet")
df_muppandal = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "muppandal_weather.parquet")

# Rename columns to match the expected input for the simulation functions
df_bhadla.index.name = 'time'
df_muppandal.index.name = 'time'

df_bhadla = df_bhadla.drop(columns = ["expver", "number"], errors='ignore').resample('15min').interpolate(method='time')
df_muppandal = df_muppandal.drop(columns = ["expver", "number"], errors='ignore').resample('15min').interpolate(method='time')

# Generate synthetic power generation data
print("Simulating solar power generation for Bhadla...")
gen_bhadla = simulate_solar_power(df_bhadla)
gen_bhadla.to_parquet(PROJECT_ROOT / "data" / "synthetic" / "bhadla_generation.parquet")
print("Bhadla generation data saved.")

print("Simulating wind power generation for Muppandal...")
gen_muppandal = simulate_wind_power(df_muppandal)
gen_muppandal.to_parquet(PROJECT_ROOT / "data" / "synthetic" / "muppandal_generation.parquet")
print("Muppandal generation data saved.")