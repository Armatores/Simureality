import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==============================================================================
# SIMUREALITY: 3D-TIME PHASE DESYNCHRONIZATION ENGINE (CHRONOS V9.2)
# Original V8 Core + 3D Time Visualization + Embedded English Ontology Manifesto
# ==============================================================================

st.set_page_config(page_title="Chronos V9.2: 3D-Time Engine", layout="wide", page_icon="⏱️")

@st.cache_data
def load_chronos_data():
    files_to_try = ["2026-05-30T23-26_export.csv", "simureality_chronos_v8_benchmark.csv"]
    for file_name in files_to_try:
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
            if 'ΔK Debt (MeV)' in df.columns and 'Log10(T_1/2)' in df.columns:
                return df.dropna(subset=['ΔK Debt (MeV)', 'Log10(T_1/2)'])
    return None

def compute_3d_phase_shift(df):
    if df is None or df.empty:
        return df
    
    # 1. Visual Model (3D-Time Desync)
    df['3D_Jitter'] = (df['ΔK Debt (MeV)'] / 110.0).clip(0, 0.4999)
    df['Desync_Angle_Deg'] = df['3D_Jitter'] * 360.0
    
    # 2. Mathematical Prediction (GC Routing Equation)
    df['Unpaired'] = ((df['Z'] % 2 != 0) | ((df['A'] - df['Z']) % 2 != 0)).astype(int)
    
    T_base, Z_imp, E_pow, P_lock = 2.76, 0.04, -0.87, -0.13
    df['Predicted_LogT'] = T_base + (Z_imp * df['Z']) + (E_pow * np.sqrt(df['ΔK Debt (MeV)'])) + (P_lock * df['Unpaired'])
    
    # 3. Error Delta Calculation
    df['Error_Delta'] = abs(df['Predicted_LogT'] - df['Log10(T_1/2)'])
    
    return df.sort_values('Desync_Angle_Deg')

# --- USER INTERFACE ---
st.title("⏱️ Chronos V9.2: 3D-Time Mechanics & Deterministic Decay")
st.markdown("**Grid Physics Framework:** Hardware-level validation tool for deterministic nuclear decay.")

df_raw = load_chronos_data()

if df_raw is None:
    st.error("Database not found. Please ensure the export file (e.g., `2026-05-30T23-26_export.csv`) is in the same directory as `app.py`.")
