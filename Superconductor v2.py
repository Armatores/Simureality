import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# ==========================================
# 🧠 SIMUREALITY PHYSICS ENGINE (MERGED)
# ==========================================

def get_prime_bonus(n):
    if n <= 1: return 0.0
    if n % 2 == 0 and n > 2: return 0.0
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return 0.0
    return 0.15 

def calculate_budget(T, mass, debye_t, valence, is_2d):
    """
    Simureality Budget Calculation v3.0 (Material Science Edition)
    
    1. Base Throughput: Global constant.
    2. Frequency Tax (The "Al vs Pb" fix): Lighter atoms vibrate faster -> higher update rate -> MORE COST.
       Heavy atoms (Pb) are slow -> LESS COST -> Higher Budget.
    3. Traffic Tax (Valence): More electrons = more interaction checks = MORE COST.
    4. Rigidity Bonus (Debye): Stiff lattice resists thermal noise better.
    5. Folding Bonus: 2D saves 33% calculation.
    """
    
    base_throughput = 1.8 # Increased base to account for new taxes
    
    # 1. Frequency Tax (Inverse Mass)
    # Light atoms (Al, Mass 27) -> High Tax
    # Heavy atoms (Pb, Mass 207) -> Low Tax
    freq_tax = 4.0 / math.sqrt(mass) 
    
    # 2. Traffic Tax (Valence)
    # Al (3e) costs more than alkali (1e)
    traffic_tax = 0.05 * valence
    
    # 3. Thermal Tax (Entropy)
    # Scaled by Rigidity (Debye Temp). High Debye = Harder to excite = Lower thermal cost.
    thermal_cost = (T / debye_t) * 1.5
    
    # 4. Dimension Folding
    folding_bonus = 0.5 if is_2d else 0.0
    
    current_budget = base_throughput - freq_tax - traffic_tax - thermal_cost + folding_bonus
    return max(0, current_budget)

def calculate_geometric_cost(N_ratio, material_class):
    """
    Cost based on Lattice Complexity from Material Science script.
    Simple metals (Al) have higher chaos penalty.
    Complex lattices (Nb, YBCO) have error correction (lower penalty).
    """
    nearest_int = round(N_ratio)
    dist = abs(N_ratio - nearest_int)
    
    # Material Class Multiplier
    # "Simple" = 2.0 (High penalty for mismatch)
    # "Transition" = 1.2 (Robust)
    # "Ceramic" = 1.0 (Self-correcting)
    if material_class == "Simple": penalty = 2.5
    elif material_class == "Transition": penalty = 1.2
    elif material_class == "Ceramic": penalty = 0.8
    else: penalty = 1.5
    
    cost = dist * penalty
    
    if get_prime_bonus(nearest_int) > 0:
        cost *= 0.6 # Prime Resonance Discount
        
    return cost

# ==========================================
# 🎛️ UI & SETUP
# ==========================================

st.set_page_config(page_title="Trilex: Materials Edition", layout="wide")
st.title("⚡ Trilex: Superconductor (Materials Edition)")
st.markdown("**Simureality v3.0:** Integrating Lattice Stiffness & Electron Traffic.")

# --- DATABASE (The "Lost" Knowledge) ---
# Added: Debye Temperature (Stiffness), Valence (Traffic), Mat_Class
data = {
    "Material": ["Aluminum (Al)", "Tin (Sn)", "Lead (Pb)", "Mercury (Hg)", "Niobium (Nb)", "MgB2", "YBCO", "BSCCO", "H3S"],
    "Tc_Real": [1.2, 3.7, 7.2, 4.2, 9.2, 39.0, 93.0, 96.0, 203.0],
    "Mass_AMU": [26.98, 118.7, 207.2, 200.6, 92.9, 45.9, 666.0, 800.0, 34.0],
    "Debye_T": [428, 200, 105, 72, 275, 1000, 400, 300, 1500], # High = Stiff
    "Valence": [3, 4, 4, 2, 5, 2, 2, 2, 1], # Electrons per atom approx
    "Mat_Class": ["Simple", "Simple", "Simple", "Simple", "Transition", "Transition", "Ceramic", "Ceramic", "Hydride"],
    "Lattice_A": [4.05, 5.83, 4.95, 3.00, 3.30, 3.08, 3.82, 5.40, 2.98],
    "Alpha": [23.1, 22.0, 29.0, 40.0, 7.3, 10.5, 11.0, 12.0, 2.0],
    "Xi": [160.0, 23.0, 83.0, 24.0, 38.0, 5.0, 1.5, 1.5, 2.0]
}
df = pd.DataFrame(data)

