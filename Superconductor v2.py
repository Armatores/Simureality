import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# ==========================================
# 🧠 SIMUREALITY PHYSICS ENGINE (Circuit 2)
# ==========================================

def get_prime_bonus(n):
    """
    Checks if N (node count) is Prime.
    Prime numbers act as 'Hard Knots' in the lattice, resisting decay.
    """
    if n <= 1: return 0.0
    # Fast check for demonstration
    if n % 2 == 0 and n > 2: return 0.0
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return 0.0
    return 0.20  # 20% Stability Bonus for Primes

def calculate_tolerance(material_type):
    """
    Determines how strict the geometry check is.
    - Type I (Pure Elements): VERY STRICT. Structure must be perfect.
    - Type II (Ceramics/Alloys): FORGIVING. Vortex lattice can pin defects.
    """
    if "Type I" in material_type:
        return 2.0 # Strict penalty (High Cost)
    elif "Type II" in material_type or "Ceramic" in material_type:
        return 1.2 # Lenient penalty (Low Cost)
    else:
        return 1.5 # Standard

def calculate_budget(T, mass, is_2d):
    """
    Calculates Available Computational Power (Simureality Budget).
    Limits:
    1. Global Const: Fixed starting budget.
    2. 2D Bonus: +33% if Z-coordinate is dropped (Trizistor Economy).
    3. Mass Tax: Heavy atoms consume budget for inertial calc.
    4. Thermal Tax: Entropy consumes budget linearly.
    """
    base_budget = 1.0
    
    # 1. Dimension Folding (The "BSCCO Effect")
    if is_2d:
        base_budget += 0.33 

    # 2. Mass Penalty (The "Lead Effect")
    # Heavier = More lag = Less budget for coherence
    mass_tax = 0.00015 * mass 
    
    # 3. Thermal Tax (Entropy cost)
    thermal_tax = 0.0075 * T
    
    current_budget = base_budget - mass_tax - thermal_tax
    return current_budget

def calculate_geometric_cost(N_ratio, tolerance_multiplier):
    """
    Calculates the 'Mismatch Cost'.
    Drifting away from Integer/Prime creates geometric friction.
    """
    nearest_int = round(N_ratio)
    dist = abs(N_ratio - nearest_int) # 0.0 (Perfect) to 0.5 (Chaos)
    
    # Base Cost
    cost = dist * tolerance_multiplier
    
    # Prime Discount (Resonance)
    if get_prime_bonus(nearest_int) > 0:
        cost *= 0.5 # Primes are very deep wells, hard to jump out
        
    return cost

# ==========================================
# 🎛️ UI & SETUP
# ==========================================

st.set_page_config(page_title="Trilex: Tc Solver Pro", layout="wide")

st.title("⚡ Trilex: Superconductor Compute Budget")
st.markdown("""
**Theory:** Superconductivity dies when **Computational Cost** > **Available Budget**.
* **Cost** comes from Geometric Mismatch (Thermal Expansion).
* **Budget** is limited by Mass (Inertia) and Temperature (Entropy).
* **2D Materials** gain a +33% Budget Boost (Dimension Folding).
""")

# --- DATABASE (EXPANDED) ---
# Xi (Coherence) is simplified "Effective Geometric Size" in nm for the model
data = {
    "Material": [
        "Mercury (Hg)", "Lead (Pb)", "Aluminum (Al)", "Niobium (Nb)", "Tin (Sn)",
        "YBCO (Ceramic)", "BSCCO (2D Layered)", "MgB2 (Binary)", "H3S (Hydride)"
    ],
    "Type": [
        "Type I (Pure)", "Type I (Pure)", "Type I (Pure)", "Type II (Element)", "Type I (Pure)",
        "Type II (Ceramic)", "2D Folded", "Type II (Binary)", "Type II (Hydride)"
    ],
    "Tc_Real": [4.2, 7.2, 1.2, 9.2, 3.7, 93.0, 96.0, 39.0, 203.0],
    "Mass_AMU": [200.59, 207.2, 26.98, 92.9, 118.7, 666.0, 800.0, 45.9, 34.0],
    "Lattice_A": [3.00, 4.95, 4.05, 3.30, 5.83, 3.82, 5.40, 3.08, 2.98],
    "Lattice_C": [3.00, 4.95, 4.05, 3.30, 3.18, 11.68, 30.80, 3.52, 2.98],
    "Alpha": [40.0, 29.0, 23.1, 7.3, 22.0, 11.0, 12.0, 10.5, 2.0], # Base Thermal Expansion
    "Xi_Coherence": [24.0, 83.0, 160.0, 38.0, 23.0, 1.5, 1.5, 5.0, 2.0] 
}
df = pd.DataFrame(data)

