import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# ==========================================
# 🧠 CORE LOGIC: SIGNAL INTEGRITY V5.0
# ==========================================

def calculate_geometry_quality(V_cell, V_coh):
    """
    Returns a 'Quality Factor' (0.0 to 1.0).
    1.0 = Perfect Geometric Resonance (Integer/Prime).
    0.0 = Total Mismatch (0.5 deviation).
    """
    N = V_coh / V_cell
    nearest = round(N)
    dist = abs(N - nearest) # 0 to 0.5
    
    # Base Quality: 1.0 is perfect, 0.5 dist is worst
    quality = 1.0 - (dist * 2.0) # Linear degradation
    
    # Prime Bonus: If we are near a prime, quality is boosted
    # Primes act as "Signal Anchors"
    is_prime = False
    if nearest > 2 and nearest % 2 != 0: # Simple heuristic check for speed
        is_prime = True
        for i in range(3, int(math.sqrt(nearest)) + 1, 2):
            if nearest % i == 0:
                is_prime = False
                break
    
    if is_prime:
        quality = min(1.0, quality + 0.15) # Prime Boost
        
    return quality

def run_simulation(row, pressure, tuning_factor):
    temps = np.arange(0, 300, 0.5)
    
    # --- 1. SIGNAL STRENGTH (The Capacity to hold Coherence) ---
    # Depends on Mass (Inertia) and Debye Temp (Lattice Stiffness).
    # Heavy + Stiff = Strong Signal.
    # Base Formula: sqrt(Mass) * log(Debye)
    # We normalize this to be in the range of 10-100 roughly.
    signal_baseline = math.sqrt(row["Mass_AMU"]) * np.log(row["Debye_T"]) * 0.8
    
    # 2D Boost: Layered materials have 'Protected' signal channels
    is_2d = "Layered" in row["Type"] or row["Lattice_C"] > 10
    if is_2d:
        signal_baseline *= 2.5 # Huge boost for topological protection
        
    signal_curve = [signal_baseline for _ in temps]

    # --- 2. NOISE LEVEL (The Entropy Attack) ---
    noise_curve = []
    
    # Effective Alpha (Pressure kills expansion)
    alpha_real = row["Alpha"] * np.exp(-pressure / 50.0)
    
    # Initial Geometry
    dim = 2 if is_2d else 3
    V_cell_0 = row["Lattice_A"]**2 * (1.0 if is_2d else row["Lattice_C"])
    V_coh_0 = (4/3)*np.pi*(row["Xi"]*10)**3
    if is_2d: V_coh_0 = np.pi*(row["Xi"]*10)**2

    for T in temps:
        # A. Thermal Noise (Base Entropy)
        # Linear growth with T
        thermal_noise = T * 0.1
        
        # B. Geometric Noise (The Multiplier)
        # Expansion ruins the resonance quality
        expansion = (1 + alpha_real * 1e-6 * T)
        V_cell_T = V_cell_0 * (expansion ** dim)
        
        quality = calculate_geometry_quality(V_cell_T, V_coh_0)
        
        # Geometric Noise Factor:
        # If Quality is 1.0 (Perfect), geometric_multiplier is 1.0 (No extra noise).
        # If Quality is 0.0 (Bad), geometric_multiplier is High.
        geo_noise_factor = 1.0 + (1.0 - quality) * 5.0 # Max 6x noise at bad geometry
        
        # C. Total Noise
        # Noise = Thermal * Geometric_Multiplier * Global_Tuning
        total_noise = thermal_noise * geo_noise_factor * tuning_factor
        
        noise_curve.append(total_noise)

    return temps, signal_curve, noise_curve

# ==========================================
# 🎛️ UI
# ==========================================
st.set_page_config(page_title="Simureality v5.0: Signal Integrity", layout="wide")
st.title("⚡ Simureality v5.0: The Signal Integrity Model")
st.markdown("**Philosophy:** Superconductivity persists as long as **Signal Strength (Mass/Inertia)** > **Noise (Entropy/Geometry)**.")

# DATABASE
data = {
    "Material": ["Aluminum (Al)", "Tin (Sn)", "Lead (Pb)", "Mercury (Hg)", "Niobium (Nb)", "MgB2", "YBCO", "BSCCO", "H3S"],
    "Type": ["Type I", "Type I", "Type I", "Type I", "Type II", "Type II", "Layered", "Layered", "Hydride"],
    "Tc_Real": [1.2, 3.7, 7.2, 4.2, 9.2, 39.0, 93.0, 96.0, 203.0],
    "Mass_AMU": [26.98, 118.7, 207.2, 200.6, 92.9, 45.9, 666.0, 800.0, 34.0],
    "Debye_T": [428, 200, 105, 72, 275, 1000, 400, 300, 1500],
    "Lattice_A": [4.05, 5.83, 4.95, 3.00, 3.30, 3.08, 3.82, 5.40, 2.98],
    "Lattice_C": [4.05, 3.18, 4.95, 3.00, 3.30, 3.52, 11.68, 30.80, 2.98],
    "Alpha": [23.1, 22.0, 29.0, 40.0, 7.3, 10.5, 11.0, 12.0, 2.0],
    "Xi": [160.0, 23.0, 83.0, 24.0, 38.0, 5.0, 1.5, 1.5, 2.0]
}
df = pd.DataFrame(data)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧪 Calibrate Reality")
    selected_mat = st.selectbox("Select Material", df["Material"])
    row = df[df["Material"] == selected_mat].iloc[0]
    
    st.info(f"Real Tc: {row['Tc_Real']} K")
    
    pressure = st.slider("Pressure (GPa)", 0, 200, 0)
    
    st.markdown("### 🎚️ Global Tuning")
    st.markdown("Adjust this slider until **Aluminum hits ~1.2K**. Then check Lead.")
    tuning = st.slider("Noise Sensitivity", 0.1, 5.0, 1.0, 0.1)

with col2:
    temps, signal_y, noise_y = run_simulation(row, pressure, tuning)
    
    # Find Tc
    tc_pred = 0
    for i in range(len(temps)):
        if noise_y[i] > signal_y[i]:
            tc_pred = temps[i]
            break
    if tc_pred == 0 and noise_y[-1] < signal_y[-1]: tc_pred = 300
    
    st.metric("Predicted Tc", f"{tc_pred} K", delta=f"{tc_pred - row['Tc_Real']:.1f} K")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temps, y=signal_y, name='Signal Strength (Mass/Inertia)', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=temps, y=noise_y, name='Noise Level (Entropy)', line=dict(color='red', width=2), fill='tozeroy'))
    fig.add_vline(x=row["Tc_Real"], line_dash="dash", line_color="green", annotation_text="Real Tc")
    
    fig.update_layout(title=f"Signal vs Noise: {selected_mat}", xaxis_title="Temperature (K)", yaxis_title="Integrity Units")
    st.plotly_chart(fig, use_container_width=True)
    
    if tc_pred < 5 and row['Tc_Real'] < 5:
        st.success("✅ **Correct Low Tc Logic:** Light mass or high expansion creates noise > signal very fast.")
