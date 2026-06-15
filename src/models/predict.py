import pandas as pd
import pickle
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from features.feature_pipeline import build_features

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_COLS_SOLAR = [
    'hour', 'minute', 'block_of_day', 'day_of_week', 'day_of_year', 'month',
    'is_weekend', 'ghi', 'ghi_ramp_1h', 'cloud_cover_change_3h',
    'relative_humidity', 'air_density', 'tcc', 'lcc', 'mcc', 'hcc',
    'solar_zenith_angle', 'solar_azimuth', 'clear_sky_ghi', 'clear_sky_index',
    'dni_extra', 'sunrise_offset_min', 'sunset_offset_min',
    'gen_t1', 'gen_t4', 'gen_t96',
    'gen_roll_mean_4', 'gen_roll_std_4', 'gen_roll_mean_16',
    'gen_roll_std_16', 'gen_roll_mean_96', 'gen_roll_std_96'
]

FEATURE_COLS_WIND = [
    'hour', 'minute', 'block_of_day', 'day_of_week', 'day_of_year', 'month',
    'is_weekend', 'wind_speed_10m', 'wind_speed_100m', 'wind_speed_hub',
    'wind_direction', 'wind_direction_bin', 'wind_shear_exponent',
    'turbulence_intensity', 'air_density', 'relative_humidity',
    'tcc', 'sp', 't2m',
    'gen_t1', 'gen_t4', 'gen_t96',
    'gen_roll_mean_4', 'gen_roll_std_4', 'gen_roll_mean_16',
    'gen_roll_std_16', 'gen_roll_mean_96', 'gen_roll_std_96'
]

def predict(site_name, site_type, feature_cols):
    """
    Load trained model and make predictions on test split.
    
    Returns:
        (y_pred, y_test, X_test, model)
    """
    # Load data
    weather = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / f"{site_name}_weather.parquet")
    generation = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / f"{site_name}_generation.parquet")['generation_mw']
    
    # Preprocess
    weather = weather.drop(columns=["expver", "number"], errors='ignore')
    weather = weather.resample('15min').interpolate(method='time')
    
    # Build features
    df = build_features(weather, generation, site_type)
    X = df[feature_cols]
    y = df['gen_t1'].shift(-1)
    
    # Align
    mask = X.notna().all(axis=1) & y.notna()
    X, y = X[mask], y[mask]
    
    # Split
    n = len(X)
    train_end = int(0.75 * n)
    val_end = int(0.83 * n)
    X_test = X.iloc[val_end:]
    y_test = y.iloc[val_end:]
    
    # Load model
    model_path = PROJECT_ROOT / "models" / f"{site_name}_model.pkl"
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Predict
    y_pred = model.predict(X_test)
    
    return y_pred, y_test.values, X_test, model

if __name__ == "__main__":
    print("Solar predictions (Bhadla)...")
    y_pred_solar, y_test_solar, X_test_solar, model_solar = predict("bhadla", "solar", FEATURE_COLS_SOLAR)
    print(f"  Shape: {y_pred_solar.shape}")
    print(f"  Sample predictions (first 10): {y_pred_solar[:10]}")
    
    print("\nWind predictions (Muppandal)...")
    y_pred_wind, y_test_wind, X_test_wind, model_wind = predict("muppandal", "wind", FEATURE_COLS_WIND)
    print(f"  Shape: {y_pred_wind.shape}")
    print(f"  Sample predictions (first 10): {y_pred_wind[:10]}")
