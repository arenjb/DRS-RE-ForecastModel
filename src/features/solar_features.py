import pvlib
import pandas as pd

BHADLA_LATITUDE = 27.53
BHADLA_LONGITUDE = 71.07
BHADLA_ALTITUDE = 225  # meters above the sea level

def add_solar_features(df):
    location =pvlib.location.Location(
        latitude = BHADLA_LATITUDE,
        longitude = BHADLA_LONGITUDE,
        altitude = BHADLA_ALTITUDE,
        tz = 'Asia/Kolkata'
    )
    solar_position = location.get_solarposition(df.index)

    df['solar_zenith_angle'] = solar_position['apparent_zenith']
    df['solar_azimuth'] = solar_position['azimuth']

    clear_sky = location.get_clearsky(df.index)
    df['clear_sky_ghi'] = clear_sky['ghi']
    df['clear_sky_index'] = (df['ghi'] / clear_sky['ghi'].clip(lower=1)).clip(upper=1.5)  # Avoid division by zero and cap at 1

    dni_et = pvlib.irradiance.get_extra_radiation(df.index)
    df['dni_extra'] = dni_et

    sun_times = location.get_sun_rise_set_transit(df.index.normalize().unique().tz_localize('Asia/Kolkata'), method='spa')
    df['date'] = df.index.normalize().tz_localize('Asia/Kolkata')
    df['sunrise_offset_min'] = (df.index.tz_localize('Asia/Kolkata') - df['date'].map(sun_times['sunrise'])).dt.total_seconds() / 60
    df['sunset_offset_min'] = (df.index.tz_localize('Asia/Kolkata') - df['date'].map(sun_times['sunset'])).dt.total_seconds() / 60
    df.drop(columns=['date'], inplace=True)
    return df

