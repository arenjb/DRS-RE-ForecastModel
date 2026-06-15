import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Load real data
with open(PROJECT_ROOT / "dashboard_data.json", 'r') as f:
    data = json.load(f)

# Read original HTML
html_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_Light.html"
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Create injection script - this will run AFTER all other code
injection_script = f"""
// ============================================================
// REAL DATA INJECTION FROM LIGHTGBM MODELS
// ============================================================
const realData = {json.dumps(data)};

// Override the performance objects with real data
function updateWithRealMetrics() {{
  // Store real metrics globally
  window.realMetrics = {{
    solar: {{
      mae: '{data['solar']['ml']['mae']:.3f}',
      rmse: '{data['solar']['ml']['rmse']:.3f}',
      nrmse: '{data['solar']['ml']['nrmse']:.2f}%',
      r2: '{data['solar']['ml']['r2']:.3f}',
      band: '{data['solar']['ml']['inband_pct']:.0f}%',
      base: '{data['solar']['nwp']['inband_pct']:.0f}%'
    }},
    wind: {{
      mae: '{data['wind']['ml']['mae']:.3f}',
      rmse: '{data['wind']['ml']['rmse']:.3f}',
      nrmse: '{data['wind']['ml']['nrmse']:.2f}%',
      r2: '{data['wind']['ml']['r2']:.3f}',
      band: '{data['wind']['ml']['inband_pct']:.0f}%',
      base: '{data['wind']['nwp']['inband_pct']:.0f}%'
    }}
  }};

  // Update model-perf-table with real values
  const perfTable = document.getElementById('model-perf-table');
  if (perfTable) {{
    const site = currentSite === 'solar' ? 'solar' : 'wind';
    const perf = window.realMetrics[site];
    perfTable.innerHTML = `
      <tr><th>Metric</th><th>ML Model</th><th>NWP</th></tr>
      <tr><td>MAE</td><td class="highlight">${{perf.mae}} MW</td><td>—</td></tr>
      <tr><td>RMSE</td><td class="highlight">${{perf.rmse}} MW</td><td>—</td></tr>
      <tr><td>nRMSE</td><td class="highlight">${{perf.nrmse}}</td><td>—</td></tr>
      <tr><td>R²</td><td class="highlight">${{perf.r2}}</td><td>—</td></tr>
      <tr><td>Band compliance</td><td class="highlight">${{perf.band}}</td><td>${{perf.base}}</td></tr>`;
  }}
}}

// Call update when page loads and when tab is switched
updateWithRealMetrics();

// Hook into switchTab to update when user switches
const origSwitchTab = window.switchTab;
window.switchTab = function(t) {{
  origSwitchTab(t);
  setTimeout(updateWithRealMetrics, 100);
}};

// Hook into switchSite to update when user switches sites
const origSwitchSite = window.switchSite;
window.switchSite = function(t) {{
  origSwitchSite(t);
  setTimeout(updateWithRealMetrics, 100);
}};

console.log('✅ Real LightGBM metrics loaded:', window.realMetrics);
"""

# Find the position right before </script> at the end
closing_script = "</script>"
last_script_pos = content.rfind(closing_script)

if last_script_pos > 0:
    # Insert before the closing </script>
    content = content[:last_script_pos] + "\n" + injection_script + "\n" + content[last_script_pos:]

    # Save
    output_path = PROJECT_ROOT / "RE_Forecasting_PoC_Dashboard_LIVE.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Successfully injected real metrics into HTML!")
    print(f"📊 Output: {output_path}")
    print(f"\n📈 Injected Data:")
    print(f"  Bhadla Solar: MAE={data['solar']['ml']['mae']:.3f} MW, In-band={data['solar']['ml']['inband_pct']:.1f}%")
    print(f"  Muppandal Wind: MAE={data['wind']['ml']['mae']:.3f} MW, In-band={data['wind']['ml']['inband_pct']:.1f}%")
    print(f"\n⚠️  Open the HTML in a local server (not file://):")
    print(f"    python -m http.server 8000")
    print(f"    Then visit: http://localhost:8000/RE_Forecasting_PoC_Dashboard_LIVE.html")
else:
    print("❌ Could not find </script> tag in HTML")
