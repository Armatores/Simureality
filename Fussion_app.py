import streamlit as st
import time

# =====================================================================
# GRID PHYSICS: DETERMINISTIC FISSION CALCULATOR (STREAMLIT MVP)
# =====================================================================

def calculate_discrete_profit(Z, N):
    if Z < 1 or N < 1: return 0

    E_alpha = 28.320
    E_macro_link = 2.425
    E_link = 2.360

    N_alpha = Z // 2
    halo_n = N - Z

    # Топологические оптимумы (Закрытые ГЦК-полиэдры)
    magic_numbers = [2, 8, 20, 28, 50, 82]
    
    dist_Z = min([abs(Z - m) for m in magic_numbers])
    dist_N = min([abs(N - m) for m in magic_numbers])

    integrity = max(0.1, 1.0 - (dist_Z + dist_N) * 0.04)
    L_base = max(0, 3 * N_alpha - 6)
    profit_macro = L_base * integrity * E_macro_link

    profit_alpha = N_alpha * E_alpha

    # Лимит валентности (Surface Port Limit)
    max_halo = int(1.35 * Z) 

    if halo_n > max_halo:
        overflow = halo_n - max_halo
        profit_halo = max_halo * E_link - (overflow * 4.0) 
    else:
        profit_halo = halo_n * E_link

    penalty = (halo_n % 2) * 1.5 

    return profit_alpha + profit_macro + profit_halo - penalty

def optimize_fission(Z_parent, N_parent):
    best_split = None
    max_total_profit = 0 
    
    for Z1 in range(30, Z_parent // 2 + 1):
        Z2 = Z_parent - Z1
        
        for free_n in range(0, 6):
            remaining_N = N_parent - free_n
            
            for N1 in range(int(Z1 * 1.2), int(Z1 * 1.6)):
                N2 = remaining_N - N1
                
                if N2 < int(Z2 * 1.2) or N2 > int(Z2 * 1.6):
                    continue
                
                profit1 = calculate_discrete_profit(Z1, N1)
                profit2 = calculate_discrete_profit(Z2, N2)
                total_profit = profit1 + profit2
                
                if total_profit > max_total_profit:
                    max_total_profit = total_profit
                    best_split = {
                        'Fragment_1': {"Z": Z1, "N": N1, "A": Z1+N1},
                        'Fragment_2': {"Z": Z2, "N": N2, "A": Z2+N2},
                        'Free_Neutrons': free_n,
                        'Total_Profit_MeV': round(total_profit, 3)
                    }

    return best_split

# --- STREAMLIT UI ---
st.set_page_config(page_title="Grid Physics: Fission", layout="centered")

st.title("⚛️ Grid Physics: Fission Calculator")
st.markdown("""
**Ontological Basis:** Nuclear fission is not the splitting of a liquid drop, but a deterministic topological garbage collection event. 
The FCC lattice fractures along a cleavage plane that strictly minimizes the total computational cost ($\Sigma K \to \min$).
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    z_input = st.number_input("Parent Protons (Z)", min_value=80, max_value=118, value=92, step=1)
with col2:
    n_input = st.number_input("Parent Neutrons (N)", min_value=120, max_value=180, value=144, step=1)

if st.button("Calculate Topological Cleavage Plane", type="primary", use_container_width=True):
    with st.spinner("Executing Vacuum Transaction (Scanning lattice configurations)..."):
        time.sleep(0.5) # Небольшая пауза для UI-эффекта тяжелых вычислений
        result = optimize_fission(z_input, n_input)
    
    if result:
        st.success("Optimal topological fracture found!")
        
        # Вывод результатов в виде метрик
        st.subheader("Fission Products")
        m1, m2, m3 = st.columns(3)
        
        frag1 = result['Fragment_1']
        frag2 = result['Fragment_2']
        
        m1.metric(label="Light Fragment", value=f"Z={frag1['Z']}, N={frag1['N']}", delta=f"A={frag1['A']}", delta_color="off")
        m2.metric(label="Heavy Fragment", value=f"Z={frag2['Z']}, N={frag2['N']}", delta=f"A={frag2['A']}", delta_color="off")
        m3.metric(label="Garbage Collection", value=f"{result['Free_Neutrons']} n", delta="Free Neutrons", delta_color="inverse")
        
        st.divider()
        st.metric(label="Total Recovered Profit (Binding Energy)", value=f"{result['Total_Profit_MeV']} MeV")
        
        st.info("Notice the asymmetry: The vacuum optimizes for at least one geometrically perfect macro-crystal (close to magic numbers) rather than symmetrical liquid-drop splitting.")
    else:
        st.error("No valid topological split found for this geometry.")
