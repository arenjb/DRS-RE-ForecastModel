import cdsapi
from pathlib import Path

PATH_ROOT = Path(__file__).resolve().parents[2]
client = cdsapi.Client()

dataset = "reanalysis-era5-single-levels"
    
request = {
    "product_type": "reanalysis",
    "data_format": "netcdf",
    "variable": [
        "2m_temperature",
        "2m_dewpoint_temperature",
        "surface_pressure",
        "mean_sea_level_pressure",
        "surface_solar_radiation_downwards",
        "total_cloud_cover",
        "low_cloud_cover",
        "medium_cloud_cover",
        "high_cloud_cover",
        "total_precipitation",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "100m_u_component_of_wind",
        "100m_v_component_of_wind"
    ],
    "day": [
        "01","02","03","04","05","06","07","08","09","10",
        "11","12","13","14","15","16","17","18","19","20",
        "21","22","23","24","25","26","27","28","29","30","31"
    ],
    "time": [
        "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
    ],
}

months_by_year = {
    2025: ["01","02","03","04","05","06","07","08","09","10","11","12"],
    2026: ["01","02","03","04","05","06"]
}

area_by_loc = {
    "Bhadla, Rajasthan": [28.0, 70.5, 27.0, 71.5],
    "Muppandal, Tamil Nadu": [8.5, 77.0, 7.7, 78.0]
}

for year in months_by_year.keys():
    for month in months_by_year.get(year, []):
        for loc in area_by_loc.keys():

            print(f"Downloading data for {year}-{month}")

            request["year"] = str(year)
            request["month"] = [month]
            request["area"] = area_by_loc.get(loc, [])
            
            target = PATH_ROOT / "data" / "raw" / f"weather_{year}_{month}_{loc.replace(', ', '_').replace(' ','_')}.nc"

            client.retrieve(dataset, request, target)

            print(f"Downloaded data for {year}-{month}-{loc} to {target}")
