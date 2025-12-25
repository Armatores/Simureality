import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# ==========================================
# 🧠 CORE LOGIC: PHASE TRANSITION
# ==========================================

def get_prime_dampener(n):
    """
    If geometry is Prime, the 'Cost of Coherence' grows slower.
    Primes are efficient geometric structures.
    """
    if n <= 1: return 1.0
    if n % 2 == 0 and n > 2: return 1.0 # Composite (No dampening)
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return 1.0 # Composite
    return 0.1 # PRIME: Massive reduction in coherence cost (10x stability)

def calculate_phase_diagram(row, pressure_gpa, alpha_tune_factor):
    """
    Calculates two curves:
    1. Chaos Cost (Threshold): Constant/Slow growth. Proportional to Mass.
       High Mass = Expensive to simulate in Chaos Mode = System prefers Superconductivity longer.
    2. Coherence Cost (The Burden): Starts at 0, grows with T, Alpha, Valence.
       When Coherence Cost > Chaos Cost -> PHASE TRANSITION (Tc).
    """
    
    temps = np.arange(0, 300, 0.5)
    
    # --- 1. THE CHAOS CEILING (Threshold) ---
    # Heavier atoms create a higher "Information Inertia" barrier.
    # The system resists breaking the optimized state because recalculating heavy atoms is 'expensive'.
    # Mass Factor: simple sqrt scale for stability.
    mass_inertia = math.sqrt(row["Mass_AMU"]) 
    
    # System Tax Gamma ~ 1.04. Used as a baseline scaler.
    chaos_threshold_base = mass_inertia * 1.04 
    
    chaos_curve = [chaos_threshold_base for _ in temps] # Constant for simplicity (or slight tilt)

    # --- 2. THE COHERENCE BURDEN (Rising Cost) ---
    coherence_curve = []
    
    # Pressure Effect: Reduces Alpha exponentially
    # At 150 GPa, expansion is effectively dead.
    alpha_real = row["Alpha"] * np.exp(-pressure_gpa / 40.0) * alpha_tune_factor
    
    # Valence Penalty: More electrons = harder to synchronize
    valence_penalty = row["Valence"] ** 1.5 
    
    # Topology Factor: 2D materials dump entropy into the void (Z-axis).
    # This drastically slows down the cost accumulation.
    is_2d = row["Lattice_C"] > (2.5 * row["Lattice_A"]) or "Layered" in row["Type"]
    topology_dampener = 0.05 if is_2d else 1.0 
    
    # Initial Geometry
    V_cell_0 = row["Lattice_A"]**2 * (1.0 if is_2d else row["Lattice_C"])
    V_coh_0 = (4/3)*np.pi*(row["Xi"]*10)**3 
    if is_2d: V_coh_0 = np.pi*(row["Xi"]*10)**2

    for T in temps:
        # A. Geometric Mismatch Cost
        expansion_factor = (1 + alpha_real * 1e-6 * T)
        dim = 2 if is_2d else 3
        V_cell_T = V_cell_0 * (expansion_factor ** dim)
        
        N_nodes = V_coh_0 / V_cell_T
        nearest_int = round(N_nodes)
        mismatch = abs(N_nodes - nearest_int) # 0 to 0.5
        
        # Prime Resonance Check
        prime_factor = get_prime_dampener(nearest_int)
        
        # B. Thermal Entropy Cost
        # T * Alpha * Valence = The rate of information decay
        entropy_generation = T * alpha_real * valence_penalty * 0.05
        
        # C. Total Coherence Cost
        # Mismatch adds instantaneous spikes
        # Entropy adds cumulative trend
        # Topology reduces the whole curve
        current_cost = (entropy_generation + (mismatch * 20.0)) * topology_dampener * prime_factor
        
        coherence_curve.append(current_cost)

    return temps, chaos_curve, coherence_curve

# ==========================================
# 🎛️ UI SETUP
# ==========================================
st.set_page_config(page_title="Simureality v4.0: Phase Transition", layout="wide")
st.title("⚡ Simureality v4.0: The Phase Transition Model")
st.markdown("""
**New Paradigm:** Superconductivity is the **Optimal State**. It persists until the **Cost of Coherence** (Entropy) exceeds the **Cost of Chaos** (System Tax).
* **Heavy Atoms:** High Chaos Cost (High Ceiling) -> Higher Tc.
* **2D Topology:** Low Coherence Cost (Flat Curve) -> Higher Tc.
* **Pressure:** Kills Expansion -> Higher Tc.
""")

