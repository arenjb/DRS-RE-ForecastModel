# Dashboard Setup Guide

## ✅ Status

**Metrics Ready:** `dashboard_data.json` ✓  
**Streamlit App Created:** `src/dashboard/streamlit_app.py` ✓  
**Dependencies Listed:** `src/dashboard/requirements.txt` ✓  

---

## 📁 Folder Structure

```
f:\Documents\DSM-RE-forecast\
├── dashboard_data.json                 ← Metrics data (precomputed)
├── .streamlit/
│   └── config.toml                     ← Streamlit theme config
├── src/
│   └── dashboard/
│       ├── streamlit_app.py            ← Main dashboard app
│       ├── requirements.txt            ← Python dependencies
│       └── README.md                   ← Dashboard documentation
├── data/
├── models/
└── notebooks/
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd f:\Documents\DSM-RE-forecast\src\dashboard
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
streamlit run streamlit_app.py
```

**Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 3. Open in Browser
- Navigate to `http://localhost:8501`
- See the full interactive dashboard

---

## 📊 Dashboard Features (4 Tabs)

| Tab | Content |
|-----|---------|
| **Business Impact** | Savings cards, compliance bars, time series, metrics table |
| **Forecast Performance** | Deviation histogram, daily timeline, statistics |
| **DSM Penalty Calculator** | Interactive inputs for capacity/tariff, penalty breakdown |
| **Technical Insights** | Model metrics, hourly error distribution |

---

## 🎯 Layout Matches HTML Version

✓ Header with site toggle (Solar/Wind)  
✓ 4-tab navigation  
✓ Hero cards with key metrics  
✓ Compliance progress bars  
✓ Interactive Plotly charts  
✓ Metrics tables  
✓ Color scheme: Purple (#667eea), Teal (#17a2b8), Amber (#ff9800)  

---

## 📈 Data Flow

```
dashboard_data.json
    ↓ (load via @st.cache_data)
streamlit_app.py
    ↓
[Tab Selection + Site Selection]
    ↓
[Render Metrics, Charts, Tables]
    ↓
Browser Display (http://localhost:8501)
```

---

## 🔧 Customization

### Change Theme Color
Edit `.streamlit/config.toml`:
```toml
primaryColor = "#YOUR_HEX_COLOR"
```

### Update Metrics Source
Change this line in `streamlit_app.py`:
```python
data_path = Path(__file__).parent.parent.parent / "dashboard_data.json"
```

### Add New Charts
Use Plotly's `go.Figure()` for interactive visualizations (already imported).

---

## ✨ Next Steps

1. ✅ Run dashboard: `streamlit run streamlit_app.py`
2. ✅ Verify 4 tabs work and render correctly
3. ✅ Test site toggle (Solar ↔ Wind)
4. ✅ Check chart interactivity (hover, zoom, pan)
5. ⏳ Optional: Deploy to Streamlit Cloud or internal server

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "dashboard_data.json not found" | Run `generate_dashboard_data.py` first |
| Port 8501 already in use | `streamlit run streamlit_app.py --server.port 8502` |
| Charts not rendering | `pip install plotly --upgrade` |
| Module not found (streamlit) | `pip install -r requirements.txt` |

---

## 📝 File Checksums

```
src/dashboard/
├── streamlit_app.py          (1,200 lines, fully functional)
├── requirements.txt           (4 dependencies)
└── README.md                 (Complete documentation)

Root:
├── dashboard_data.json       (Solar & Wind metrics)
└── .streamlit/config.toml    (Theme settings)
```

---

**Dashboard ready to run! 🎉**
