# pvlib is a library for simulating solar power of photovoltaic energy systems.
import pvlib
import pandas as pd

#  Variables for the location of the site
BHADLA_LATITUDE = 27.53
BHADLA_LONGITUDE = 71.07
BHADLA_ALTITUDE = 225  # meters above the sea level
AZIMUTH = 180 # south-facing panels
TILT = 27 # panel tilt angle
PLANT_CAPACITY_MW = 100 

def simulate_solar_power(df_weather):
    # Create a location object for the site
    location = pvlib.location.Location(latitude = BHADLA_LATITUDE, longitude = BHADLA_LONGITUDE, altitude = BHADLA_ALTITUDE, tz= 'Asia/Kolkata')

    # Convert ERAS ssrd to GHI (Global Horizontal Irradiance)
    ghi = (df_weather['ssrd']/3600).clip(lower=0)  # Convert from J/m^2 to W/m^2 and ensure non-negative

    solar_position = location.get_solarposition(df_weather.index) # Gives Zenith, Azimuth and Apparent Zenith

    # DNI and DHI estimation using the Erbs model
    dni_dhi = pvlib.irradiance.erbs(ghi, solar_position['zenith'], df_weather.index)

    # Plane of array
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt = TILT,
        surface_azimuth = AZIMUTH,
        solar_zenith = solar_position['apparent_zenith'],
        solar_azimuth = solar_position['azimuth'],
        dni = dni_dhi['dni'],
        dhi = dni_dhi['dhi'],
        ghi = ghi
    )

    temp_c = df_weather['t2m'] - 273.15  # Convert from Kelvin to Celsius
    # Actual cell temperature estimation using the Faiman model
    temp_cell = pvlib.temperature.faiman(poa['poa_global'], temp_c)

    #Conversion
    temp_factor = 1 - 0.004 * (temp_cell - 25)  # Assuming 25°C as the reference temperature

    generation_mw = (PLANT_CAPACITY_MW * (poa['poa_global'] / 1000) * temp_factor).clip(lower=0)  # Convert W/m^2 to MW and ensure non-negative
    return pd.DataFrame({
        'generation_mw': generation_mw
    }, index=df_weather.index)