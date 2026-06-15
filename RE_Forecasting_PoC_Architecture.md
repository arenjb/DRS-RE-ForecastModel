# RE Generation Forecasting PoC — Architecture Spec

**Product**: Renewable Energy Generation Forecaster for DSM Penalty Avoidance  
**Owner**: Deliverain Research & Solutions  
**Author**: Vimal / Claude  
**Date**: June 2026  
**Target timeline**: 3–4 weeks to working PoC with demo dashboard

---

## 1. Context & Objective

India's Central Electricity Regulatory Commission (CERC) has tightened the Deviation Settlement Mechanism (DSM) for wind and solar generators. Starting April 2027, tolerance bands narrow from ±10% to ±5% for solar and ±15% to ±10% for wind. Revenue impact estimates: ~11% for solar, up to 48% for wind portfolios.

Every renewable IPP in India needs better generation forecasting to avoid these penalties. In CERC public hearings, developers explicitly flagged the absence of hyperlocal weather forecasting models in India. The existing Qualified Coordinating Agency (QCA) ecosystem relies on standard numerical weather prediction (NWP) with basic statistical overlays — adequate under the old regime, insufficient under the new one.

**Objective**: Build a 15-minute-block RE generation forecasting engine that demonstrably reduces deviation vs. a naive NWP/persistence baseline, and quantify the penalty savings in ₹ terms under the new CERC DSM formula.

**Commercial thesis**: Sell the forecasting ML engine to RE developers (ReNew, Hero Future, Sunsure, Sembcorp, Avaada, NTPC Green, etc.) as a plug-in that improves their QCA's scheduling accuracy. Not becoming a QCA ourselves.

---

## 2. PoC Scope

### In scope
- Day-ahead solar generation forecast (15-min blocks, 96 blocks/day)
- Day-ahead wind generation forecast (15-min blocks)
- Intra-day revision capability (update forecast every 3 hours with latest weather)
- DSM penalty calculator (old regime vs. new regime, ₹ impact per MW)
- Streamlit demo dashboard
- Backtested on 3–6 months of historical data

### Out of scope (Phase 2)
- Real-time SCADA integration with live plants
- QCA scheduling portal / SLDC API integration
- BESS dispatch co-optimization
- Curtailment prediction at pooling stations
- Multi-site portfolio aggregation optimization
- Automatic weather station (AWS) hardware integration

---

## 3. CERC DSM Formula

The developer **must** implement this formula exactly — it's the regulatory basis for the entire product.

### Deviation calculation (post-2026 regulation)

```
Dws% = 100 × [(Actual_MWh − Scheduled_MWh) / ((X% × Available_Capacity) + ((100−X)% × Scheduled_MWh))]
```

Where:
- `Actual_MWh` = actual metered generation in a 15-min block
- `Scheduled_MWh` = scheduled/forecasted generation submitted to SLDC
- `Available_Capacity` = installed capacity adjusted for known outages
- `X` = a parameter that CERC reduces over time (currently being phased from 100 toward 0, which shifts the denominator from available capacity toward scheduled generation — making the penalty harsher as scheduled generation becomes smaller relative to capacity)

### Penalty bands (solar, new regime)

| Deviation band | Penalty |
|---|---|
| Within ±5% | No charge |
| 5%–10% over/under | Moderate DSM charge |
| 10%–15% over/under | Higher DSM charge |
| >15% over-injection | Zero payment for excess (developer loses all revenue on the over-injected units) |
| >15% under-injection | Penalty linked to ancillary services market price |

### Penalty bands (wind, new regime)

| Deviation band | Penalty |
|---|---|
| Within ±10% | No charge |
| 10%–15% | Moderate DSM charge |
| >15% over-injection | Zero payment for excess |
| >15% under-injection | Penalty linked to ancillary services market price |

### What this means for the model

