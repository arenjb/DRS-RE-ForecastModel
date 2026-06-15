import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.models.predict import predict, FEATURE_COLS_SOLAR, FEATURE_COLS_WIND
from src.models.baseline import persistence_baseline, nwp_baseline
from src.evaluation.metrics import compute_metrics
from src.evaluation.dsm_penalty import compute_dsm_penalty

PROJECT_ROOT = Path(__file__).resolve().parent

print("🔄 Loading predictions...")
y_pred_solar, y_test_solar, X_test_solar, _ = predict("bhadla", "solar", FEATURE_COLS_SOLAR)
y_pred_wind, y_test_wind, X_test_wind, _ = predict("muppandal", "wind", FEATURE_COLS_WIND)

print("📊 Loading generation data...")
gen_solar = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / "bhadla_generation.parquet")['generation_mw']
gen_wind = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / "muppandal_generation.parquet")['generation_mw']

# Get NWP baseline (synthetic generation as-is)
nwp_solar = gen_solar.iloc[-len(y_test_solar):].values
nwp_wind = gen_wind.iloc[-len(y_test_wind):].values

print("📈 Computing metrics...")

# ============================================================
# SOLAR METRICS (BHADLA)
# ============================================================
metrics_ml_solar = compute_metrics(y_test_solar, y_pred_solar, 100.0)
metrics_nwp_solar = compute_metrics(y_test_solar, nwp_solar, 100.0)

# Penalties for ML
penalties_ml_solar = [compute_dsm_penalty(s, a, "solar") for s, a in zip(y_pred_solar, y_test_solar)]
df_pen_ml_solar = pd.DataFrame(penalties_ml_solar)

# Penalties for NWP baseline
penalties_nwp_solar = [compute_dsm_penalty(s, a, "solar") for s, a in zip(nwp_solar, y_test_solar)]
df_pen_nwp_solar = pd.DataFrame(penalties_nwp_solar)

# Annual penalties
ml_penalty_solar_annual = df_pen_ml_solar['penalty_inr'].sum() * 365 / len(y_test_solar)
nwp_penalty_solar_annual = df_pen_nwp_solar['penalty_inr'].sum() * 365 / len(y_test_solar)

# In-band percentages
ml_inband_solar = (df_pen_ml_solar['within_band'].sum() / len(df_pen_ml_solar)) * 100
nwp_inband_solar = (df_pen_nwp_solar['within_band'].sum() / len(df_pen_nwp_solar)) * 100

# Deviations for histogram (90 days = 1440 blocks)
ml_devs_solar = df_pen_ml_solar['deviation_pct'].values[:1440]
nwp_devs_solar = df_pen_nwp_solar['deviation_pct'].values[:1440]

# Daily compliance (for 90 days)
daily_ml_solar = []
daily_nwp_solar = []
for day in range(90):
    start_idx = day * 96
    end_idx = (day + 1) * 96
    if end_idx <= len(df_pen_ml_solar):
        ml_daily = (df_pen_ml_solar['within_band'].iloc[start_idx:end_idx].sum() / 96) * 100
        nwp_daily = (df_pen_nwp_solar['within_band'].iloc[start_idx:end_idx].sum() / 96) * 100
        daily_ml_solar.append(ml_daily)
        daily_nwp_solar.append(nwp_daily)

