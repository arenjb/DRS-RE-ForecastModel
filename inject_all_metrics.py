import json
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Load real data
with open(PROJECT_ROOT / "dashboard_data.json", 'r') as f:
    data = json.load(f)

# Read original HTML
html_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light.html"
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract metrics
solar_ml = data['solar']['ml']
solar_nwp = data['solar']['nwp']
wind_ml = data['wind']['ml']
wind_nwp = data['wind']['nwp']

print("🔄 Replacing metrics in HTML...\n")

# ============================================================
# TAB 3: TECHNICAL INSIGHTS - Model Performance Table
# ============================================================
# Solar perf object: {mae:'1.8 MW',rmse:'2.6 MW',nrmse:'2.6%',r2:'0.987',band:'87%',base:'65%'}
solar_perf_old = "{mae:'1.8 MW',rmse:'2.6 MW',nrmse:'2.6%',r2:'0.987',band:'87%',base:'65%'}"
solar_perf_new = f"{{mae:'{solar_ml['mae']:.2f} MW',rmse:'{solar_ml['rmse']:.2f} MW',nrmse:'{solar_ml['nrmse']:.2f}%',r2:'{solar_ml['r2']:.3f}',band:'{solar_ml['inband_pct']:.0f}%',base:'{solar_nwp['inband_pct']:.0f}%'}}"

# Wind perf object: {mae:'2.1 MW',rmse:'3.4 MW',nrmse:'6.8%',r2:'0.961',band:'82%',base:'58%'}
wind_perf_old = "{mae:'2.1 MW',rmse:'3.4 MW',nrmse:'6.8%',r2:'0.961',band:'82%',base:'58%'}"
wind_perf_new = f"{{mae:'{wind_ml['mae']:.3f} MW',rmse:'{wind_ml['rmse']:.2f} MW',nrmse:'{wind_ml['nrmse']:.2f}%',r2:'{wind_ml['r2']:.3f}',band:'{wind_ml['inband_pct']:.0f}%',base:'{wind_nwp['inband_pct']:.0f}%'}}"

content = content.replace(solar_perf_old, solar_perf_new)
content = content.replace(wind_perf_old, wind_perf_new)
print(f"✅ Updated Technical Insights tab metrics")

# ============================================================
# TAB 1: DEVIATION ANALYSIS - mlPct calculation
# ============================================================
# Replace: mlPct=currentSite==='solar'?87:82;
old_pct = "mlPct=currentSite==='solar'?87:82;"
new_pct = f"mlPct=currentSite==='solar'?{solar_ml['inband_pct']:.0f}:{wind_ml['inband_pct']:.0f};"
content = content.replace(old_pct, new_pct)
print(f"✅ Updated Deviation Analysis tab in-band percentages")

# Replace: nwpPct=currentSite==='solar'?65:58;
old_nwp_pct = "nwpPct=currentSite==='solar'?65:58;"
new_nwp_pct = f"nwpPct=currentSite==='solar'?{solar_nwp['inband_pct']:.0f}:{wind_nwp['inband_pct']:.0f};"
content = content.replace(old_nwp_pct, new_nwp_pct)

# ============================================================
# TAB 2: PENALTY CALCULATOR - recalcPenalty()
# ============================================================
# Replace: const mlRate=currentSite==='solar'?0.87:0.82;
old_mlrate = "const mlRate=currentSite==='solar'?0.87:0.82;"
new_mlrate = f"const mlRate=currentSite==='solar'?{solar_ml['inband_pct']/100:.3f}:{wind_ml['inband_pct']/100:.3f};"
content = content.replace(old_mlrate, new_mlrate)

# Replace: const nwpRate=currentSite==='solar'?0.65:0.58;
old_nwprate = "const nwpRate=currentSite==='solar'?0.65:0.58;"
new_nwprate = f"const nwpRate=currentSite==='solar'?{solar_nwp['inband_pct']/100:.3f}:{wind_nwp['inband_pct']/100:.3f};"
content = content.replace(old_nwprate, new_nwprate)

# Replace excess deviation percentages
# Solar: const nwpExcess=type==='solar'?0.04:0.06; const mlExcess=type==='solar'?0.015:0.025;
# We'll estimate these from the actual deviations
solar_ml_excess = np.mean([d for d in data['solar']['ml']['deviations'] if d > 5])  # Above tolerance
solar_nwp_excess = np.mean([d for d in data['solar']['nwp']['deviations'] if d > 5])
wind_ml_excess = np.mean([d for d in data['wind']['ml']['deviations'] if d > 10])
wind_nwp_excess = np.mean([d for d in data['wind']['nwp']['deviations'] if d > 10])

old_excess = "const nwpExcess=type==='solar'?0.04:0.06;const mlExcess=type==='solar'?0.015:0.025;"
new_excess = f"const nwpExcess=type==='solar'?{solar_nwp_excess/100:.3f}:{wind_nwp_excess/100:.3f};const mlExcess=type==='solar'?{solar_ml_excess/100:.3f}:{wind_ml_excess/100:.3f};"
content = content.replace(old_excess, new_excess)

print(f"✅ Updated Penalty Calculator tab rates")

# ============================================================
# Add data object for easy access
# ============================================================
data_script = f"""
<script id="dashboard-metrics-data">
window.dashboardMetrics = {json.dumps(data)};
</script>
"""

# Insert after opening <script> tag
insert_pos = content.find("<script>") + len("<script>")
content = content[:insert_pos] + "\n" + data_script + "\n" + content[insert_pos:]

print(f"✅ Added metrics data object to window")

# ============================================================
# Save updated HTML
# ============================================================
output_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_UPDATED.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ HTML updated successfully!")
print(f"📊 Output: {output_path}")
print(f"\n📈 Bhadla Solar Metrics Updated:")
print(f"   ML:  MAE={solar_ml['mae']:.3f} MW, NRMSE={solar_ml['nrmse']:.2f}%, In-band={solar_ml['inband_pct']:.1f}%")
print(f"   NWP: MAE={solar_nwp['mae']:.3f} MW, NRMSE={solar_nwp['nrmse']:.2f}%, In-band={solar_nwp['inband_pct']:.1f}%")

print(f"\n💨 Muppandal Wind Metrics Updated:")
print(f"   ML:  MAE={wind_ml['mae']:.3f} MW, NRMSE={wind_ml['nrmse']:.2f}%, In-band={wind_ml['inband_pct']:.1f}%")
print(f"   NWP: MAE={wind_nwp['mae']:.3f} MW, NRMSE={wind_nwp['nrmse']:.2f}%, In-band={wind_nwp['inband_pct']:.1f}%")

print(f"\n⚠️  Next: Open the UPDATED HTML in your browser to verify all tabs display correctly")
