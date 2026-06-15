import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Load real metrics
with open(PROJECT_ROOT / "dashboard_data.json", 'r') as f:
    data = json.load(f)

# Extract values
solar = data['solar']['lightgbm']
wind = data['wind']['lightgbm']
solar_inband = data['solar']['penalty']['percent_in_band']
wind_inband = data['wind']['penalty']['percent_in_band']

# Read original HTML
html_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light.html"
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements: (old_value, new_value)
replacements = [
    # SOLAR (Bhadla) - 100 MW
    ("'1.8 MW'", f"'{solar['mae']:.2f} MW'"),  # MAE
    ("'2.6 MW'", f"'{solar['rmse']:.2f} MW'"),  # RMSE
    ("'2.6%'", f"'{solar['nrmse']:.2f}%'"),  # nRMSE
    ("'0.987'", f"'{solar['r2']:.3f}'"),  # R²
    ("band:'87%'", f"band:'{solar_inband:.0f}%'"),  # In-band compliance

    # WIND (Muppandal) - 50 MW
    ("'2.1 MW'", f"'{wind['mae']:.3f} MW'"),  # MAE
    ("'3.4 MW'", f"'{wind['rmse']:.2f} MW'"),  # RMSE
    ("'6.8%'", f"'{wind['nrmse']:.2f}%'"),  # nRMSE
    ("'0.961'", f"'{wind['r2']:.3f}'"),  # R²
    ("band:'82%'", f"band:'{wind_inband:.0f}%'"),  # In-band compliance
]

# Apply replacements
original_content = content
for old, new in replacements:
    content = content.replace(old, new)
    if old in original_content:
        print(f"✅ {old:20} → {new}")
    else:
        print(f"⚠️  {old:20} (NOT FOUND)")

# Also replace in penalty calculations if they reference static percentages
content = content.replace("mlPct=currentSite==='solar'?87:82;",
                         f"mlPct=currentSite==='solar'?{solar_inband}:{wind_inband};")

# Save updated HTML
output_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light_FINAL.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Dashboard metrics updated successfully!")
print(f"📊 Output: {output_path}")
print(f"\n📈 Bhadla Solar (100 MW):")
print(f"   MAE: {solar['mae']:.2f} MW")
print(f"   RMSE: {solar['rmse']:.2f} MW")
print(f"   nRMSE: {solar['nrmse']:.2f}%")
print(f"   R²: {solar['r2']:.3f}")
print(f"   In-band: {solar_inband:.1f}%")
print(f"\n💨 Muppandal Wind (50 MW):")
print(f"   MAE: {wind['mae']:.3f} MW")
print(f"   RMSE: {wind['rmse']:.2f} MW")
print(f"   nRMSE: {wind['nrmse']:.2f}%")
print(f"   R²: {wind['r2']:.3f}")
print(f"   In-band: {wind_inband:.1f}%")
