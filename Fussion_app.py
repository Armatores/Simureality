import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# =====================================================================
# SIMUREALITY: FISSION CLEAVAGE SIMULATOR (TACTICAL DASHBOARD)
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
                n_str = line[4:9].strip()
                z_str = line[9:14].strip()
                be_str = line[54:67].strip().replace('#', '')
                if not n_str.isdigit() or not z_str.isdigit() or '*' in be_str or not be_str: continue
                N, Z = int(n_str), int(z_str)
                A = N + Z
                be_per_A_keV = float(be_str)
                total_be_MeV = (be_per_A_keV * A) / 1000.0
                db[(Z, N)] = total_be_MeV
            except ValueError:
                continue
    return db

@st.cache_data
def generate_fcc_magic():
    base_shells = [int((n+1)*(n+2)*(n+3)/3) for n in range(6)] 
    twist_shifts = [28, 50, 82, 126] 
    return sorted(list(set(base_shells + twist_shifts)))

MAGIC_NODES = generate_fcc_magic()
E_ALPHA = 28.320       
E_MACRO = 2.425        
E_PAIR = 1.180         
J_TAX = 0.0131         

def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z = min([abs(Z - m) for m in MAGIC_NODES])
    dist_N = min([abs(N - m) for m in MAGIC_NODES])
    geom_mismatch = dist_Z + dist_N
    base_ports = 10.0 * ((Z + N)**(2/3))
    total_ports = base_ports + (15.0 * (geom_mismatch**1.2))
    return total_ports * J_TAX

def calculate_topological_profit(Z, N):
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_NODES]) + min([abs(N - m) for m in MAGIC_NODES])) * 0.4
    
    N_macro_links = max(0, l_ideal - l_lost)
    BE = (N_alpha * E_ALPHA) + (N_macro_links * E_MACRO) - get_jitter_tax(Z, N)
    if Z % 2 == 0 and N % 2 == 0: BE += E_PAIR
    return BE

def run_fission_scan(Z_parent, N_parent, ame_db):
    results = []
    BE_parent_theo = calculate_topological_profit(Z_parent, N_parent) - 22.0
    BE_parent_exp = ame_db.get((Z_parent, N_parent), None)
    
    for Z1 in range(30, Z_parent // 2 + 1): 
        Z2 = Z_parent - Z1
        best_theo_Q = -float('inf')
        exp_Q_for_best = None
        best_N1, best_N2, best_free_n = 0, 0, 0
        
        for free_n in range(0, 10): 
            remaining_N = N_parent - free_n
            for N1 in range(int(Z1*1.2), int(Z1*1.6)):
                N2 = remaining_N - N1
                if N2 < int(Z2*1.2) or N2 > int(Z2*1.6): continue
                
                BE1_theo = calculate_topological_profit(Z1, N1)
                BE2_theo = calculate_topological_profit(Z2, N2)
                theo_Q = BE1_theo + BE2_theo - BE_parent_theo
                
                if theo_Q > best_theo_Q:
                    best_theo_Q = theo_Q
                    best_N1, best_N2, best_free_n = N1, N2, free_n
                    
                    if BE_parent_exp and (Z1, N1) in ame_db and (Z2, N2) in ame_db:
                        exp_Q_for_best = ame_db[(Z1, N1)] + ame_db[(Z2, N2)] - BE_parent_exp
                    else:
                        exp_Q_for_best = np.nan
                        
        results.append({
            "Light Fragment Z": Z1,
            "Light Fragment N": best_N1,
            "Heavy Fragment Z": Z2,
            "Heavy Fragment N": best_N2,
            "Dropped Neutrons": best_free_n,
            "Topological Profit (Grid Physics)": best_theo_Q,
            "Experimental Profit (AME2020)": exp_Q_for_best
        })
        
    return pd.DataFrame(results)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Grid Physics: Topology Dashboard", layout="wide")

st.title("⚛️ Fission Landscape: Topology vs Reality")
st.markdown("Visualizing the deterministic breakdown of the FCC lattice. The vacuum algorithm strictly minimizes computational cost ($\Sigma K \to \min$).")

ame_db = load_ame2020()

col1, col2 = st.columns(2)
with col1:
    z_input = st.number_input("Parent Protons (Z)", min_value=30, max_value=118, value=92, step=1)
with col2:
    n_input = st.number_input("Parent Neutrons (N)", min_value=30, max_value=180, value=144, step=1)

if st.button("Execute Vacuum Transaction", type="primary", use_container_width=True):
    with st.spinner("Scanning topology..."):
        df = run_fission_scan(z_input, n_input, ame_db)
    
    if not df.empty:
        # 1. ВЫДЕЛЕНИЕ ОПТИМАЛЬНОЙ КОНФИГУРАЦИИ
        winner = df.loc[df["Topological Profit (Grid Physics)"].idxmax()]
        
        st.divider()
        st.subheader("🏆 Global Topological Maximum (Optimal Cleavage)")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Light Fragment", f"Z={int(winner['Light Fragment Z'])} | N={int(winner['Light Fragment N'])}")
        m2.metric("Heavy Fragment", f"Z={int(winner['Heavy Fragment Z'])} | N={int(winner['Heavy Fragment N'])}")
        m3.metric("Garbage Collection", f"{int(winner['Dropped Neutrons'])} n", delta="Free Neutrons", delta_color="inverse")
        m4.metric("Q-Profit", f"{winner['Topological Profit (Grid Physics)']:.2f} MeV")

        # 2. ИНТЕРАКТИВНЫЙ ГРАФИК
        st.divider()
        st.subheader("Bimodal Fission Yield (Interactive Landscape)")
        
        # Подготовка данных для Plotly
        fig = px.line(df, x="Light Fragment Z", 
                      y=["Topological Profit (Grid Physics)", "Experimental Profit (AME2020)"],
                      markers=True, 
                      hover_data=["Heavy Fragment Z", "Dropped Neutrons"],
                      color_discrete_map={
                          "Topological Profit (Grid Physics)": "#00BFFF",
                          "Experimental Profit (AME2020)": "#FF4B4B"
                      })
        
        fig.update_layout(
            xaxis_title="Light Fragment Protons (Z)",
            yaxis_title="Energy Profit (MeV)",
            legend_title="Data Source",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. СОРТИРОВАННАЯ ТАБЛИЦА
        st.subheader("Raw Transaction Log (Sorted by Profit)")
        st.dataframe(df.sort_values(by="Topological Profit (Grid Physics)", ascending=False), use_container_width=True)