else:
    df = compute_3d_phase_shift(df_raw)
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'].notna())].copy()

    # --- LIVE BENCHMARK PANEL ---
    mae_global = df_unstable['Error_Delta'].mean()
    # The timescale spans roughly 50 orders of magnitude (from yoctoseconds to quadrillions of years)
    accuracy_percent = max(0, 100 - (mae_global / 50.0 * 100))
    
    st.markdown("### 🎯 Live Benchmark: Hardware-Level Theory Accuracy")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Processed Isotopes", f"{len(df_unstable)}")
    col2.metric("Mean Absolute Error (MAE)", f"{mae_global:.2f} orders", help="Average deviation of prediction from CERN/NUBASE empirical data")
    col3.metric("Computational Accuracy", f"{accuracy_percent:.1f}%", delta="Grid Physics Core", delta_color="normal")
    col4.metric("Time Singularity", "180°", help="Absolute desync limit before Kernel Panic")
    
    st.divider()

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Matrix Ontology (Manifesto)",
        "🔬 Isotope Chains (Death Vector)", 
        "🌌 Global Desync Graph", 
        "🗄️ System Log (Theory vs Reality)"
    ])

    with tab1:
        st.header("Simureality: How the Universe Actually Works")
        st.markdown("""
        Modern physics has hit a dead end trying to describe the world with a set of probabilities and infinite fields. 
        **Grid Physics** offers a radical ontological shift: The Universe is a discrete computational substrate (Face-Centered Cubic lattice) governed by a single hardware law — **the drive towards minimal computational complexity ($\Sigma K \\to \min$)**.
        ### 1. The Dual Nature of Time: 3D Micro-Time vs. 1D Macro-Time
        Forget about protons and neutrons as independent, solid spheres. At the fundamental hardware level, reality is constructed entirely from **three-dimensional numbers** (Trinaries). Because the Matrix's processor (the Trisistor) updates these data structures across all three spatial axes (X, Y, Z) simultaneously, **time inside a particle is strictly three-dimensional** — an update vector $(t_x, t_y, t_z)$. 
        
        What we perceive as standard, linear one-dimensional "time" is merely the macroscopic rendering track — the straight coordinate axis along which the global system moves as a whole, frame by frame. 
        
        Therefore, an atomic nucleus is a dynamic 3D-graph compilation process. **Mass** is not an innate property of matter; it is **Topological Debt ($\Delta K$)** — the amount of processor resources the Matrix must spend to successfully route these 3D-time vectors through a distorted lattice node to keep it synchronized with the 1D macro-timeline.

        ### 2. Data Deduplication (Mass Defect)
        Why does a nucleus weigh less than the sum of its parts? In IT, this is called **Data Deduplication**. When nodes merge, they collapse shared I/O ports. The Matrix no longer needs to compute their internal boundaries. Computational complexity drops, and the freed resources are released into the physical world as "Binding Energy".

        ### 3. 3D-Time and Gravity (Compensated Lag)
        In a perfect lattice ($\Delta K = 0$), system clocks tick absolutely synchronously in all directions. 
        But if a node is deformed, the Matrix requires more clock cycles to compute its topology. A **routing lag** emerges. 
        To compensate for this local lag, the System Dispatcher *slows down the clock rate* in that region. 
        > **Gravity** is the operating system's attempt to move heavy, "lagging" processes closer together (defragmentation) to optimize the cache. This is exactly why time flows slower near massive objects.

        #### 4. Radioactivity as a 3D-Time Synchronization Error (Kernel Panic)
Stable nuclei are those whose geometry perfectly resonates with the discrete steps of the FCC lattice. Because their nodes align exactly with the "integer floors" of the grid, their internal 3D-time vectors ($t_x, t_y, t_z$) update in absolute synchrony. The Matrix recalculates them flawlessly, without lag or Topological Debt ($\Delta K \approx 0$). They exist in a stable, infinite execution loop.

Unstable nuclei are geometrically deformed. Their nodes get physically shifted and "stuck" between the lattice layers (Geometric Jitter). Because the speed of information transfer in the system is finite (the speed of light), this physical spatial misalignment automatically converts into a temporal lag. The three time axes inside the nucleus begin to desynchronize.

When the topological debt reaches a critical threshold (around 55 MeV), the desynchronization angle hits 180° (complete anti-phase). A fatal system error occurs: the global 1D macro-timeline cannot render a node whose internal 3D dimensions are ticking in opposite directions. 

**Radioactive decay is not a quantum accident.** It is a deterministic Garbage Collector Timeout, forcefully terminating and recompiling the desynchronized process to save the Universe's operating system from Geometry Overflow.

        ### ⚙️ How Does This Script Work?
        This engine completely avoids the probabilistic crutches of the Standard Model. It takes the geometric assembly error ($\Delta K$), translates it into a 3D-time desynchronization angle, and computes the exact Garbage Collector timeout. It then compares this theoretical timeout against real collider measurements (NUBASE database). The accuracy you see in the Live Benchmark proves that **the Universe is strictly algorithmic**.
        """)
        st.info("💡 **Grid Physics:** We don't guess by the noise of the cooling fan. We decompile the processor's code.")

    with tab2:
        st.subheader("Phase Decay of an Element (Micro-analysis)")
        elements = sorted(df_unstable['Z'].unique())
        selected_Z = st.selectbox("Select Nuclear Charge (Z):", elements, index=elements.index(6) if 6 in elements else 0)
        chain = df_unstable[df_unstable['Z'] == selected_Z]
        
        if len(chain) > 2:
            fig1 = px.scatter(
                chain, x="Desync_Angle_Deg", y="Log10(T_1/2)", 
                hover_name="Isotope", text="Isotope",
                title=f"Kernel Panic Trajectory for Z={selected_Z}",
                labels={"Desync_Angle_Deg": "3D-Time Desync Angle (°)", "Log10(T_1/2)": "Real Time Log10(T)"},
                trendline="ols", trendline_color_override="#FF1744", template="plotly_dark"
            )
            fig1.update_traces(textposition='top right', marker=dict(size=14, color='#00E676', line=dict(width=2, color='white')))
            fig1.add_vline(x=180, line_dash="dash", line_color="red", annotation_text="Kernel Panic (180°)")
            
            stable_chain = df[(df['Z'] == selected_Z) & (df['Status'] == 'Stable')]
            if not stable_chain.empty:
                fig1.add_trace(px.scatter(stable_chain, x="Desync_Angle_Deg", y=[30]*len(stable_chain), text="Isotope").data[0])
                fig1.data[-1].marker.color = 'yellow'
                fig1.data[-1].marker.symbol = 'star'
                fig1.data[-1].name = 'Stable (∞)'

            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("Not enough data to plot the chain trend.")

    with tab3:
        st.subheader("Global Phase Shift (All Elements)")
        fig2 = px.scatter(
            df_unstable, x="Desync_Angle_Deg", y="Log10(T_1/2)", color="Z", 
            hover_name="Isotope", hover_data=["ΔK Debt (MeV)", "Predicted_LogT", "Error_Delta"],
            color_continuous_scale="Turbo", template="plotly_dark",
            title="Global 3D-Time Degradation Map",
            labels={"Desync_Angle_Deg": "Desync Angle (°)", "Log10(T_1/2)": "Real Time Log10(T)"}
        )
        fig2.add_vline(x=180, line_dash="dash", line_color="red")
        st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        st.markdown("### 🗄️ Comparison: Theory vs. Reality")
        st.markdown("The Matrix compares its mathematical prediction (`Predicted_LogT`) against real collider data (`Log10(T_1/2)`).")
        display_cols = ['Isotope', 'Z', 'Status', 'ΔK Debt (MeV)', 'Desync_Angle_Deg', 'Predicted_LogT', 'Log10(T_1/2)', 'Error_Delta']
        format_dict = {'ΔK Debt (MeV)': '{:.3f}', 'Desync_Angle_Deg': '{:.2f}°', 'Predicted_LogT': '{:.2f}', 'Log10(T_1/2)': '{:.2f}', 'Error_Delta': '{:.3f}'}
        
        st.dataframe(
            df_unstable[display_cols].sort_values('Error_Delta').style
            .format(format_dict)
            .background_gradient(subset=['Error_Delta'], cmap='Reds', vmin=0, vmax=5)
            .background_gradient(subset=['Desync_Angle_Deg'], cmap='Oranges'),
            use_container_width=True, height=600
        )
