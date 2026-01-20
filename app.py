import subprocess
import sys
import os

try:
    import pandas
    import plotly
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "plotly"])

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UIDAI Advanced Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-top: 5px solid #003366; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    files = [
        'api_data_aadhar_biometric_0_500000.csv', 
        'api_data_aadhar_biometric_500000_1000000.csv', 
        'api_data_aadhar_biometric_1000000_1500000.csv', 
        'api_data_aadhar_biometric_1500000_1861108.csv'
    ]
    df = pd.concat([pd.read_csv(f) for f in files])
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['total_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
    df['day_name'] = df['date'].dt.day_name()
    return df

df = load_data()

st.sidebar.image("https://uidai.gov.in/images/logo/aadhaar_english_logo.svg", width=140)
st.sidebar.title("Command Center")
state_filter = st.sidebar.selectbox("Select Region", ["All India"] + sorted(df['state'].unique().tolist()))

working_df = df if state_filter == "All India" else df[df['state'] == state_filter]

st.title("🛡️ Aadhaar National Biometric Command Center")
st.markdown(f"**Advanced Analytics Report for:** {state_filter}")

t1, t2, t3, t4 = st.tabs(["📋 Executive Summary", "📈 Trend Analysis", "🏗️ Operational Efficiency", "🎯 Strategic Targets"])

with t1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Updates", f"{working_df['total_updates'].sum():,.0f}")
    m2.metric("MBU (5-17)", f"{working_df['bio_age_5_17'].sum():,.0f}")
    m3.metric("Adult Updates", f"{working_df['bio_age_17_'].sum():,.0f}")
    m4.metric("Active Pincodes", f"{working_df['pincode'].nunique():,}")
    
    st.subheader("Chart 1: Regional Contribution Hierarchy")
    fig1 = px.treemap(working_df.groupby(['state', 'district'])['total_updates'].sum().reset_index(), 
                      path=['state', 'district'], values='total_updates', color='total_updates', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Chart 2: National Demographic Distribution")
    fig2 = px.pie(values=[working_df['bio_age_5_17'].sum(), working_df['bio_age_17_'].sum()], 
                  names=['Minors', 'Adults'], hole=0.4, color_discrete_sequence=['#ff9999','#66b3ff'])
    st.plotly_chart(fig2, use_container_width=True)

with t2:
    st.subheader("Chart 3: Temporal Load (Weekly Patterns)")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_data = working_df.groupby('day_name')['total_updates'].sum().reindex(day_order).reset_index()
    fig3 = px.bar(day_data, x='day_name', y='total_updates', color='total_updates', color_continuous_scale='GnBu')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Chart 4: Daily Transaction Velocity")
    daily = working_df.groupby('date')['total_updates'].sum().reset_index()
    fig4 = px.area(daily, x='date', y='total_updates', color_discrete_sequence=['#003366'])
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Chart 5: Demographic Smoothing (7-Day Moving Average)")
    ts = working_df.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum().reset_index()
    ts['Minor (7D MA)'] = ts['bio_age_5_17'].rolling(7).mean()
    ts['Adult (7D MA)'] = ts['bio_age_17_'].rolling(7).mean()
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=ts['date'], y=ts['Minor (7D MA)'], name="Minor Trend", line=dict(color='orange', width=3)))
    fig5.add_trace(go.Scatter(x=ts['date'], y=ts['Adult (7D MA)'], name="Adult Trend", line=dict(color='green', width=3)))
    st.plotly_chart(fig5, use_container_width=True)

with t3:
    st.subheader("Chart 6: Infrastructure Efficiency (Density vs. Volume)")
    eff = working_df.groupby('district').agg({'total_updates':'sum', 'pincode':'nunique'}).reset_index()
    eff['Efficiency'] = (eff['total_updates'] / eff['pincode']).round(0)
    fig6 = px.scatter(eff, x='pincode', y='total_updates', size='Efficiency', color='Efficiency', hover_name='district', color_continuous_scale='Viridis')
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Chart 7: State vs. Weekday Intensity Heatmap")
    top10 = working_df.groupby('state')['total_updates'].sum().nlargest(10).index
    h = working_df[working_df['state'].isin(top10)].pivot_table(index='state', columns='day_name', values='total_updates', aggfunc='sum')
    h = h.reindex(columns=day_order)
    fig7 = px.imshow(h, text_auto=True, color_continuous_scale='YlGnBu')
    st.plotly_chart(fig7, use_container_width=True)

with t4:
    st.subheader("Chart 8: Priority Districts for MBU Deployment")
    mbu = working_df.groupby('district').agg({'bio_age_5_17':'sum', 'total_updates':'sum'}).reset_index()
    mbu['perc'] = (mbu['bio_age_5_17'] / mbu['total_updates'] * 100).round(1)
    fig8 = px.bar(mbu.nsmallest(15, 'perc'), x='perc', y='district', color='perc', color_continuous_scale='Reds', orientation='h')
    fig8.add_vline(x=49.1, line_dash="dash", line_color="blue", annotation_text="National Avg")
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align: center;'>UIDAI Hackathon 2026 | Proprietary Data-Driven Governance Suite</p>", unsafe_allow_html=True)
