import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# --- CORE LOGIC: SIMUREALITY ENGINE ---

def get_prime_bonus(n):
    """Returns a stability bonus if N is Prime."""
    if n <= 1: return 0.0
    # Fast prime check for reasonable numbers
    if n % 2 == 0 and n > 2: return 0.0
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return 0.0
    return 0.15 # 15% bonus stability for Primes (The "Knot" effect)

def calculate_complexity_budget(T, mass_amu, is_2d):
    """
    Calculates the 'Thermal Tax' based on Temperature and Mass.
    Heavier mass = More static complexity cost, but less vibration noise.
    Higher T = Linear increase in entropy cost.
    """
    # Base Constants (tuned to Simureality)
    base_budget = 1.0 
    
    # 1. Dimension Folding Bonus
    if is_2d:
        base_budget += 0.33 # +33% efficiency from dropping Z-coord
        
    # 2. Thermal Tax (Entropy)
    # Amplitude of vibration ~ sqrt(T / M)
    # Complexity Cost ~ T (linear thermodynamic cost)
    thermal_cost = 0.008 * T # Empirical coefficient
    
    # 3. Mass Penalty (Gravity Lag)
    # Heavier atoms consume more compute for position updates
    mass_tax = 0.0001 * mass_amu 
    
    current_budget = base_budget - thermal_cost - mass_tax
    return max(0, current_budget)

def calculate_geometric_cost(N_ratio):
    """
    Calculates the 'Mismatch Cost'.
    If N is Integer -> Cost is 0.
    If N is X.5 -> Cost is Max (1.0).
    Primes reduce the cost of neighboring integers.
    """
    nearest_int = round(N_ratio)
    mismatch = abs(N_ratio - nearest_int) # 0 to 0.5
    
    # Base Geometric Cost (Linear penalty for mismatch)
    cost = mismatch * 2.0 # Normalized 0 to 1
    
    # Prime Discount
    # If the nearest integer is Prime, the "Well" is deeper, 
    # making it harder to jump out even with mismatch.
    if get_prime_bonus(nearest_int) > 0:
        cost *= 0.7 # 30% discount on cost if hovering near a Prime
        
    return cost

# --- UI SETUP ---
st.set_page_config(page_title="Trilex: Unified Tc Solver", layout="wide")
st.title("⚡ Trilex: Superconductor Compute Budget")
st.markdown("Determining Tc via **Conservation of Complexity**.")

# --- DATABASE ---
data = {
    "Material": ["Mercury (Hg)", "Lead (Pb)", "YBCO (Ceramic)", "BSCCO (2D Layered)", "MgB2", "H3S (High Pressure)"],
    "Type": ["Type I", "Type I", "Type II", "2D Folded", "Type II", "Hydride"],
    "Tc_Real": [4.2, 7.2, 93.0, 96.0, 39.0, 203.0],
    "Mass_AMU": [200.59, 207.2, 666.0, 800.0, 45.9, 34.0], # Approx molar mass
    "Lattice_A": [3.00, 4.95, 3.82, 5.40, 3.08, 2.98],
    "Lattice_C": [3.00, 4.95, 11.68, 30.80, 3.52, 2.98], # C-axis
    "Alpha": [40.0, 29.0, 11.0, 12.0, 10.5, 2.0], # Expansion coeff
    "Xi_Coherence": [24.0, 83.0, 1.5, 1.5, 5.0, 2.0] # In nm (simplified effective volume)
}
df = pd.DataFrame(data)

# --- SIDEBAR ---
selected = st.sidebar.selectbox("Select Material Target", df["Material"])
row = df[df["Material"] == selected].iloc[0]

# Auto-detect 2D Folding
is_2d_detected = row["Lattice_C"] > (2.5 * row["Lattice_A"])
st.sidebar.write(f"**Topology:** {'2D Folded (Layered)' if is_2d_detected else '3D Volumetric'}")

# Tuning
alpha_tune = st.sidebar.slider("Thermal Expansion Tuning", 0.5, 50.0, float(row["Alpha"]))
coherence_tune = st.sidebar.slider("Coherence Factor", 0.8, 1.5, 1.0)

# --- SIMULATION ---
temps = np.arange(0, 300, 0.5)
budget_history = []
cost_history = []
net_stability = []

# Initial Volumes
V_cell_0 = row["Lattice_A"]**2 * row["Lattice_C"]
if is_2d_detected:
    # In 2D, we only care about Area of the plane
    V_cell_0 = row["Lattice_A"]**2 

V_coherence_eff = (4/3) * np.pi * (row["Xi_Coherence"] * 10 * coherence_tune)**3
if is_2d_detected:
    # In 2D, coherence is Area (Circle)
    V_coherence_eff = np.pi * (row["Xi_Coherence"] * 10 * coherence_tune)**2

tc_predicted = 0
found_break = False

for T in temps:
    # 1. Calculate Available Budget (Supply)
    budget = calculate_complexity_budget(T, row["Mass_AMU"], is_2d_detected)
    
    # 2. Calculate Expansion
    # 2D only expands Area (2D), 3D expands Volume (3D)
    exp_factor = (1 + alpha_tune * 1e-6 * T)
    dim_power = 2 if is_2d_detected else 3
    
    V_cell_T = V_cell_0 * (exp_factor ** dim_power)
    
    # 3. Calculate Node Ratio
    N_ratio = V_coherence_eff / V_cell_T
    
    # 4. Calculate Geometric Cost (Demand)
    cost = calculate_geometric_cost(N_ratio)
    
    # 5. Net Stability
    # Stability = Supply - Demand
    stability = budget - cost
    
    budget_history.append(budget)
    cost_history.append(cost)
    net_stability.append(stability)
    
    # Check for Breakpoint
    if stability <= 0 and not found_break:
        tc_predicted = T
        found_break = True

# --- VISUALIZATION ---
st.metric("Predicted Tc (Break Point)", f"{tc_predicted} K", delta=f"{tc_predicted - row['Tc_Real']:.1f} K vs Real")

fig = go.Figure()

# Plot Budget (Supply)
fig.add_trace(go.Scatter(x=temps, y=budget_history, mode='lines', name='Compute Budget (Supply)', line=dict(color='green', dash='dot')))

# Plot Cost (Demand)
fig.add_trace(go.Scatter(x=temps, y=cost_history, mode='lines', name='Geometric Cost (Demand)', line=dict(color='red')))

# Plot Net Stability
fig.add_trace(go.Scatter(x=temps, y=net_stability, mode='lines', name='Net Stability', line=dict(color='blue', width=3), fill='tozeroy'))

# Add Tc Line
fig.add_vline(x=row["Tc_Real"], line_dash="dash", line_color="orange", annotation_text="Real Tc")

fig.update_layout(title="Stability Analysis: Budget vs Geometric Cost", xaxis_title="Temperature (K)", yaxis_title="Computational Units")
st.plotly_chart(fig, use_container_width=True)

# --- INSIGHTS ---
if is_2d_detected:
    st.success("🧩 **Dimension Folding Active:** System ignored Z-axis expansion. +33% Budget Boost applied.")
if tc_predicted > 250:
    st.warning("🔥 **Room Temp Potential:** Stability holds above 250K! Check parameters.")
elif tc_predicted < 10 and not is_2d_detected:
    st.info("❄️ **Type I Limit:** Low Tc due to lack of topological protection and high mass penalty.")
1