# --- CONTROLS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧪 Material Config")
    selected_mat = st.selectbox("Select Target", df["Material"])
    row = df[df["Material"] == selected_mat].iloc[0]
    
    is_2d = "BSCCO" in row["Material"] or "YBCO" in row["Material"] # Simplified 2D check
    if "YBCO" in row["Material"]: is_2d = False # YBCO is 3D-ish but layered, let's keep it complex 3D for now or toggle
    
    # Manual Override for Topology
    topology = st.radio("Topology Mode", ["3D Volumetric", "2D Folded"], index=1 if is_2d else 0)
    is_2d_active = topology == "2D Folded"

    st.info(f"""
    **Properties:**
    * Mass: {row['Mass_AMU']} (Freq Tax: {4.0/math.sqrt(row['Mass_AMU']):.2f})
    * Debye T: {row['Debye_T']} K (Rigidity)
    * Valence: {row['Valence']} (Traffic)
    * Class: {row['Mat_Class']}
    """)
    
    pressure = st.slider("Pressure (GPa)", 0, 200, 0)
    alpha_eff = row["Alpha"] * np.exp(-pressure/50.0)
    if pressure > 100: alpha_eff = 0.1

# ==========================================
# 🚀 SIMULATION
# ==========================================
temps = np.arange(0, 300, 0.5)
budget_hist, cost_hist, net_hist = [], [], []
tc_pred = 0
found = False

V_cell_0 = row["Lattice_A"]**2 * (1.0 if is_2d_active else row["Lattice_A"]) # Cube or Square
V_coh_0 = (4/3)*np.pi*(row["Xi"]*10)**3 
if is_2d_active: V_coh_0 = np.pi*(row["Xi"]*10)**2

for T in temps:
    # New Budget Calculation
    budget = calculate_budget(T, row["Mass_AMU"], row["Debye_T"], row["Valence"], is_2d_active)
    
    # Geometric Cost
    exp = (1 + alpha_eff*1e-6*T)
    dim = 2 if is_2d_active else 3
    V_cell = V_cell_0 * (exp**dim)
    N_ratio = V_coh_0 / V_cell
    
    cost = calculate_geometric_cost(N_ratio, row["Mat_Class"])
    
    net = budget - cost
    
    budget_hist.append(budget)
    cost_hist.append(cost)
    net_hist.append(net)
    
    if net <= 0 and not found:
        tc_pred = T
        found = True

# ==========================================
# 📊 VISUALIZATION
# ==========================================
with col2:
    st.metric("Predicted Tc", f"{tc_pred} K", delta=f"{tc_pred - row['Tc_Real']:.1f} K")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temps, y=budget_hist, name='Compute Budget (Supply)', line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=temps, y=cost_hist, name='Geometric Cost (Demand)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=temps, y=net_hist, name='Net Stability', line=dict(color='blue', width=3), fill='tozeroy'))
    fig.add_vline(x=row["Tc_Real"], line_dash="dash", line_color="orange", annotation_text="Real Tc")
    
    fig.update_layout(yaxis_title="Compute Units", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    if row["Material"] == "Aluminum (Al)":
        st.success("✅ **Al Correction:** Low Tc due to High Frequency Tax (Low Mass) + High Valence Traffic.")
    if row["Material"] == "Niobium (Nb)":
        st.success("✅ **Nb Correction:** High Tc due to 'Transition' class stability (d-orbitals).")
