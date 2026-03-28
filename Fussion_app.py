import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# =====================================================================
# SIMUREALITY: FISSION CLEAVAGE SIMULATOR (RELEASE CANDIDATE + RAW LOG)
# =====================================================================

@st.cache_data
def load_ame2020():
    db = {}
    file_path = "mass.txt"
    if not os.path.exists(file_path): return db
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if len(line) < 100 or "A T O M I C" in line or "mass.mas20" in line: continue
            try:
                n_str, z_str, be_str = line[4:9].strip(), line[9:14].strip(), line[54:67].strip().replace('#', '')
                if not n_str.isdigit() or not z_str.isdigit() or '*' in be_str or not be_str: continue
                N, Z = int(n_str), int(z_str)
                total_be_MeV = (float(be_str) * (N + Z)) / 1000.0
                db[(Z, N)] = total_be_MeV
            except ValueError: continue
    return db

@st.cache_data
def generate_fcc_magic():
    base_shells = [int((n+1)*(n+2)*(n+3)/3) for n in range(6)] 
    twist_shifts = [28, 50, 82, 126] 
    return sorted(list(set(base_shells + twist_shifts)))

MAGIC_NODES = generate_fcc_magic()
E_ALPHA = 28.320       
E_MACRO = 2.425        
E_LINK = 2.360         
E_PAIR = 1.180         
J_TAX = 0.0131         

def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    base_ports = 10.0 * ((Z + N)**(2/3))
    return (base_ports + (15.0 * ((dist_Z + dist_N)**1.2))) * J_TAX

def calculate_topological_profit(Z, N):
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_NODES]) + min([abs(N - m) for m in MAGIC_NODES])) * 0.4
    
    BE = (N_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO) - get_jitter_tax(Z, N)
    if Z % 2 == 0 and N % 2 == 0: BE += E_PAIR
    
    halo_n = N - Z
    if halo_n > 0: BE += halo_n * E_LINK
    return BE

def run_fission_scan(Z_parent, N_parent, ame_db):
    results = []
    BE_parent_theo = calculate_topological_profit(Z_parent, N_parent) - 22.0
    BE_parent_exp = ame_db.get((Z_parent, N_parent), None)
    
    for Z1 in range(30, Z_parent // 2 + 1): 
        Z2 = Z_parent - Z1
        best_theo_Q = -float('inf')
        exp_Q_for_best, best_N1, best_N2, best_free_n = None, 0, 0, 0
        
        for free_n in range(0, 8): 
            remaining_N = N_parent - free_n
            for N1 in range(int(Z1*1.2), int(Z1*1.6)):
                N2 = remaining_N - N1
                if N2 < int(Z2*1.2) or N2 > int(Z2*1.6): continue
                
                theo_Q = calculate_topological_profit(Z1, N1) + calculate_topological_profit(Z2, N2) - BE_parent_theo
                if theo_Q > best_theo_Q:
                    best_theo_Q, best_N1, best_N2, best_free_n = theo_Q, N1, N2, free_n
                    exp_Q_for_best = ame_db[(Z1, N1)] + ame_db[(Z2, N2)] - BE_parent_exp if (BE_parent_exp and (Z1, N1) in ame_db and (Z2, N2) in ame_db) else np.nan
                        
        results.append({
            "Light Fragment Z": Z1, "Light Fragment N": best_N1,
            "Heavy Fragment Z": Z2, "Heavy Fragment N": best_N2,
            "Dropped Neutrons": best_free_n,
            "Topological Profit (Grid Physics)": best_theo_Q,
            "Experimental Profit (AME2020)": exp_Q_for_best
        })
    return pd.DataFrame(results)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Grid Physics: Fission Simulator", layout="wide")

st.title("⚛️ Fission Landscape: Topology vs Reality")
st.markdown("Visualizing the deterministic breakdown of the FCC lattice. The vacuum algorithm strictly minimizes computational cost ($\Sigma K \to \min$).")

ame_db = load_ame2020()

ISOTOPE_PRESETS = {
    "U-236 (Thermal Fission of U-235)": (92, 144),
    "Pu-240 (Thermal Fission of Pu-239)": (94, 146),
    "Cf-252 (Spontaneous Fission)": (98, 154),
    "Fm-258 (Symmetric Anomaly)": (100, 158),
    "Pb-208 (Stable Monolith)": (82, 126),
    "Custom Manual Input": None
}

selected_preset = st.selectbox("Select Target Isotope for Cleavage Analysis", list(ISOTOPE_PRESETS.keys()))

if ISOTOPE_PRESETS[selected_preset] is None:
    col1, col2 = st.columns(2)
    z_input = col1.number_input("Parent Protons (Z)", min_value=10, max_value=118, value=92, step=1)
    n_input = col2.number_input("Parent Neutrons (N)", min_value=10, max_value=180, value=144, step=1)
else:
    z_input, n_input = ISOTOPE_PRESETS[selected_preset]
    st.info(f"Target locked: Z={z_input}, N={n_input} (A={z_input+n_input})")

if st.button("Execute Vacuum Transaction", type="primary", use_container_width=True):
    with st.spinner("Scanning lattice topology..."):
        df = run_fission_scan(z_input, n_input, ame_db)
    
    if not df.empty:
        winner = df.loc[df["Topological Profit (Grid Physics)"].idxmax()]
        max_profit = winner['Topological Profit (Grid Physics)']
        
        st.divider()
        
        if max_profit <= 0:
            st.error("🚨 TRANSACTION DENIED: Topological Profit is negative. The FCC lattice configuration is highly stable and optimally packed. This isotope DOES NOT undergo spontaneous fission.")
            st.metric("Minimum Required Profit", f"{max_profit:.2f} MeV", delta="Deficit", delta_color="inverse")
        else:
            st.success("✅ TRANSACTION APPROVED: Geometry overflow detected. Lattice cleavage is computationally profitable.")
            st.subheader("🏆 Global Topological Maximum (Optimal Cleavage)")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Light Fragment", f"Z={int(winner['Light Fragment Z'])} | N={int(winner['Light Fragment N'])}")
            m2.metric("Heavy Fragment", f"Z={int(winner['Heavy Fragment Z'])} | N={int(winner['Heavy Fragment N'])}")
            m3.metric("Garbage Collection", f"{int(winner['Dropped Neutrons'])} n", delta="Free Neutrons", delta_color="inverse")
            m4.metric("Q-Profit", f"{max_profit:.2f} MeV")

        st.divider()
        st.subheader("Bimodal Fission Yield (Interactive Landscape)")
        fig = px.line(df, x="Light Fragment Z", y=["Topological Profit (Grid Physics)", "Experimental Profit (AME2020)"],
                      markers=True, hover_data=["Heavy Fragment Z", "Dropped Neutrons"],
                      color_discrete_map={"Topological Profit (Grid Physics)": "#00BFFF", "Experimental Profit (AME2020)": "#FF4B4B"})
        fig.update_layout(xaxis_title="Light Fragment Protons (Z)", yaxis_title="Energy Profit (MeV)", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # ВОЗВРАЩЕННАЯ ТАБЛИЦА (Сырой дамп транзакций)
        st.divider()
        st.subheader("Raw Transaction Log (Sorted by Profit)")
        st.dataframe(df.sort_values(by="Topological Profit (Grid Physics)", ascending=False), use_container_width=True)