The model's accuracy isn't measured in generic RMSE — it's measured in **how many 15-min blocks fall outside the tolerance band** and by how much. A model that's 3% wrong 100% of the time is better than one that's 1% wrong 90% of the time and 20% wrong 10% of the time. Consistency within the band matters more than average accuracy.

---

## 4. Data Sources (All Publicly Available)

The PoC must run entirely on public/free data so demos don't depend on a customer sharing their SCADA.

### 4.1 Weather / NWP

| Source | Resolution | Horizon | Access | URL |
|---|---|---|---|---|
| GFS (NOAA) | 0.25° (~28 km), 3-hourly | 16 days | Free, no auth | https://nomads.ncep.noaa.gov |
| ECMWF ERA5 (reanalysis) | 0.25°, hourly | Historical (1940–present) | Free via CDS API | https://cds.climate.copernicus.eu |
| ECMWF IFS HRES | 0.1°, hourly | 10 days | Free (limited) via Open Data | https://data.ecmwf.int |
| IMD (India Met Dept) | Station-level | Variable | Free registration | https://mausam.imd.gov.in |

**Variables to pull**: GHI (Global Horizontal Irradiance), DNI, DHI, temperature_2m, relative_humidity, wind_speed_10m, wind_speed_100m, wind_direction, cloud_cover_total, cloud_cover_low/mid/high, precipitation, pressure_msl, dewpoint.

### 4.2 Satellite Irradiance

| Source | Resolution | Access | URL |
|---|---|---|---|
| NASA POWER | 0.5°, hourly | Free, REST API | https://power.larc.nasa.gov |
| CERES (NASA) | 1°, hourly | Free | https://ceres.larc.nasa.gov |
| ISRO Bhuvan | 4 km, 15-min | Free registration | https://bhuvan.nrsc.gov.in |

### 4.3 RE Generation Data (for training/backtesting)

Since real plant SCADA is not publicly available, use one of these approaches:

**Option A — Synthetic generation using PVLib / windpowerlib (recommended for PoC)**:
- Use `pvlib-python` to simulate a solar plant's output from weather data (specify panel type, tilt, azimuth, inverter, array size — model a realistic 100 MW plant)
- Use `windpowerlib` to simulate wind turbine output from wind speed profiles (specify turbine model, hub height, power curve)
- This gives you "actual" generation you can forecast against, with realistic weather-driven variability
- Advantage: fully reproducible, no NDA, can generate for any Indian location

**Option B — Open datasets**:
- Kaggle: "Solar Power Generation Data" (34-day, two plants, India) — small but real
- NREL NSRDB + SAM: US-based but useful for model validation
- Open Power System Data (OPSD): European, but good for wind model benchmarking

**Recommended**: Use Option A. Pick two real Indian RE locations:
- Solar: Bhadla, Rajasthan (27.53°N, 71.07°E) — India's largest solar park
- Wind: Muppandal, Tamil Nadu (8.17°N, 77.52°E) — one of India's largest wind clusters

Generate 12 months of synthetic 15-min generation data using pvlib/windpowerlib + ERA5 historical weather. Train on 9 months, validate on 1, test on 2.

---

## 5. Feature Engineering

### 5.1 Calendar features
- `block_of_day`: 0–95 (the 15-min time block index — this is the scheduling unit)
- `hour`, `minute`
- `day_of_week`, `day_of_year`, `month`
- `is_weekend`, `is_holiday` (Indian national holidays)
- `season`: summer/monsoon/post-monsoon/winter (India-specific)

### 5.2 Solar-specific features
- `solar_zenith_angle`, `solar_azimuth` (from `pvlib.solarposition`)
- `clear_sky_ghi` (theoretical max GHI for that location/time — from `pvlib.clearsky`)
- `clear_sky_index` = actual_GHI / clear_sky_GHI (cloud impact ratio, 0–1+)
- `sunrise_offset_minutes`, `sunset_offset_minutes` (time relative to sunrise/sunset)
- `extraterrestrial_irradiance` (top-of-atmosphere)

