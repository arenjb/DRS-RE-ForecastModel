import pandas as pd
import lightgbm as lgb
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

def train_model(site_name, site_type, feature_cols):
    weather = pd.read_parquet(PROJECT_ROOT  / "data" / "processed" / f"{site_name}_weather.parquet")
    generation = pd.read_parquet(PROJECT_ROOT  / "data" / "synthetic" / f"{site_name}_generation.parquet")['generation_mw']

    weather = weather.drop(columns = ["expver", "number"], errors='ignore')
    weather = weather.resample('15min').interpolate(method='time')

    df = build_features(weather, generation, site_type)

    X = df[feature_cols].dropna()
    y = df['gen_t1'].shift(-1).reindex(X.index).dropna()
    mask = X.notna().all(axis=1) & y.notna()
    X, y = X[mask], y[mask]

    n = len(X)
    train_end = int(0.75 * n)
    val_end = int(0.83 * n)

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    model = lgb.LGBMRegressor(
        num_leaves=63,
        learning_rate=0.05,
        n_estimators=1000,  
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,   
        reg_alpha=0.1,
        reg_lambda=0.1,
        objective='mae'
    )

    model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)])
    
    model_path =  PROJECT_ROOT / "models" / f"{site_name}_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model for {site_name} saved to {model_path}")
    return model, X_test, y_test

if __name__ ==  "__main__":
    print("Training model for Bhadla (solar)...")
    model_bhadla, X_test_bhadla, y_test_bhadla = train_model("bhadla", "solar", FEATURE_COLS_SOLAR)

    print("\nTraining model for Muppandal (wind)...")
    model_muppandal, X_test_muppandal, y_test_muppandal = train_model("muppandal", "wind", FEATURE_COLS_WIND)