import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# --- MATH CORE ---
def is_prime(n):
    if n <= 1: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

# --- CONFIG ---
st.set_page_config(page_title="Superconductor Resonance", layout="wide")
st.title("⚡ Superconductor Tc Predictor")
st.markdown("**Simureality Circuit:** Tracking the Prime Resonance break-point during thermal expansion.")

# --- DATA LOADER ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("superconductors_db.csv")
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Database superconductors_db.csv not found!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("🔬 Material Chamber")
selected_mat = st.sidebar.selectbox("Select Superconductor", df["Material"])
row = df[df["Material"] == selected_mat].iloc[0]

# Extract Params
Tc_real = row["Tc_critical"]
a_0 = row["a_lattice"]
b_0 = row["b_lattice"]
c_0 = row["c_lattice"]
xi_ab = row["Xi_ab_coherence"]
xi_c = row["Xi_c_coherence"]
alpha_0 = row["Alpha_expansion"] # in 10^-6 K^-1

# Fine Tuning
st.sidebar.markdown("---")
st.sidebar.write("🎛️ **Simureality Calibration**")
alpha_tune = st.sidebar.slider("Thermal Expansion (α) [10⁻⁶]", 1.0, 50.0, float(alpha_0), 0.1)
xi_tune_factor = st.sidebar.slider("Coherence Volume Factor", 0.8, 1.2, 1.0, 0.01)

# --- PHYSICS ENGINE ---
# We simulate Temperature from 0K to 150K (or 300K)
temp_range = np.arange(0, 300, 0.5)
nodes_history = []
stability_history = []

# Volume of Unit Cell at 0K
V_cell_0 = a_0 * b_0 * c_0

# Volume of Cooper Pair (Coherence Volume)
# Ellipsoid volume = 4/3 * pi * a * b * c
# Here dimensions are xi_ab, xi_ab, xi_c (nm) -> convert to Angstrom for calc?
# Let's keep everything in Angstroms (1 nm = 10 A)
xi_ab_A = xi_ab * 10 * xi_tune_factor
xi_c_A = xi_c * 10 * xi_tune_factor
V_coherence_0 = (4/3) * np.pi * (xi_ab_A**2) * xi_c_A

for T in temp_range:
    # 1. Thermal Expansion
    # Linear expansion approximation: L(T) = L0 * (1 + alpha * T)
    # Volume expansion: V(T) approx V0 * (1 + 3*alpha*T)
    # Alpha is in 10^-6
    expansion_factor = (1 + alpha_tune * 1e-6 * T)
    
    # Lattice expands -> Cell gets bigger
    V_cell_T = V_cell_0 * (expansion_factor ** 3) 
    
    # Coherence Length? 
    # In Ginzburg-Landau, Xi diverges at Tc. But we are looking for the STRUCTURAL cause.
    # Simureality Hypothesis: The "Hardware" (Lattice) expands relative to the "Software" (Cooper Pair).
    # Let's assume the Quantum Object (Cooper Pair) is geometrically rigid at first approximation,
    # or it scales differently. Let's try Constant Cooper Volume vs Expanding Lattice.
    
    V_coherence_T = V_coherence_0 # Fixed quantum object size
    
    # NUMBER OF NODES
    N_nodes = V_coherence_T / V_cell_T
    N_int = int(round(N_nodes))
    
    nodes_history.append(N_nodes)
    
    # STABILITY SCORE
    # 100 if Prime, lower if Composite
    if is_prime(N_int):
        stability_history.append(100) # Resonance
    else:
        # Check proximity to integer
        diff = abs(N_nodes - N_int)
        # If it's composite, how "bad" is it?
        divs = 0
        for i in range(1, int(math.sqrt(N_int))+1):
            if N_int % i == 0: divs += 2
        score = max(0, 100 - divs*5)
        
        # Penalize for drift from integer
        score = score * (1 - diff*2) 
        stability_history.append(max(0, score))

# --- PLOTTING ---
fig = go.Figure()

# Stability Line
fig.add_trace(go.Scatter(x=temp_range, y=stability_history, mode='lines', name='Resonance Score', line=dict(color='#00CC96', width=2)))

# Critical Temp Line (Real)
fig.add_vline(x=Tc_real, line_dash="dash", line_color="red", annotation_text=f"Tc (Real): {Tc_real}K")

fig.update_layout(title=f"Thermal Resonance Scan: {selected_mat}", xaxis_title="Temperature (K)", yaxis_title="Geometric Stability (0-100)")

st.plotly_chart(fig, use_container_width=True)

# --- ANALYSIS ---
# Find peaks near Tc
peaks = []
for i in range(1, len(stability_history)-1):
    if stability_history[i] > stability_history[i-1] and stability_history[i] > stability_history[i+1]:
        peaks.append((temp_range[i], nodes_history[i]))

st.subheader("📊 Resonance Analysis")
col1, col2 = st.columns(2)

with col1:
    st.metric("Real Tc", f"{Tc_real} K")
    # Find nearest peak
    nearest_peak_T = min(peaks, key=lambda x: abs(x[0] - Tc_real))[0] if peaks else 0
    nearest_peak_N = min(peaks, key=lambda x: abs(x[0] - Tc_real))[1] if peaks else 0
    st.metric("Predicted Resonance Tc", f"{nearest_peak_T} K", delta=f"{nearest_peak_T - Tc_real:.1f} K")

with col2:
    st.metric("Nodes at Tc", f"{int(nearest_peak_N)}")
    if is_prime(int(nearest_peak_N)):
        st.success("✅ At Tc, the lattice hits a PRIME NUMBER!")
    else:
        st.warning("⚠️ At Tc, geometry is Composite.")

st.info("Гипотеза: Если Красная Линия (Реальный Tc) совпадает с Пиком Графика — значит, сверхпроводимость умирает, потому что решетка 'съезжает' с резонансного числа.")
