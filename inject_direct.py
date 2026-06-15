import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Load real data
with open(PROJECT_ROOT / "dashboard_data.json", 'r') as f:
    data = json.load(f)

# Read original HTML
html_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light.html"
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔄 Applying direct replacements...")

# Extract values
solar_ml = data['solar']['ml']
solar_nwp = data['solar']['nwp']
wind_ml = data['wind']['ml']
wind_nwp = data['wind']['nwp']

# Format as strings to match HTML
solar_mae_str = f"'{solar_ml['mae']:.2f} MW'"
solar_rmse_str = f"'{solar_ml['rmse']:.2f} MW'"
solar_nrmse_str = f"'{solar_ml['nrmse']:.2f}%'"
solar_r2_str = f"'{solar_ml['r2']:.3f}'"
solar_band_str = f"'{solar_ml['inband_pct']:.0f}%'"
solar_base_str = f"'{solar_nwp['inband_pct']:.0f}%'"

wind_mae_str = f"'{wind_ml['mae']:.3f} MW'"
wind_rmse_str = f"'{wind_ml['rmse']:.2f} MW'"
wind_nrmse_str = f"'{wind_ml['nrmse']:.2f}%'"
wind_r2_str = f"'{wind_ml['r2']:.3f}'"
wind_band_str = f"'{wind_ml['inband_pct']:.0f}%'"
wind_base_str = f"'{wind_nwp['inband_pct']:.0f}%'"

# Define replacements (old -> new)
replacements = [
    # SOLAR
    ("'1.8 MW'", solar_mae_str),
    ("'2.6 MW'", solar_rmse_str),
    ("'2.6%'", solar_nrmse_str),
    ("'0.987'", solar_r2_str),

    # WIND
    ("'2.1 MW'", wind_mae_str),
    ("'3.4 MW'", wind_rmse_str),
    ("'6.8%'", wind_nrmse_str),
    ("'0.961'", wind_r2_str),

    # In-band percentages
    ("mlPct=currentSite==='solar'?87:82;", f"mlPct=currentSite==='solar'?{solar_ml['inband_pct']:.0f}:{wind_ml['inband_pct']:.0f};"),
    ("nwpPct=currentSite==='solar'?65:58;", f"nwpPct=currentSite==='solar'?{solar_nwp['inband_pct']:.0f}:{wind_nwp['inband_pct']:.0f};"),

    # ML and NWP rates for penalty calculator
    ("const mlRate=currentSite==='solar'?0.87:0.82;", f"const mlRate=currentSite==='solar'?{solar_ml['inband_pct']/100:.3f}:{wind_ml['inband_pct']/100:.3f};"),
    ("const nwpRate=currentSite==='solar'?0.65:0.58;", f"const nwpRate=currentSite==='solar'?{solar_nwp['inband_pct']/100:.3f}:{wind_nwp['inband_pct']/100:.3f};"),
]

replaced_count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        replaced_count += 1
        print(f"  ✅ {old[:30]:<30} → {new[:30]}")
    else:
        print(f"  ⚠️  {old[:30]:<30} (NOT FOUND)")

# Save
output_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_FINAL.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Replaced {replaced_count} values")
print(f"📊 Output: {output_path}")
print(f"\n📈 Real Metrics Injected:")
print(f"  ☀️  Solar: MAE={solar_ml['mae']:.3f} MW, R²={solar_ml['r2']:.4f}, In-band={solar_ml['inband_pct']:.1f}%")
print(f"  💨 Wind:  MAE={wind_ml['mae']:.3f} MW, R²={wind_ml['r2']:.4f}, In-band={wind_ml['inband_pct']:.1f}%")
print(f"\n⚠️  Open with local server:")
print(f"    python -m http.server 8000")
print(f"    Visit: http://localhost:8000/RE_Forecasting_PoC_Dashboard_FINAL.html")