# Hourly errors (24 hours from test data)
hourly_errors_ml_solar = []
hourly_errors_nwp_solar = []
for hour in range(24):
    indices = [i for i in range(len(y_test_solar)) if (i % 96) // 4 == hour]
    if indices:
        hour_mae_ml = np.mean(np.abs(y_pred_solar[indices] - y_test_solar[indices]))
        hour_mae_nwp = np.mean(np.abs(nwp_solar[indices] - y_test_solar[indices]))
        hourly_errors_ml_solar.append(hour_mae_ml)
        hourly_errors_nwp_solar.append(hour_mae_nwp)

# ============================================================
# WIND METRICS (MUPPANDAL)
# ============================================================
metrics_ml_wind = compute_metrics(y_test_wind, y_pred_wind, 50.0)
metrics_nwp_wind = compute_metrics(y_test_wind, nwp_wind, 50.0)

# Penalties for ML
penalties_ml_wind = [compute_dsm_penalty(s, a, "wind") for s, a in zip(y_pred_wind, y_test_wind)]
df_pen_ml_wind = pd.DataFrame(penalties_ml_wind)

# Penalties for NWP baseline
penalties_nwp_wind = [compute_dsm_penalty(s, a, "wind") for s, a in zip(nwp_wind, y_test_wind)]
df_pen_nwp_wind = pd.DataFrame(penalties_nwp_wind)

# Annual penalties
ml_penalty_wind_annual = df_pen_ml_wind['penalty_inr'].sum() * 365 / len(y_test_wind)
nwp_penalty_wind_annual = df_pen_nwp_wind['penalty_inr'].sum() * 365 / len(y_test_wind)

# In-band percentages
ml_inband_wind = (df_pen_ml_wind['within_band'].sum() / len(df_pen_ml_wind)) * 100
nwp_inband_wind = (df_pen_nwp_wind['within_band'].sum() / len(df_pen_nwp_wind)) * 100

# Deviations for histogram
ml_devs_wind = df_pen_ml_wind['deviation_pct'].values[:1440]
nwp_devs_wind = df_pen_nwp_wind['deviation_pct'].values[:1440]

# Daily compliance
daily_ml_wind = []
daily_nwp_wind = []
for day in range(90):
    start_idx = day * 96
    end_idx = (day + 1) * 96
    if end_idx <= len(df_pen_ml_wind):
        ml_daily = (df_pen_ml_wind['within_band'].iloc[start_idx:end_idx].sum() / 96) * 100
        nwp_daily = (df_pen_nwp_wind['within_band'].iloc[start_idx:end_idx].sum() / 96) * 100
        daily_ml_wind.append(ml_daily)
        daily_nwp_wind.append(nwp_daily)

# Hourly errors
hourly_errors_ml_wind = []
hourly_errors_nwp_wind = []
for hour in range(24):
    indices = [i for i in range(len(y_test_wind)) if (i % 96) // 4 == hour]
    if indices:
        hour_mae_ml = np.mean(np.abs(y_pred_wind[indices] - y_test_wind[indices]))
        hour_mae_nwp = np.mean(np.abs(nwp_wind[indices] - y_test_wind[indices]))
        hourly_errors_ml_wind.append(hour_mae_ml)
        hourly_errors_nwp_wind.append(hour_mae_nwp)

print("💾 Compiling dashboard data...")

# ============================================================
# COMPILE FINAL JSON
# ============================================================
dashboard_data = {
    "solar": {
        "capacity_mw": 100,
        "site": "Bhadla, Rajasthan",
        "ml": {
            "mae": float(metrics_ml_solar['MAE']),
            "rmse": float(metrics_ml_solar['RMSE']),
            "nrmse": float(metrics_ml_solar['NRMSE (%)']),
            "r2": float(metrics_ml_solar['R²']),
            "inband_pct": float(ml_inband_solar),
            "annual_penalty_inr": float(ml_penalty_solar_annual),
            "hourly_errors": [float(x) for x in hourly_errors_ml_solar],
            "daily_inband": [float(x) for x in daily_ml_solar],
            "deviations": [float(x) for x in ml_devs_solar]
        },
        "nwp": {
            "mae": float(metrics_nwp_solar['MAE']),
            "rmse": float(metrics_nwp_solar['RMSE']),
            "nrmse": float(metrics_nwp_solar['NRMSE (%)']),
            "r2": float(metrics_nwp_solar['R²']),
            "inband_pct": float(nwp_inband_solar),
            "annual_penalty_inr": float(nwp_penalty_solar_annual),
            "hourly_errors": [float(x) for x in hourly_errors_nwp_solar],
            "daily_inband": [float(x) for x in daily_nwp_solar],
            "deviations": [float(x) for x in nwp_devs_solar]
        }
    },
    "wind": {
        "capacity_mw": 50,
        "site": "Muppandal, Tamil Nadu",
        "ml": {
            "mae": float(metrics_ml_wind['MAE']),
            "rmse": float(metrics_ml_wind['RMSE']),
            "nrmse": float(metrics_ml_wind['NRMSE (%)']),
            "r2": float(metrics_ml_wind['R²']),
            "inband_pct": float(ml_inband_wind),
            "annual_penalty_inr": float(ml_penalty_wind_annual),
            "hourly_errors": [float(x) for x in hourly_errors_ml_wind],
            "daily_inband": [float(x) for x in daily_ml_wind],
            "deviations": [float(x) for x in ml_devs_wind]
        },
        "nwp": {
            "mae": float(metrics_nwp_wind['MAE']),
            "rmse": float(metrics_nwp_wind['RMSE']),
            "nrmse": float(metrics_nwp_wind['NRMSE (%)']),
            "r2": float(metrics_nwp_wind['R²']),
            "inband_pct": float(nwp_inband_wind),
            "annual_penalty_inr": float(nwp_penalty_wind_annual),
            "hourly_errors": [float(x) for x in hourly_errors_nwp_wind],
            "daily_inband": [float(x) for x in daily_nwp_wind],
            "deviations": [float(x) for x in nwp_devs_wind]
        }
    },
    "metadata": {
        "generated_at": str(pd.Timestamp.now()),
        "test_samples_solar": int(len(y_test_solar)),
        "test_samples_wind": int(len(y_test_wind)),
        "annual_blocks_solar": int(96 * 365 * 0.5),
        "annual_blocks_wind": int(96 * 365)
    }
}

# Save JSON
output_path = PROJECT_ROOT / "dashboard_data.json"
with open(output_path, 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print(f"✅ Dashboard data generated: {output_path}")
print(f"\n📈 BHADLA SOLAR (100 MW):")
print(f"   ML:  MAE={metrics_ml_solar['MAE']:.3f} MW, R²={metrics_ml_solar['R²']:.4f}, In-band={ml_inband_solar:.1f}%, Penalty=₹{ml_penalty_solar_annual:,.0f}")
print(f"   NWP: MAE={metrics_nwp_solar['MAE']:.3f} MW, R²={metrics_nwp_solar['R²']:.4f}, In-band={nwp_inband_solar:.1f}%, Penalty=₹{nwp_penalty_solar_annual:,.0f}")
print(f"   Improvement: {ml_inband_solar - nwp_inband_solar:.1f}pp in-band, ₹{nwp_penalty_solar_annual - ml_penalty_solar_annual:,.0f} saved")

print(f"\n💨 MUPPANDAL WIND (50 MW):")
print(f"   ML:  MAE={metrics_ml_wind['MAE']:.3f} MW, R²={metrics_ml_wind['R²']:.4f}, In-band={ml_inband_wind:.1f}%, Penalty=₹{ml_penalty_wind_annual:,.0f}")
print(f"   NWP: MAE={metrics_nwp_wind['MAE']:.3f} MW, R²={metrics_nwp_wind['R²']:.4f}, In-band={nwp_inband_wind:.1f}%, Penalty=₹{nwp_penalty_wind_annual:,.0f}")
print(f"   Improvement: {ml_inband_wind - nwp_inband_wind:.1f}pp in-band, ₹{nwp_penalty_wind_annual - ml_penalty_wind_annual:,.0f} saved")