### 5.3 Wind-specific features
- `wind_speed_hub_height` (extrapolate from 10m/100m using power law or log profile)
- `wind_direction_binned` (8 or 16 compass bins — captures terrain/wake effects)
- `wind_shear_exponent` = log(ws_100m / ws_10m) / log(100/10)
- `air_density` (derived from temperature + pressure — affects power curve)
- `turbulence_intensity` (std of wind speed over rolling window / mean)

### 5.4 Weather derivative features
- `ghi_ramp_1h` = GHI(t) − GHI(t−4) (irradiance change over last hour)
- `cloud_cover_change_3h` = cloud(t) − cloud(t−12)
- `temperature_deviation` = temp(t) − climatological_mean(t) (anomaly from normal)
- `humidity_x_temperature` (interaction — affects panel efficiency)

### 5.5 Lag and rolling features
- Generation lags: `gen_t-1`, `gen_t-4` (1h ago), `gen_t-96` (same block yesterday)
- Rolling generation stats (1h, 4h, 24h windows): mean, std, min, max
- Rolling weather stats (same windows): GHI mean, wind speed std, cloud cover mean
- NWP forecast error lags: `nwp_error_t-1` = actual_gen(t−1) − nwp_forecast(t−1) (lets the model learn systematic NWP bias)

### 5.6 NWP forecast features (the "raw" baseline inputs)
- Day-ahead GFS/ECMWF forecasts for all weather variables at plant location
- Ensemble spread (if using ECMWF ENS): std across ensemble members (captures forecast uncertainty)

**Total feature count**: ~45–60 features depending on how aggressively you create interactions. This aligns with the 45-feature spec already built for the GE Vernova time-series TDD — reuse that template.

---

## 6. Model Architecture

### 6.1 Primary model: LightGBM

Gradient boosted trees on the tabular feature set. Fastest to prototype, strong on structured/tabular data, interpretable feature importances (critical for showing customers *why* the model deviates).

```
Hyperparameter starting points:
- num_leaves: 63
- learning_rate: 0.05
- n_estimators: 1000 (with early stopping)
- min_child_samples: 20
- subsample: 0.8
- colsample_bytree: 0.8
- reg_alpha: 0.1
- reg_lambda: 0.1
- objective: 'regression' (MAE loss preferred — penalizes outliers less than MSE, which aligns with the DSM band structure where large errors are catastrophic but small errors don't matter)
```

Train separate models for:
- Solar day-ahead
- Wind day-ahead
- Solar intra-day revision (uses latest weather observations as additional features)
- Wind intra-day revision

### 6.2 Baselines (must implement for comparison)

| Baseline | Description |
|---|---|
| Persistence | Tomorrow's generation = today's generation (same 15-min block) |
| Climatological | Monthly average generation for each 15-min block |
| Raw NWP | Direct conversion of GFS/ECMWF weather forecast to generation using pvlib/windpowerlib with no ML |

The ML model must beat all three, and the demo must show the comparison visually.

### 6.3 Phase 2 model (out of PoC scope, note for roadmap)

- Temporal Fusion Transformer (TFT) for sequence modeling with attention — handles variable-length inputs and gives temporal attention weights (useful for explainability)
- LSTM encoder-decoder for multi-step-ahead forecasting
- Ensemble blend: LightGBM (tabular strength) + TFT (sequence strength), weighted by recent performance

---

## 7. Forecast Pipeline

### 7.1 Day-ahead forecast

```
Timeline:
- 16:00 Day D-1: Fetch latest GFS/ECMWF NWP run for Day D
- 16:30 D-1: Run feature pipeline
- 17:00 D-1: Generate 96-block forecast for Day D
- 17:30 D-1: Submit schedule to QCA/SLDC (in production; for PoC, log to DB)
```

### 7.2 Intra-day revision

CERC allows intra-day schedule revisions (number varies by state — typically 8–16 revisions per day). Each revision uses the latest observed weather + generation + updated NWP.