# --- CONTROLS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔬 Lab Controls")
    selected_mat = st.selectbox("Select Material", df["Material"])
    row = df[df["Material"] == selected_mat].iloc[0]
    
    # Auto-detect Physics
    is_2d = row["Lattice_C"] > (2.5 * row["Lattice_A"])
    tolerance = calculate_tolerance(row["Type"])
    
    st.info(f"**Class:** {row['Type']}")
    st.write(f"**Topology:** {'2D (Folded)' if is_2d else '3D (Volumetric)'}")
    st.write(f"**Tolerance:** {'Strict' if tolerance > 1.8 else 'Forgiving'}")

    st.markdown("---")
    st.write("**Simureality Calibration**")
    
    # Pressure Logic: Reduces Alpha
    pressure = st.slider("Pressure (GPa)", 0, 200, 0, help="Pressure kills Thermal Expansion.")
    
    # Effective Alpha Calculation
    # Simple model: Pressure reduces expansion exponentially
    alpha_reduction = np.exp(-pressure / 50.0) 
    alpha_eff = row["Alpha"] * alpha_reduction
    if pressure > 100: alpha_eff = 0.1 # Limit for extreme pressure
    
    st.metric("Effective Expansion (α)", f"{alpha_eff:.2f}", delta=f"{alpha_eff - row['Alpha']:.2f}")
    
    coherence_tune = st.slider("Coherence Factor", 0.8, 1.2, 1.0)

# ==========================================
# 🚀 SIMULATION LOOP
# ==========================================
temps = np.arange(0, 300, 0.5)
budget_hist, cost_hist, stability_hist = [], [], []
tc_pred = 0
found_break = False

# Initial Geometry
V_cell_0 = row["Lattice_A"]**2 * (1.0 if is_2d else row["Lattice_C"]) # If 2D, C is ignored for volume
# Coherence Volume (Spherical approx scaled)
V_coh_0 = (4/3) * np.pi * (row["Xi_Coherence"] * 10 * coherence_tune)**3 
if is_2d: V_coh_0 = np.pi * (row["Xi_Coherence"] * 10 * coherence_tune)**2 # Area

for T in temps:
    # 1. Budget Supply
    budget = calculate_budget(T, row["Mass_AMU"], is_2d)
    
    # 2. Geometric Demand (Cost)
    # Expansion applies to dimensions
    expansion = (1 + alpha_eff * 1e-6 * T)
    dim_power = 2 if is_2d else 3
    
    V_cell_T = V_cell_0 * (expansion ** dim_power)
    N_ratio = V_coh_0 / V_cell_T
    
    cost = calculate_geometric_cost(N_ratio, tolerance)
    
    # 3. Net Stability
    net = budget - cost
    
    budget_hist.append(budget)
    cost_hist.append(cost)
    stability_hist.append(net)
    
    if net <= 0 and not found_break:
        tc_pred = T
        found_break = True

# ==========================================
# 📊 VISUALIZATION
# ==========================================
with col2:
    st.subheader(f"Analysis: {selected_mat}")
    
    # Scorecard
    c1, c2, c3 = st.columns(3)
    c1.metric("Real Tc", f"{row['Tc_Real']} K")
    c2.metric("Simulated Tc", f"{tc_pred} K", delta_color="normal" if abs(tc_pred - row['Tc_Real']) < 5 else "inverse", delta=f"{tc_pred - row['Tc_Real']:.1f} K")
    
    # Logic Explanation
    if is_2d:
        c3.success("✨ 2D Bonus Active")
    elif pressure > 50:
        c3.warning("🔨 High Pressure")
    else:
        c3.info("📦 Standard 3D")

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temps, y=budget_hist, name='Compute Budget (Supply)', line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=temps, y=cost_hist, name='Geometric Cost (Demand)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=temps, y=stability_hist, name='Net Stability', line=dict(color='blue', width=3), fill='tozeroy'))
    
    # Reference Line
    fig.add_vline(x=row["Tc_Real"], line_dash="dash", line_color="orange", annotation_text="Real Tc")
    
    fig.update_layout(height=450, xaxis_title="Temperature (K)", yaxis_title="Computational Units", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Simureality Insights
    if tc_pred < 2.0 and row['Type'] == "Type I (Pure)":
        st.caption("ℹ️ **Simureality Note:** Low Tc caused by high 'Strictness' penalty for pure elements + Mass tax.")
    if abs(tc_pred - row['Tc_Real']) > 20 and pressure == 0 and "Hydride" in row['Material']:
        st.error("⚠️ **Mismatch Alert:** Hydrides require High Pressure to suppress Alpha expansion. Try increasing Pressure slider!")
