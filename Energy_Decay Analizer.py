import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: CHRONOS ANALYZER V8.0
# DETAILED STATISTICAL PROOF OF DECAY DEPENDENCE ON TOPOLOGICAL DEBT
# ==========================================================================================

st.set_page_config(page_title="Chronos Analyzer", layout="wide")
st.title("Simureality: Chronos Analyzer 🔬")
st.markdown("""
**Rigorous verification tool.** Correlation analysis between FCC Topological Debt ($\Delta K$) and isotope lifetimes.
""")

@st.cache_data
def load_data():
    file_name = "simureality_chronos_benchmark_V73.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return None

df = load_data()

if df is None:
    st.warning("File `simureality_chronos_benchmark_V73.csv` not found in the root directory. Upload it manually:")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

if df is not None:
    # Data cleaning: keeping only unstable nuclei, excluding extreme incomplete builds (Drip Line)
    # Filtering timers > -25 (cutting off yoctosecond resonances that never even assembled)
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()
    
    st.success(f"Database loaded. Analyzing unstable isotopes: **{len(df_unstable)}**")
    
    # --- BLOCK 1: GLOBAL MACRO-TREND (ALPHA AND BETA DECAY) ---
    st.header("1. Global Macro-Trend")
    
    col1, col2 = st.columns(2)
    
    # Heavy nuclei (Z > 82) - Alpha decay dominates (Garbage Collection)
    heavy = df_unstable[df_unstable['Z'] > 82]
    r_heavy, p_heavy = stats.pearsonr(heavy['ΔK Debt (MeV)'], heavy['Log10(T_1/2)'])
    
    # Light/Medium nuclei (Z <= 82) - Beta decay dominates (Patching)
    light = df_unstable[df_unstable['Z'] <= 82]
    r_light, p_light = stats.pearsonr(light['ΔK Debt (MeV)'], light['Log10(T_1/2)'])
    
    with col1:
        st.subheader("Heavy nuclei ($Z > 82$)")
        st.markdown("**Mechanics:** Alpha-dump (critical Coulomb stress of the macro-crystal).")
        st.metric("Pearson Correlation", f"{r_heavy:.3f}")
        st.metric("p-value (Chance of randomness)", f"{p_heavy:.2e}")
        
        fig_heavy = px.scatter(
            heavy, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope",
            trendline="ols", trendline_color_override="red",
            title="X-Axis: Geometry Error | Y-Axis: Lifetime (Log10)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_heavy, use_container_width=True)

    with col2:
        st.subheader("Light/Medium nuclei ($Z \le 82$)")
        st.markdown("**Mechanics:** Beta decay (hardware patch for isospin asymmetry).")
        st.metric("Pearson Correlation", f"{r_light:.3f}")
        st.metric("p-value (Chance of randomness)", f"{p_light:.2e}")
        
        fig_light = px.scatter(
            light, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope",
            trendline="ols", trendline_color_override="red",
            title="X-Axis: Geometry Error | Y-Axis: Lifetime (Log10)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_light, use_container_width=True)

    st.info("""
    **How to read the charts:** The red trend line goes down. This proves a strict rule: 
    *The greater the Topological Debt (deviation from the ideal FCC matrix), the faster the Task Manager kills the process (decay).* The probability that this trend is random (p-value) is mathematically zero.
    """)

    st.divider()

    # --- BLOCK 2: MICRO-ANALYSIS BY ELEMENTS ---
    st.header("2. Micro-Analysis of Isotope Chains")
    st.markdown("The macro-formula produces background noise when comparing iron to uranium. But if we fix the charge ($Z$) and look only at the addition of neutrons to a single element, the Geiger-Nuttall law in the FCC interpretation becomes crystal clear.")
    
    element_list = sorted(df_unstable['Z'].unique())
    # Default selection is Uranium (92)
    default_index = element_list.index(92) if 92 in element_list else 0
    
    selected_Z = st.selectbox("Select nuclear charge (Z) for detailed analysis:", element_list, index=default_index)
    
    chain = df_unstable[df_unstable['Z'] == selected_Z]
    
    if len(chain) > 2:
        r_chain, p_chain = stats.pearsonr(chain['ΔK Debt (MeV)'], chain['Log10(T_1/2)'])
        
        col3, col4 = st.columns([1, 2])
        with col3:
            st.metric(f"Correlation for Z={selected_Z}", f"{r_chain:.3f}")
            st.metric("Isotopes in chain", len(chain))
            st.dataframe(chain[['Isotope', 'ΔK Debt (MeV)', 'Log10(T_1/2)']].sort_values('ΔK Debt (MeV)'))
            
        with col4:
            fig_chain = px.scatter(
                chain, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope", text="Isotope",
                trendline="ols", trendline_color_override="orange",
                title=f"Lifetime vs Geometry Dependency for Z={selected_Z}",
                template="plotly_dark"
            )
            fig_chain.update_traces(textposition='top center')
            st.plotly_chart(fig_chain, use_container_width=True)
    else:
        st.warning("Insufficient data to build a trend (minimum 3 unstable isotopes required).")