```
Every 3 hours during Day D:
- Fetch latest weather observations (if AWS available) or latest NWP update
- Compute NWP error vs. actuals so far today
- Re-run forecast for remaining blocks
- Compare revised forecast vs. current schedule
- If revision reduces expected penalty: flag for schedule update
```

### 7.3 Data flow (PoC)

```
[ERA5 historical weather] ──┐
[GFS/ECMWF NWP forecasts] ──┤──> Feature Pipeline ──> LightGBM ──> 15-min block forecast
[pvlib/windpowerlib synth] ──┤                                          │
[Calendar + solar position] ─┘                                          │
                                                                        ▼
                                                              DSM Penalty Calculator
                                                                        │
                                                                        ▼
                                                              Streamlit Dashboard
```

---

## 8. Evaluation Framework

### 8.1 Statistical metrics (standard)

- **MAE** (Mean Absolute Error) in MW and as % of installed capacity
- **RMSE** in MW
- **nRMSE** (normalized RMSE) = RMSE / installed_capacity — industry standard for RE forecasting
- **Correlation coefficient** (R²)

### 8.2 Regulatory metrics (the ones that matter commercially)

- **Band compliance rate**: % of 15-min blocks where |Dws%| falls within the tolerance band (±5% solar, ±10% wind)
- **Penalty exposure**: total DSM charges in ₹ over the test period, computed using the CERC formula
- **Penalty reduction**: ₹ saved by ML model vs. each baseline

### 8.3 The demo number

The single number that goes into the cold email:

```
"Reduces DSM deviation from X% to Y% on a [100 MW solar / 50 MW wind] site,
saving approximately ₹Z lakhs per year under the April 2027 CERC regime."
```

Work backward from the penalty tables to compute Z. For a 100 MW solar site with ~20% CUF generating ~175 GWh/year, even a 3 percentage point improvement in band compliance rate translates to meaningful savings. Quantify this precisely — it's the pitch.

### 8.4 Backtest structure

- Training: months 1–9 of synthetic data
- Validation: month 10 (hyperparameter tuning)
- Test: months 11–12 (untouched, reported metrics come from here)
- Walk-forward validation: retrain monthly, test on next month (simulates production)

---

## 9. Demo Deliverable — Streamlit Dashboard

The dashboard is the product demo for cold emails. It must make a non-technical asset management head understand the value in 60 seconds.

### Screen 1: Forecast vs. Actual (time-series)

- X-axis: time (15-min blocks over a selected day/week)
- Y-axis: generation in MW
- Lines: actual generation (solid), ML forecast (dashed blue), NWP baseline (dashed grey)
- Shaded band: ±5% (solar) or ±10% (wind) tolerance zone around scheduled
- Red markers on blocks where ML forecast would have breached the band
- Green markers on blocks where ML forecast saves you vs. NWP baseline

### Screen 2: Deviation Distribution

- Histogram of Dws% across all test blocks
- Overlay: old tolerance band vs. new tolerance band
- Annotation: "X% of blocks within band (ML) vs. Y% (NWP baseline)"

### Screen 3: Penalty Calculator

- Input: installed capacity (MW), CUF assumption, PPA tariff (₹/kWh)
- Output table:

| Metric | NWP Baseline | ML Model | Improvement |
|---|---|---|---|
| Blocks within band | X% | Y% | +Z pp |
| Annual DSM penalty | ₹ A lakhs | ₹ B lakhs | ₹ C lakhs saved |
| Revenue impact | −D% | −E% | F pp recovered |

### Screen 4: Feature Importance

- SHAP summary plot showing top 15 features driving the forecast
- Purpose: builds trust ("the model is using physically meaningful inputs, not black-box noise")

### Screen 5: Site Selector (stretch goal)

- Dropdown to switch between Bhadla (solar) and Muppandal (wind)
- Map showing site location
- Auto-updates all screens

