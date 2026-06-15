import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Load dashboard data
with open(PROJECT_ROOT / "dashboard_data.json", 'r') as f:
    data = json.load(f)

# Read original HTML
html_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light.html"
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract metrics
solar_mae = data['solar']['lightgbm']['mae']
solar_rmse = data['solar']['lightgbm']['rmse']
solar_nrmse = data['solar']['lightgbm']['nrmse']
solar_r2 = data['solar']['lightgbm']['r2']
solar_penalty = data['solar']['penalty']['annual_inr']
solar_inband = data['solar']['penalty']['percent_in_band']

wind_mae = data['wind']['lightgbm']['mae']
wind_rmse = data['wind']['lightgbm']['rmse']
wind_nrmse = data['wind']['lightgbm']['nrmse']
wind_r2 = data['wind']['lightgbm']['r2']
wind_penalty = data['wind']['penalty']['annual_inr']
wind_inband = data['wind']['penalty']['percent_in_band']

# Format numbers
solar_mae_str = f"{solar_mae:.2f}"
wind_mae_str = f"{wind_mae:.3f}"

# Create data object that will be injected
data_object = f"""
// ============================================================
// INJECTED REAL DATA FROM LIGHTGBM MODELS
// ============================================================
const realMetrics = {{
  solar: {{ mae: {solar_mae}, rmse: {solar_rmse}, nrmse: {solar_nrmse}, r2: {solar_r2}, penalty: {solar_penalty}, inband: {solar_inband} }},
  wind: {{ mae: {wind_mae}, rmse: {wind_rmse}, nrmse: {wind_nrmse}, r2: {wind_r2}, penalty: {wind_penalty}, inband: {wind_inband} }}
}};
"""

# Replace the hardcoded metrics in renderInsightsTab function
# Original: {mae:'1.8 MW',rmse:'2.6 MW',nrmse:'2.6%',r2:'0.987',band:'87%',base:'65%'}
# With: real values

old_solar_perf = r"\{mae:'1\.8 MW',rmse:'2\.6 MW',nrmse:'2\.6%',r2:'0\.987',band:'87%',base:'65%'\}"
new_solar_perf = f"{{mae:'{solar_mae_str} MW',rmse:'{solar_rmse:.2f} MW',nrmse:'{solar_nrmse:.2f}%',r2:'{solar_r2:.3f}',band:'{solar_inband:.0f}%',base:'65%'}}"

old_wind_perf = r"\{mae:'2\.1 MW',rmse:'3\.4 MW',nrmse:'6\.8%',r2:'0\.961',band:'82%',base:'58%'\}"
new_wind_perf = f"{{mae:'{wind_mae_str} MW',rmse:'{wind_rmse:.2f} MW',nrmse:'{wind_nrmse:.2f}%',r2:'{wind_r2:.3f}',band:'{wind_inband:.0f}%',base:'58%'}}"

html_content = re.sub(old_solar_perf, new_solar_perf, html_content)
html_content = re.sub(old_wind_perf, new_wind_perf, html_content)

# Inject real metrics into calcMetrics function
# Find the function and replace the hardcoded percentages
pattern = r"let mlPct=currentSite==='solar'\?87:82;"
replacement = f"let mlPct=realMetrics[currentSite].inband;"
html_content = re.sub(pattern, replacement, html_content)

# Update annual penalty values in the penalty display
# The nwpAnnual and mlAnnual need to use real values
pattern = r"const mlAnnual=[^;]*;"
if "const mlAnnual=" in html_content:
    replacement = f"const mlAnnual=realMetrics[currentSite].penalty;"
    html_content = re.sub(pattern, replacement, html_content)

# Insert the data object right after the initial script tag
insert_pos = html_content.find("<script>") + len("<script>")
html_content = html_content[:insert_pos] + data_object + html_content[insert_pos:]

# Save updated HTML
output_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light_UPDATED.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Dashboard updated successfully!")
print(f"📊 Output: {output_path}")
print(f"\n📈 Injected Real Metrics:")
print(f"  Solar: MAE={solar_mae_str} MW, NRMSE={solar_nrmse:.2f}%, R²={solar_r2:.4f}, In-band={solar_inband:.1f}%")
print(f"  Wind:  MAE={wind_mae_str} MW, NRMSE={wind_nrmse:.2f}%, R²={wind_r2:.4f}, In-band={wind_inband:.1f}%")
print(f"\n💰 Annual DSM Penalties:")
print(f"  Solar: ₹{solar_penalty:,.0f}")
print(f"  Wind:  ₹{wind_penalty:,.2f}")
print(f"\n⚠️  To view: Open the UPDATED HTML file in a browser (not as file://)")
