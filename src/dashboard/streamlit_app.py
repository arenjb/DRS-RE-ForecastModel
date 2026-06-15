import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(
    page_title="RE Forecasting Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    :root {
        --primary: #1f77b4;
        --teal: #17a2b8;
        --amber: #ffc107;
        --green: #28a745;
        --danger: #dc3545;
        --text-primary: #1a1a1a;
        --text-secondary: #666;
        --bg: #f8f9fa;
        --border: #dee2e6;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Header styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        margin-bottom: 24px;
    }

    .header-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 4px;
    }

    /* Tab styling */
    .tab-container {
        display: flex;
        gap: 8px;
        margin-bottom: 24px;
        border-bottom: 2px solid #dee2e6;
    }

    .tab-btn {
        padding: 12px 20px;
        border: none;
        background: transparent;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.3s;
    }

    .tab-btn.active {
        border-bottom-color: #667eea;
        color: #667eea;
    }

    /* Card styling */
    .metric-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .card-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 16px;
        color: #1a1a1a;
    }

    .card-subtitle {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    /* Hero card */
    .hero-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .hero-label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    .hero-value {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-value.teal {color: #17a2b8;}
    .hero-value.green {color: #28a745;}
    .hero-value.amber {color: #ffc107; color: #ff9800;}

    .hero-sub {
        font-size: 12px;
        color: #666;
        line-height: 1.5;
    }

    /* Metric table */
    .metrics-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .metrics-table th {
        background: #f8f9fa;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #dee2e6;
    }

    .metrics-table td {
        padding: 12px;
        border-bottom: 1px solid #dee2e6;
    }

    .metrics-table .highlight {
        font-weight: 700;
        color: #667eea;
    }

    /* Progress bar */
    .progress-bar {
        background: #e9ecef;
        border-radius: 4px;
        height: 24px;
        overflow: hidden;
        margin-top: 8px;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 8px;
        color: white;
        font-size: 11px;
        font-weight: 600;
    }

    /* Input styling */
    .calc-input {
        margin-bottom: 16px;
    }

    .calc-input label {
        display: block;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 6px;
        color: #1a1a1a;
    }

    .calc-input input {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent.parent.parent / "dashboard_data.json"
    with open(data_path) as f:
        return json.load(f)

data = load_data()

# Session state for site & tab
if 'site' not in st.session_state:
    st.session_state.site = 'solar'
if 'tab' not in st.session_state:
    st.session_state.tab = 0

# Header with site toggle
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("### Deliverain **Forecast**")
    st.markdown("*RE Generation Forecasting Engine*", help="")
with col3:
    if st.button("☀️ Solar" if st.session_state.site != 'solar' else "☀️ Solar (Active)", key="btn_solar", use_container_width=True):
        st.session_state.site = 'solar'
        st.rerun()
    if st.button("⚡ Wind" if st.session_state.site != 'wind' else "⚡ Wind (Active)", key="btn_wind", use_container_width=True):
        st.session_state.site = 'wind'
        st.rerun()

st.divider()

# Get current data
site = st.session_state.site
site_data = data[site]
site_name = "Bhadla, Rajasthan (100 MW Solar)" if site == 'solar' else "Muppandal, Tamil Nadu (50 MW Wind)"
ml = site_data['ml']
nwp = site_data['nwp']

# Tabs
tabs = ["Business Impact", "Forecast Performance", "DSM Savings Calculator", "Technical Insights"]
cols = st.columns(len(tabs))

for i, col in enumerate(cols):
    with col:
        if st.button(tabs[i], key=f"tab_{i}", use_container_width=True):
            st.session_state.tab = i

st.divider()

# ============================================================
# TAB 0: BUSINESS IMPACT
# ============================================================
if st.session_state.tab == 0:
    st.subheader("Business Impact Analysis")

    # Hero cards
    col1, col2, col3, col4 = st.columns(4)

    # Calculate metrics for display
    savings_lakhs = (nwp['annual_penalty_inr'] - ml['annual_penalty_inr']) / 100000
    ml_pct = int(ml['inband_pct'])
    nwp_pct = int(nwp['inband_pct'])
    improvement_pp = ml_pct - nwp_pct
    mae_reduction = int((1 - ml['mae'] / nwp['mae']) * 100)
    outband_ml = 96 - (ml['inband_pct'] / 100 * 96)
    outband_nwp = 96 - (nwp['inband_pct'] / 100 * 96)
    out_reduction = int((outband_nwp - outband_ml) / outband_nwp * 100) if outband_nwp > 0 else 0

    with col1:
        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 24px; text-align: center;'>
            <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Annual DSM Savings</div>
            <div style='font-size: 28px; font-weight: 800; color: #17a2b8; margin-bottom: 8px;'>₹{savings_lakhs:.1f}L</div>
            <div style='font-size: 12px; color: #666; line-height: 1.5;'>For a {site_data['capacity_mw']} MW {site.capitalize()} Plant</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 24px; text-align: center;'>
            <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Compliance Improvement</div>
            <div style='font-size: 28px; font-weight: 800; color: #17a2b8; margin-bottom: 8px;'>+{improvement_pp}pp</div>
            <div style='font-size: 12px; color: #666; line-height: 1.5;'>Blocks within tolerance band</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 24px; text-align: center;'>
            <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Forecast Accuracy</div>
            <div style='font-size: 28px; font-weight: 800; color: #28a745; margin-bottom: 8px;'>{mae_reduction}%</div>
            <div style='font-size: 12px; color: #666; line-height: 1.5;'>Reduction in MAE (MW)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 24px; text-align: center;'>
            <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Risk Reduction</div>
            <div style='font-size: 28px; font-weight: 800; color: #28a745; margin-bottom: 8px;'>{out_reduction}%</div>
            <div style='font-size: 12px; color: #666; line-height: 1.5;'>Fewer out-of-band blocks</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Compliance bars
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Band Compliance Before vs After")
        st.markdown(f"""
        <div style='margin-bottom: 16px;'>
            <div style='display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 6px;'>
                <span style='color: #17a2b8;'>ML Model</span>
                <span style='color: #17a2b8;'>{ml_pct}%</span>
            </div>
            <div style='background: #e9ecef; border-radius: 4px; height: 20px;'>
                <div style='background: linear-gradient(90deg, #17a2b8, #0b7593); width: {ml_pct}%; height: 100%; border-radius: 4px;'></div>
            </div>
        </div>
        <div>
            <div style='display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 6px;'>
                <span style='color: #ffc107;'>NWP Baseline</span>
                <span style='color: #ffc107;'>{nwp_pct}%</span>
            </div>
            <div style='background: #e9ecef; border-radius: 4px; height: 20px;'>
                <div style='background: linear-gradient(90deg, #ffc107, #ff9800); width: {nwp_pct}%; height: 100%; border-radius: 4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Forecast Error Reduction")
        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px;'>
            <div style='display: flex; align-items: center; justify-content: space-around;'>
                <div style='text-align: center;'>
                    <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;'>NWP Baseline</div>
                    <div style='font-size: 32px; font-weight: 800; color: #ff9800;'>{nwp['mae']:.1f}</div>
                    <div style='font-size: 12px; color: #666;'>MW MAE</div>
                </div>
                <div style='font-size: 24px; color: #ccc;'>→</div>
                <div style='text-align: center;'>
                    <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;'>ML Model</div>
                    <div style='font-size: 32px; font-weight: 800; color: #17a2b8;'>{ml['mae']:.2f}</div>
                    <div style='font-size: 12px; color: #666;'>MW MAE</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Time series chart
    st.markdown("#### Forecast vs Actual — " + site_name)

    fig = go.Figure()

    # Add traces for deviations
    num_days = min(30, len(ml['daily_inband']))
    for day in range(num_days):
        within_ml = ml['daily_inband'][day] >= 95
        within_nwp = nwp['daily_inband'][day] >= 95

        fig.add_vline(
            x=day,
            line_dash="dot",
            line_color="rgba(0,0,0,0.1)",
            annotation_text="" if day % 5 != 0 else f"Day {day+1}",
            annotation_position="top"
        )

    fig.add_trace(go.Scatter(
        y=ml['daily_inband'][:num_days],
        name="ML Model",
        line=dict(color="#17a2b8", width=2),
        mode="lines+markers"
    ))

    fig.add_trace(go.Scatter(
        y=nwp['daily_inband'][:num_days],
        name="NWP Baseline",
        line=dict(color="#ff9800", width=2),
        mode="lines+markers"
    ))

    fig.update_layout(
        height=400,
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Technical metrics
    st.markdown("#### Technical Metrics")
    st.markdown(f"""
    <table style='width: 100%; border-collapse: collapse; font-size: 13px;'>
        <tr style='background: #f8f9fa;'>
            <th style='padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>Metric</th>
            <th style='padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>ML Model</th>
            <th style='padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>NWP</th>
        </tr>
        <tr style='border-bottom: 1px solid #dee2e6;'>
            <td style='padding: 12px;'>MAE</td>
            <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['mae']:.3f} MW</td>
            <td style='padding: 12px;'>{nwp['mae']:.3f} MW</td>
        </tr>
        <tr style='border-bottom: 1px solid #dee2e6;'>
            <td style='padding: 12px;'>RMSE</td>
            <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['rmse']:.3f} MW</td>
            <td style='padding: 12px;'>{nwp['rmse']:.3f} MW</td>
        </tr>
        <tr style='border-bottom: 1px solid #dee2e6;'>
            <td style='padding: 12px;'>nRMSE</td>
            <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['nrmse']:.2f}%</td>
            <td style='padding: 12px;'>{nwp['nrmse']:.2f}%</td>
        </tr>
        <tr style='border-bottom: 1px solid #dee2e6;'>
            <td style='padding: 12px;'>R²</td>
            <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['r2']:.3f}</td>
            <td style='padding: 12px;'>{nwp['r2']:.3f}</td>
        </tr>
        <tr>
            <td style='padding: 12px;'>Band Compliance</td>
            <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml_pct}%</td>
            <td style='padding: 12px;'>{nwp_pct}%</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

# ============================================================
# TAB 1: FORECAST PERFORMANCE (Deviation Analysis)
# ============================================================
elif st.session_state.tab == 1:
    st.subheader("Deviation Analysis")
    st.markdown(f"Distribution of deviation % across all 15-minute test blocks (90-day backtest)")

    # Stats
    ml_mean_dev = np.mean([d for d in ml['deviations'] if d > 0]) if any(ml['deviations']) else 0
    nwp_mean_dev = np.mean([d for d in nwp['deviations'] if d > 0]) if any(nwp['deviations']) else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("ML Mean Deviation", f"{ml_mean_dev:.2f}%")
    col2.metric("NWP Mean Deviation", f"{nwp_mean_dev:.2f}%")
    col3.metric("Improvement", f"{nwp_mean_dev - ml_mean_dev:.2f}pp")

    # Histogram
    st.markdown("#### Deviation Histogram — ML vs NWP")

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=ml['deviations'],
        name="ML Model",
        nbinsx=50,
        opacity=0.7,
        marker_color="#17a2b8"
    ))
    fig.add_trace(go.Histogram(
        x=nwp['deviations'],
        name="NWP Baseline",
        nbinsx=50,
        opacity=0.7,
        marker_color="#ff9800"
    ))

    fig.update_layout(
        height=400,
        barmode="overlay",
        hovermode="x",
        xaxis_title="Deviation %",
        yaxis_title="Frequency",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Daily compliance timeline
    st.markdown("#### Daily Band Compliance Over Time")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=ml['daily_inband'],
        name="ML Model",
        line=dict(color="#17a2b8", width=2),
        mode="lines+markers"
    ))
    fig.add_trace(go.Scatter(
        y=nwp['daily_inband'],
        name="NWP Baseline",
        line=dict(color="#ff9800", width=2),
        mode="lines+markers"
    ))
    fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")

    fig.update_layout(
        height=400,
        hovermode="x unified",
        xaxis_title="Day",
        yaxis_title="In-Band %",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 2: DSM PENALTY CALCULATOR
# ============================================================
elif st.session_state.tab == 2:
    st.subheader("DSM Penalty Impact Calculator")
    st.markdown("Estimate annual DSM charges under April 2027 CERC regime")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Site Parameters")
        capacity = st.number_input("Installed Capacity (MW)", value=site_data['capacity_mw'], min_value=1, max_value=5000)
        cuf = st.number_input("Capacity Utilization Factor (%)", value=25, min_value=5, max_value=60)
        tariff = st.number_input("PPA Tariff (₹/kWh)", value=2.50, min_value=0.5, max_value=10.0, step=0.1)
        penalty_rate = st.number_input("DSM Penalty Rate (₹/kWh deviation)", value=1.0, min_value=0.1, max_value=5.0, step=0.1)

    with col2:
        st.markdown("#### Annual Impact Comparison")

        # Calculate penalties
        annual_gen_kwh = capacity * 1000 * 24 * 365 * (cuf / 100)
        ml_annual_pen = ml['annual_penalty_inr']
        nwp_annual_pen = nwp['annual_penalty_inr']
        savings = nwp_annual_pen - ml_annual_pen

        st.markdown(f"""
        <div style='background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px;'>
            <div style='margin-bottom: 16px;'>
                <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em;'>ML Model Annual Penalty</div>
                <div style='font-size: 24px; font-weight: 800; color: #17a2b8;'>₹{ml_annual_pen:,.0f}</div>
            </div>
            <div style='margin-bottom: 16px;'>
                <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em;'>NWP Annual Penalty</div>
                <div style='font-size: 24px; font-weight: 800; color: #ff9800;'>₹{nwp_annual_pen:,.0f}</div>
            </div>
            <div style='border-top: 1px solid #dee2e6; padding-top: 16px;'>
                <div style='font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.1em;'>Annual Savings</div>
                <div style='font-size: 28px; font-weight: 800; color: #28a745;'>₹{savings:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Penalty breakdown by deviation band
    st.markdown("#### Penalty by Deviation Band — Annual Breakdown")

    fig = go.Figure()

    bands = ["0-5%", "5-10%", "10-15%", ">15%"]
    ml_counts = [
        len([d for d in ml['deviations'] if 0 <= d <= 5]),
        len([d for d in ml['deviations'] if 5 < d <= 10]),
        len([d for d in ml['deviations'] if 10 < d <= 15]),
        len([d for d in ml['deviations'] if d > 15])
    ]
    nwp_counts = [
        len([d for d in nwp['deviations'] if 0 <= d <= 5]),
        len([d for d in nwp['deviations'] if 5 < d <= 10]),
        len([d for d in nwp['deviations'] if 10 < d <= 15]),
        len([d for d in nwp['deviations'] if d > 15])
    ]

    fig.add_trace(go.Bar(name="ML Model", x=bands, y=ml_counts, marker_color="#17a2b8"))
    fig.add_trace(go.Bar(name="NWP Baseline", x=bands, y=nwp_counts, marker_color="#ff9800"))

    fig.update_layout(
        height=400,
        barmode="group",
        xaxis_title="Deviation Band",
        yaxis_title="Blocks",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 3: TECHNICAL INSIGHTS
# ============================================================
elif st.session_state.tab == 3:
    st.subheader("Technical Insights")
    st.markdown(f"Model performance diagnostics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Model Performance Summary")
        st.markdown(f"""
        <table style='width: 100%; border-collapse: collapse; font-size: 13px;'>
            <tr style='background: #f8f9fa;'>
                <th style='padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>Metric</th>
                <th style='padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>Value</th>
            </tr>
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 12px;'>MAE</td>
                <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['mae']:.3f} MW</td>
            </tr>
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 12px;'>RMSE</td>
                <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['rmse']:.3f} MW</td>
            </tr>
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 12px;'>nRMSE</td>
                <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['nrmse']:.2f}%</td>
            </tr>
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 12px;'>R²</td>
                <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{ml['r2']:.4f}</td>
            </tr>
            <tr>
                <td style='padding: 12px;'>In-band %</td>
                <td style='padding: 12px; font-weight: 700; color: #17a2b8;'>{int(ml['inband_pct'])}%</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Hourly Error Distribution")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(24)),
            y=ml['hourly_errors'],
            name="ML Model",
            marker_color="#17a2b8"
        ))
        fig.add_trace(go.Bar(
            x=list(range(24)),
            y=nwp['hourly_errors'],
            name="NWP Baseline",
            marker_color="#ff9800",
            opacity=0.7
        ))

        fig.update_layout(
            height=350,
            barmode="group",
            xaxis_title="Hour of Day",
            yaxis_title="MAE (MW)",
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode="x"
        )
        st.plotly_chart(fig, use_container_width=True)