# DATABASE (Added Valence & Correct Masses)
data = {
    "Material": ["Aluminum (Al)", "Tin (Sn)", "Lead (Pb)", "Mercury (Hg)", "Niobium (Nb)", "MgB2", "YBCO", "BSCCO", "H3S"],
    "Type": ["Type I", "Type I", "Type I", "Type I", "Type II", "Type II", "Layered", "Layered", "Hydride"],
    "Tc_Real": [1.2, 3.7, 7.2, 4.2, 9.2, 39.0, 93.0, 96.0, 203.0],
    "Mass_AMU": [26.98, 118.7, 207.2, 200.6, 92.9, 45.9, 666.0, 800.0, 34.0],
    "Valence": [3, 4, 4, 2, 5, 2, 2, 2, 1], # Key parameter for entropy generation
    "Lattice_A": [4.05, 5.83, 4.95, 3.00, 3.30, 3.08, 3.82, 5.40, 2.98],
    "Lattice_C": [4.05, 3.18, 4.95, 3.00, 3.30, 3.52, 11.68, 30.80, 2.98],
    "Alpha": [23.1, 22.0, 29.0, 40.0, 7.3, 10.5, 11.0, 12.0, 2.0],
    "Xi": [160.0, 23.0, 83.0, 24.0, 38.0, 5.0, 1.5, 1.5, 2.0]
}
df = pd.DataFrame(data)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧪 Controls")
    selected_mat = st.selectbox("Select Material", df["Material"])
    row = df[df["Material"] == selected_mat].iloc[0]
    
    pressure = st.slider("Pressure (GPa)", 0, 200, 0)
    alpha_tune = st.slider("Global Sensitivity", 0.5, 2.0, 1.0, 0.1)

    st.markdown("---")
    st.info(f"""
    **Material DNA:**
    * **Mass:** {row['Mass_AMU']} (Chaos Ceiling Height)
    * **Valence:** {row['Valence']} (Entropy Generator)
    * **Alpha:** {row['Alpha']} (Expansion Rate)
    """)

# ==========================================
# 🚀 SIMULATION
# ==========================================
temps, chaos_y, coherence_y = calculate_phase_diagram(row, pressure, alpha_tune)

# Find Intersection (Tc)
tc_pred = 0
for i in range(len(temps)):
    if coherence_y[i] > chaos_y[i]:
        tc_pred = temps[i]
        break

# Special handling for "Never Intersected" (Room Temp Superconductor)
if tc_pred == 0 and coherence_y[-1] < chaos_y[-1]:
    tc_pred = 300.0 

# ==========================================
# 📊 VISUALIZATION
# ==========================================
with col2:
    st.metric("Predicted Tc (Phase Shift)", f"{tc_pred} K", delta=f"{tc_pred - row['Tc_Real']:.1f} K")
    
    fig = go.Figure()
    
    # 1. Chaos Ceiling (Blue Line) - The limit of System Stability
    fig.add_trace(go.Scatter(x=temps, y=chaos_y, name='Chaos Cost (Threshold)', 
                             line=dict(color='blue', width=4)))
    
    # 2. Coherence Burden (Red Line) - The Entropy Attack
    fig.add_trace(go.Scatter(x=temps, y=coherence_y, name='Coherence Cost (Entropy)', 
                             line=dict(color='red', width=2), fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.1)'))
    
    # Tc Marker
    fig.add_vline(x=row["Tc_Real"], line_dash="dash", line_color="green", annotation_text="Real Tc")
    
    fig.update_layout(title="Phase Transition Diagram: Order vs Chaos",
                      xaxis_title="Temperature (K)", yaxis_title="Information Cost",
                      template="plotly_white")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    if row["Mass_AMU"] < 40 and row["Valence"] > 2:
        st.caption("📉 **Why Low Tc?** Low Mass (Low Ceiling) + High Valence (Fast Entropy Growth) = Instant Phase Shift.")
    if row["Lattice_C"] > 10:
        st.caption("📈 **Why High Tc?** 2D Topology dumps entropy, keeping the Cost Curve flat.")
