import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.predict import predict, FEATURE_COLS_SOLAR, FEATURE_COLS_WIND
from models.baseline import nwp_baseline
from evaluation.metrics import compute_metrics
from evaluation.dsm_penalty import compute_dsm_penalty

PROJECT_ROOT = Path(__file__).resolve().parents[2]

st.set_page_config(page_title="DSM RE Forecast PoC", layout="wide")
st.markdown("# DSM Penalty Avoidance — Renewable Energy Forecasting PoC")

# Custom CSS for bordered metrics
st.markdown("""
<style>
.metric-card {
    border: 2px solid #00B4C8;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background-color: #f0f8ff;
}
.metric-card-warning {
    border: 2px solid #ff7f0e;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background-color: #fff8f0;
}
.metric-title {
    font-weight: bold;
    color: #2c3e50;
    font-size: 14px;
    margin-bottom: 5px;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #00B4C8;
}
.metric-delta {
    font-size: 12px;
    color: #2ca02c;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

def metric_card(title, value, delta="", style="teal"):
    """Create a bordered metric card"""
    style_class = "metric-card-warning" if style == "warning" else "metric-card"
    return f"""
    <div class="{style_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta">{delta}</div>
    </div>
    """

@st.cache_resource
def load_all_data():
    y_pred_solar, y_test_solar, X_test_solar, _ = predict("bhadla", "solar", FEATURE_COLS_SOLAR)
    y_pred_wind, y_test_wind, X_test_wind, _ = predict("muppandal", "wind", FEATURE_COLS_WIND)

    gen_solar = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / "bhadla_generation.parquet")['generation_mw']
    gen_wind = pd.read_parquet(PROJECT_ROOT / "data" / "synthetic" / "muppandal_generation.parquet")['generation_mw']

    return {
        'solar': {'y_pred': y_pred_solar, 'y_test': y_test_solar, 'X_test': X_test_solar, 'gen': gen_solar},
        'wind': {'y_pred': y_pred_wind, 'y_test': y_test_wind, 'X_test': X_test_wind, 'gen': gen_wind}
    }

data = load_all_data()

# Get NWP baseline (synthetic generation as-is)
nwp_solar = data['solar']['gen'].iloc[-len(data['solar']['y_test']):].values
nwp_wind = data['wind']['gen'].iloc[-len(data['wind']['y_test']):].values

# Compute all metrics
ml_metrics_solar = compute_metrics(data['solar']['y_test'], data['solar']['y_pred'], 100.0)
nwp_metrics_solar = compute_metrics(data['solar']['y_test'], nwp_solar, 100.0)

ml_metrics_wind = compute_metrics(data['wind']['y_test'], data['wind']['y_pred'], 50.0)
nwp_metrics_wind = compute_metrics(data['wind']['y_test'], nwp_wind, 50.0)

# Calculate improvements globally
mae_improvement_solar = ((nwp_metrics_solar['MAE'] - ml_metrics_solar['MAE']) / nwp_metrics_solar['MAE'] * 100) if nwp_metrics_solar['MAE'] > 0 else 0
rmse_improvement_solar = ((nwp_metrics_solar['RMSE'] - ml_metrics_solar['RMSE']) / nwp_metrics_solar['RMSE'] * 100) if nwp_metrics_solar['RMSE'] > 0 else 0
r2_improvement_solar = ((ml_metrics_solar['R²'] - nwp_metrics_solar['R²']) / abs(nwp_metrics_solar['R²']) * 100) if nwp_metrics_solar['R²'] != 0 else 0

mae_improvement_wind = ((nwp_metrics_wind['MAE'] - ml_metrics_wind['MAE']) / nwp_metrics_wind['MAE'] * 100) if nwp_metrics_wind['MAE'] > 0 else 0
rmse_improvement_wind = ((nwp_metrics_wind['RMSE'] - ml_metrics_wind['RMSE']) / nwp_metrics_wind['RMSE'] * 100) if nwp_metrics_wind['RMSE'] > 0 else 0
r2_improvement_wind = ((ml_metrics_wind['R²'] - nwp_metrics_wind['R²']) / abs(nwp_metrics_wind['R²']) * 100) if nwp_metrics_wind['R²'] != 0 else 0

# Calculate penalties for savings
penalties_solar = [compute_dsm_penalty(s, a, "solar") for s, a in zip(data['solar']['y_pred'], data['solar']['y_test'])]
df_pen_ml_solar = pd.DataFrame(penalties_solar)
penalties_nwp_solar = [compute_dsm_penalty(s, a, "solar") for s, a in zip(nwp_solar, data['solar']['y_test'])]
df_pen_nwp_solar = pd.DataFrame(penalties_nwp_solar)

ml_penalty_solar = df_pen_ml_solar['penalty_inr'].sum() * 365 / len(data['solar']['y_test'])
nwp_penalty_solar = df_pen_nwp_solar['penalty_inr'].sum() * 365 / len(data['solar']['y_test'])
savings = nwp_penalty_solar - ml_penalty_solar

penalties_wind = [compute_dsm_penalty(s, a, "wind") for s, a in zip(data['wind']['y_pred'], data['wind']['y_test'])]
df_pen_ml_wind = pd.DataFrame(penalties_wind)
penalties_nwp_wind = [compute_dsm_penalty(s, a, "wind") for s, a in zip(nwp_wind, data['wind']['y_test'])]
df_pen_nwp_wind = pd.DataFrame(penalties_nwp_wind)

ml_penalty_wind = df_pen_ml_wind['penalty_inr'].sum() * 365 / len(data['wind']['y_test'])
nwp_penalty_wind = df_pen_nwp_wind['penalty_inr'].sum() * 365 / len(data['wind']['y_test'])
savings_w = nwp_penalty_wind - ml_penalty_wind

def draw_kpi_card(col, title, ml_val, nwp_val, unit="", improvement_pct=None):
    """Draw a KPI card comparing ML vs NWP"""
    with col:
        st.markdown(f"**{title}**")
        col_ml, col_nwp = st.columns(2)
        with col_ml:
            st.metric("ML Model", f"{ml_val:.3f} {unit}")
        with col_nwp:
            st.metric("NWP Baseline", f"{nwp_val:.3f} {unit}")
        if improvement_pct:
            improvement_color = "🟢" if improvement_pct > 0 else "🔴"
            st.caption(f"{improvement_color} {improvement_pct:+.1f}% better")

# NAVIGATION
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Select view:", [
    "📊 Overview & KPIs",
    "☀️ Solar Forecast",
    "💨 Wind Forecast",
    "💰 DSM Penalty Impact",
    "🔍 Performance Details"
])

if page == "📊 Overview & KPIs":
    st.markdown("## Key Performance Indicators")

    # SOLAR KPIs
    st.markdown("### ☀️ Bhadla Solar (100 MW)")
    cols = st.columns(4)

    with cols[0]:
        st.markdown(metric_card("MAE (MW)", f"{ml_metrics_solar['MAE']:.3f}", f"{mae_improvement_solar:+.0f}% vs NWP"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(metric_card("RMSE (MW)", f"{ml_metrics_solar['RMSE']:.3f}", f"{rmse_improvement_solar:+.0f}% vs NWP"), unsafe_allow_html=True)
    with cols[2]:
        nrmse_improvement = (nwp_metrics_solar['NRMSE (%)'] - ml_metrics_solar['NRMSE (%)']) / nwp_metrics_solar['NRMSE (%)'] * 100
        st.markdown(metric_card("NRMSE (%)", f"{ml_metrics_solar['NRMSE (%)']:.2f}%", f"{nrmse_improvement:+.0f}% better"), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(metric_card("R² Score", f"{ml_metrics_solar['R²']:.4f}", f"{r2_improvement_solar:+.1f}% vs NWP"), unsafe_allow_html=True)

    # WIND KPIs
    st.markdown("### 💨 Muppandal Wind (50 MW)")
    cols = st.columns(4)

    with cols[0]:
        st.markdown(metric_card("MAE (MW)", f"{ml_metrics_wind['MAE']:.3f}", f"{mae_improvement_wind:+.0f}% vs NWP"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(metric_card("RMSE (MW)", f"{ml_metrics_wind['RMSE']:.3f}", f"{rmse_improvement_wind:+.0f}% vs NWP"), unsafe_allow_html=True)
    with cols[2]:
        nrmse_improvement_w = (nwp_metrics_wind['NRMSE (%)'] - ml_metrics_wind['NRMSE (%)']) / nwp_metrics_wind['NRMSE (%)'] * 100
        st.markdown(metric_card("NRMSE (%)", f"{ml_metrics_wind['NRMSE (%)']:.2f}%", f"{nrmse_improvement_w:+.0f}% better"), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(metric_card("R² Score", f"{ml_metrics_wind['R²']:.4f}", f"{r2_improvement_wind:+.1f}% vs NWP"), unsafe_allow_html=True)

elif page == "☀️ Solar Forecast":
    st.markdown("## 24-Hour Solar Generation Forecast (Bhadla)")

    end_idx = min(500, len(data['solar']['y_test']))
    x_range = np.arange(end_idx)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_range, y=data['solar']['y_test'][-end_idx:],
                             name='Actual (Ground Truth)', mode='lines',
                             line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=x_range, y=data['solar']['y_pred'][-end_idx:],
                             name='LightGBM Forecast', mode='lines',
                             line=dict(color='#2ca02c', width=2.5, dash='dash')))
    fig.add_trace(go.Scatter(x=x_range, y=nwp_solar[-end_idx:],
                             name='NWP Baseline', mode='lines',
                             line=dict(color='#ff7f0e', width=2, dash='dot')))

    fig.update_layout(
        title="Solar Generation: Actual vs ML Forecast vs NWP",
        xaxis_title="15-min Block",
        yaxis_title="Generation (MW)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Average Error (MAE)", f"{ml_metrics_solar['MAE']:.3f} MW",
              f"vs NWP: {nwp_metrics_solar['MAE']:.3f} MW")

elif page == "💨 Wind Forecast":
    st.markdown("## 24-Hour Wind Generation Forecast (Muppandal)")

    end_idx = min(500, len(data['wind']['y_test']))
    x_range = np.arange(end_idx)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_range, y=data['wind']['y_test'][-end_idx:],
                             name='Actual (Ground Truth)', mode='lines',
                             line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=x_range, y=data['wind']['y_pred'][-end_idx:],
                             name='LightGBM Forecast', mode='lines',
                             line=dict(color='#2ca02c', width=2.5, dash='dash')))
    fig.add_trace(go.Scatter(x=x_range, y=nwp_wind[-end_idx:],
                             name='NWP Baseline', mode='lines',
                             line=dict(color='#ff7f0e', width=2, dash='dot')))

    fig.update_layout(
        title="Wind Generation: Actual vs ML Forecast vs NWP",
        xaxis_title="15-min Block",
        yaxis_title="Generation (MW)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Average Error (MAE)", f"{ml_metrics_wind['MAE']:.3f} MW",
              f"vs NWP: {nwp_metrics_wind['MAE']:.3f} MW")

elif page == "💰 DSM Penalty Impact":
    st.markdown("## DSM Penalty Analysis (April 2027 CERC Regime)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("☀️ Solar (±5% tolerance)")
        st.markdown(metric_card("ML Annual Penalty", f"₹{ml_penalty_solar:,.0f}", f"vs NWP: ₹{nwp_penalty_solar:,.0f}"), unsafe_allow_html=True)
        st.markdown(metric_card("Potential Savings", f"₹{savings:,.0f}", f"{(savings/nwp_penalty_solar*100):.1f}% reduction", style="warning"), unsafe_allow_html=True)
        in_band_pct = (df_pen_ml_solar['within_band'].sum()/len(df_pen_ml_solar)*100)
        nwp_in_band = (df_pen_nwp_solar['within_band'].sum()/len(df_pen_nwp_solar)*100)
        st.markdown(metric_card("In-Band Blocks", f"{in_band_pct:.1f}%", f"vs NWP: {nwp_in_band:.1f}%"), unsafe_allow_html=True)

    with col2:
        st.subheader("💨 Wind (±10% tolerance)")
        st.markdown(
            metric_card(
                "ML Annual Penalty",
                f"₹{ml_penalty_wind:,.0f}",
                f"vs NWP: ₹{nwp_penalty_wind:,.0f}",
            ),
            unsafe_allow_html=True,
        )
        savings_pct_w = (
            f"{(savings_w/nwp_penalty_wind*100):.1f}% reduction"
            if nwp_penalty_wind > 0
            else "Minimal"
        )
        st.markdown(
            metric_card(
                "Potential Savings", f"₹{savings_w:,.0f}", savings_pct_w, style="warning"
            ),
            unsafe_allow_html=True,
        )
        in_band_pct_w = (
            df_pen_ml_wind["within_band"].sum() / len(df_pen_ml_wind) * 100
        )
        nwp_in_band_w = (
            df_pen_nwp_wind["within_band"].sum() / len(df_pen_nwp_wind) * 100
        )
        st.markdown(
            metric_card(
                "In-Band Blocks",
                f"{in_band_pct_w:.1f}%",
                f"vs NWP: {nwp_in_band_w:.1f}%",
            ),
            unsafe_allow_html=True,
        )

elif page == "🔍 Performance Details":
    st.markdown("## Detailed Performance Comparison")

    # Create comparison table
    comparison_data = {
        'Metric': ['MAE (MW)', 'RMSE (MW)', 'NRMSE (%)', 'R²'],
        'Solar (ML)': [
            f"{ml_metrics_solar['MAE']:.4f}",
            f"{ml_metrics_solar['RMSE']:.4f}",
            f"{ml_metrics_solar['NRMSE (%)']:.2f}%",
            f"{ml_metrics_solar['R²']:.4f}"
        ],
        'Solar (NWP)': [
            f"{nwp_metrics_solar['MAE']:.4f}",
            f"{nwp_metrics_solar['RMSE']:.4f}",
            f"{nwp_metrics_solar['NRMSE (%)']:.2f}%",
            f"{nwp_metrics_solar['R²']:.4f}"
        ],
        'Wind (ML)': [
            f"{ml_metrics_wind['MAE']:.4f}",
            f"{ml_metrics_wind['RMSE']:.4f}",
            f"{ml_metrics_wind['NRMSE (%)']:.2f}%",
            f"{ml_metrics_wind['R²']:.4f}"
        ],
        'Wind (NWP)': [
            f"{nwp_metrics_wind['MAE']:.4f}",
            f"{nwp_metrics_wind['RMSE']:.4f}",
            f"{nwp_metrics_wind['NRMSE (%)']:.2f}%",
            f"{nwp_metrics_wind['R²']:.4f}"
        ]
    }

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    st.markdown("### Summary")
    st.info(f"""
    **Bhadla Solar (100 MW):**
    - LightGBM MAE: {ml_metrics_solar['MAE']:.3f} MW ({ml_metrics_solar['NRMSE (%)']:.2f}% of capacity)
    - Improvement vs NWP: {mae_improvement_solar:.0f}% better error
    - Annual penalty savings: ₹{savings:,.0f}

    **Muppandal Wind (50 MW):**
    - LightGBM MAE: {ml_metrics_wind['MAE']:.3f} MW ({ml_metrics_wind['NRMSE (%)']:.2f}% of capacity)
    - Improvement vs NWP: {mae_improvement_wind:.0f}% better error
    - Annual penalty savings: ₹{savings_w:,.0f}
    """)
