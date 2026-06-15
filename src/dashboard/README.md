# RE Forecasting Dashboard

A Streamlit-based interactive dashboard for analyzing renewable energy (solar & wind) forecasting performance and DSM penalty impacts.

## 📁 Project Structure

```
src/dashboard/
├── streamlit_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md              # This file

Data Source:
├── dashboard_data.json    # Pre-computed metrics (in project root)
```

## 🎯 Features

### 4 Interactive Tabs:

1. **Business Impact** — Key metrics, savings analysis, and performance comparison
2. **Forecast Performance** — Deviation analysis, distribution histograms, daily compliance
3. **DSM Penalty Calculator** — Interactive calculator for custom capacity/tariff scenarios
4. **Technical Insights** — Model performance metrics and hourly error distributions

### Site Toggle:
- Switch between **Bhadla Solar (100 MW)** and **Muppandal Wind (50 MW)**
- Metrics update automatically for each site

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit 1.28+

### Installation

```bash
cd f:\Documents\DSM-RE-forecast\src\dashboard
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard will open at `http://localhost:8501` in your browser.

## 📊 Dashboard Layout

### Tab 1: Business Impact
- **Hero Cards:** Annual savings, compliance improvement, forecast accuracy, risk reduction
- **Compliance Bars:** ML vs NWP in-band comparison
- **Time Series Chart:** 30-day daily compliance timeline
- **Technical Metrics Table:** MAE, RMSE, nRMSE, R², Band Compliance

### Tab 2: Forecast Performance (Deviation Analysis)
- **Statistics:** Mean deviation comparison
- **Histogram:** Distribution of deviations (ML vs NWP)
- **Timeline:** Daily band compliance over 90 days
- **Target Line:** 95% compliance benchmark

### Tab 3: DSM Penalty Calculator
- **Input Panel:** Capacity, CUF, PPA tariff, penalty rate
- **Results Panel:** Annual penalties and savings
- **Breakdown Chart:** Blocks by deviation band (0-5%, 5-10%, 10-15%, >15%)

### Tab 4: Technical Insights
- **Performance Table:** MAE, RMSE, nRMSE, R², In-band %
- **Hourly Error Chart:** Error distribution by hour of day

## 📈 Data Source

The dashboard reads from `dashboard_data.json`, which contains:

```json
{
  "solar": {
    "ml": {
      "mae": 0.226,
      "rmse": 0.533,
      "nrmse": 0.533,
      "r2": 0.9997,
      "inband_pct": 93.9,
      "annual_penalty_inr": 30.7,
      "hourly_errors": [...],
      "daily_inband": [...],
      "deviations": [...]
    },
    "nwp": { ... }
  },
  "wind": { ... }
}
```

## 🎨 Styling

- **Color Scheme:** 
  - Primary: #667eea (purple)
  - Teal: #17a2b8 (ML Model)
  - Amber: #ff9800 (NWP Baseline)
  - Green: #28a745 (Success)

- **Typography:** Clean sans-serif with 500-800px card widths
- **Responsive:** Full-width layout with adaptive columns

## 🔧 Customization

### Change Color Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#YOUR_COLOR"
```

### Modify Metrics Calculation
Edit the hero card calculations in `streamlit_app.py`:
```python
savings_lakhs = (nwp['annual_penalty_inr'] - ml['annual_penalty_inr']) / 100000
```

### Add New Visualizations
- Use Plotly (already imported) for interactive charts
- Reference `ml` and `nwp` dictionaries from `dashboard_data.json`

## 📝 Notes

- **Caching:** Dashboard data is cached with `@st.cache_data` for fast loads
- **State Management:** Uses `st.session_state` for site/tab persistence
- **Responsive:** Mobile-friendly with adaptive column layouts

## 🐛 Troubleshooting

**Issue:** "dashboard_data.json not found"
- Ensure `generate_dashboard_data.py` has been run
- File should be at `f:\Documents\DSM-RE-forecast\dashboard_data.json`

**Issue:** Charts not rendering
- Check browser console (F12) for errors
- Ensure Plotly is installed: `pip install plotly --upgrade`

**Issue:** Streamlit port already in use
- Run on different port: `streamlit run streamlit_app.py --server.port 8502`

## 📧 Support

For issues or questions, refer to the main project README.