---

## 10. Tech Stack

| Component | Tool | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Weather data fetch | `cdsapi` (ERA5), `herbie` (GFS/ECMWF GRIB) | `herbie` is excellent for NWP data |
| Solar simulation | `pvlib-python` | System modeling, clear-sky, solar position |
| Wind simulation | `windpowerlib` | Turbine power curves, hub-height extrapolation |
| Feature engineering | `pandas`, `numpy` | |
| Model | `lightgbm` | |
| Explainability | `shap` | SHAP values for feature importance |
| Evaluation | `scikit-learn` | MAE, RMSE, custom DSM penalty function |
| Dashboard | `streamlit` | Single-page app, deployable to Streamlit Cloud for sharing |
| Plotting | `plotly` | Interactive charts in Streamlit |
| Data storage | SQLite or Parquet files | Lightweight for PoC, no database setup |

---

## 11. Timeline

| Week | Deliverable |
|---|---|
| Week 1 | Data pipeline: fetch ERA5 + GFS for two Indian sites, generate synthetic solar + wind generation via pvlib/windpowerlib. Validate data quality. |
| Week 2 | Feature engineering pipeline + LightGBM training for solar day-ahead. Implement CERC DSM penalty calculator. Baseline models (persistence, climatological, raw NWP). |
| Week 3 | Wind model. Intra-day revision logic. Backtesting framework (walk-forward). SHAP integration. |
| Week 4 | Streamlit dashboard (all 5 screens). Package and document. Internal demo to Vimal + Gokul. Compute the "cold email number." |

---

## 12. Success Criteria

The PoC is demo-ready when:

1. Solar day-ahead forecast achieves ≥85% of 15-min blocks within ±5% band on the test set (vs. NWP baseline at ~65–70%)
2. Wind day-ahead forecast achieves ≥80% of blocks within ±10% band (vs. NWP baseline at ~55–65%)
3. Penalty savings are quantified in ₹ lakhs/year for a reference 100 MW site
4. Streamlit dashboard loads, runs, and tells the story in under 60 seconds
5. SHAP plot confirms physically meaningful feature rankings (GHI, cloud cover, wind speed dominate — not calendar artifacts)

---

## 13. Phase 2 Roadmap (Post-PoC)

Once the PoC validates the approach and the cold email pipeline starts generating responses:

- **Real SCADA integration**: connect to a pilot customer's historian (TSDE or third-party) for live generation data instead of synthetic
- **Curtailment prediction**: predict grid congestion at pooling stations using historical curtailment patterns + weather + generation forecast — this is the genuinely novel feature nobody in India offers
- **Portfolio aggregation optimizer**: ML-driven scheduling across multiple wind + solar sites at a pooling station to minimize net deviation (cross-asset balancing)
- **BESS co-optimization**: if the site has battery storage, optimize charge/discharge schedule to absorb forecast errors before they become deviations
- **TFT/LSTM ensemble**: upgrade from pure LightGBM to sequence models for better multi-step-ahead accuracy
- **Automatic weather station integration**: ingest hyperlocal AWS data (site-level temperature, irradiance, wind) for intra-day corrections — this is the "hyperlocal forecasting" gap the industry flagged

---

## 14. Key References

- CERC DSM Regulations 2024 (current in force): https://cercind.gov.in
- CERC September 2025 draft on tightened F&S for wind/solar
- Forum of Regulators — Model Regulations on F&S: https://forumofregulators.gov.in
- pvlib-python documentation: https://pvlib-python.readthedocs.io
- windpowerlib documentation: https://windpowerlib.readthedocs.io
- LightGBM documentation: https://lightgbm.readthedocs.io
- SHAP documentation: https://shap.readthedocs.io
- NASA POWER API: https://power.larc.nasa.gov/docs/
- Herbie (NWP data access): https://herbie.readthedocs.io
- ERA5 via CDS API: https://cds.climate.copernicus.eu
