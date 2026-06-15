import xarray as xr
from glob import glob
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load_site(site_name):
    files = sorted(glob(str(PROJECT_ROOT / "data" / "raw" / f"weather_*_{site_name}.nc")))
    # print(f"Found files: {files}")
    frames = []
    for f in files:
        ds = xr.open_dataset(f, engine = 'netcdf4')
        print(f"Raw file:\n{ds}")
        # Average latitude and longitude to get a single value for the site
        ds_mean = ds.mean(dim=["latitude", "longitude"],skipna=True)
        print(f"After mean of the timestamp:\n{ds_mean}")
        frames.append(ds_mean.to_dataframe())
    df =  pd.concat(frames).sort_index()
    return df

df_bhadla = load_site("Bhadla_Rajasthan")
df_muppandal = load_site("Muppandal_Tamil_Nadu")

df_bhadla.to_parquet(str(PROJECT_ROOT / "data" / "processed" / "bhadla_weather.parquet"))
df_muppandal.to_parquet(str(PROJECT_ROOT / "data" / "processed" / "muppandal_weather.parquet"))