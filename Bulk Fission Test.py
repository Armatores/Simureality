import streamlit as st
import pandas as pd
import numpy as np
import os

# =====================================================================
# HEADLESS BULK VALIDATOR: MASSIVE MATRIX SCANNER
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

def get_dangling_port_tax(Z, N):
    return (E_LINK / 2.0) * ((Z % 2) + (N % 2))

def calculate_topological_profit(Z, N):
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_NODES]) + min([abs(N - m) for m in MAGIC_NODES])) * 0.4
    BE = (N_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO)
    
    halo_n = N - Z
    if halo_n > 0: 
        max_strong_links = int(Z * 0.4) 
        strong_halo = min(halo_n, max_strong_links)
        weak_halo = halo_n - strong_halo
        BE += strong_halo * E_LINK
        BE += weak_halo * (E_PAIR / 2.0)
    
    BE -= get_jitter_tax(Z, N)
    BE -= get_dangling_port_tax(Z, N)
    return BE

def get_discrete_graph_diameter(A):
    diameter = 1
    for magic_size in MAGIC_NODES:
        if A > magic_size: diameter += 1
        else: break
    current_layer_base = MAGIC_NODES[diameter - 2] if diameter > 1 else 0
    next_layer_base = MAGIC_NODES[diameter - 1] if diameter <= len(MAGIC_NODES) else A
    layer_progress = (A - current_layer_base) / max(1, (next_layer_base - current_layer_base))
    return diameter + layer_progress

def get_stable_endpoint(Z_start, N_start):
    current_Z, current_N = Z_start, N_start
    C_TAX = E_LINK * np.sqrt(2) 
    
    def get_beta_profit(Z, N):
        if Z <= 0 or N <= 0: return -float('inf')
        base_profit = calculate_topological_profit(Z, N)
        A = Z + N
        coulomb_penalty = C_TAX * ((Z * (Z - 1)) / 2.0) / get_discrete_graph_diameter(A)
        return base_profit - coulomb_penalty

    for _ in range(25): # Лимит шагов каскада
        p_cur = get_beta_profit(current_Z, current_N)
        p_m1 = get_beta_profit(current_Z + 1, current_N - 1)
        p_p1 = get_beta_profit(current_Z - 1, current_N + 1)
        p_m2 = get_beta_profit(current_Z + 2, current_N - 2)
        p_p2 = get_beta_profit(current_Z - 2, current_N + 2)
        
        best, nxt = p_cur, None
        if p_m1 > best: best, nxt = p_m1, (current_Z + 1, current_N - 1)
        elif p_p1 > best: best, nxt = p_p1, (current_Z - 1, current_N + 1)
        if not nxt:
            if p_m2 > p_cur: nxt = (current_Z + 2, current_N - 2)
            elif p_p2 > p_cur: nxt = (current_Z - 2, current_N + 2)
        if not nxt: break
        current_Z, current_N = nxt
        
    return current_Z, current_N

def run_bulk_scan(z_min, z_max, ame_db):
    bulk_results = []
    # Сканируем только тяжелые ядра (кандидаты на деление)
    parent_isotopes = [(Z, N) for (Z, N) in ame_db.keys() if z_min <= Z <= z_max and N > Z]
    
    progress_bar = st.progress(0)
    total = len(parent_isotopes)
    
    for idx, (Z_p, N_p) in enumerate(parent_isotopes):
        BE_p = calculate_topological_profit(Z_p, N_p) - 22.0
        best_Q = -float('inf')
        winner_data = None
        
        # 1. Ищем оптимальный разлом
        for Z1 in range(30, Z_p // 2 + 1): 
            Z2 = Z_p - Z1
            for free_n in range(0, 8): 
                rem_N = N_p - free_n
                for N1 in range(int(Z1*1.2), int(Z1*1.6)):
                    N2 = rem_N - N1
                    if N2 < int(Z2*1.2) or N2 > int(Z2*1.6): continue
                    Q = calculate_topological_profit(Z1, N1) + calculate_topological_profit(Z2, N2) - BE_p
                    if Q > best_Q:
                        best_Q = Q
                        winner_data = (Z1, N1, Z2, N2, free_n)
                        
        # 2. Прогоняем победителей через бета-каскад до стабильности
        if winner_data and best_Q > 0:
            Z1, N1, Z2, N2, free_n = winner_data
            Z1_stable, N1_stable = get_stable_endpoint(Z1, N1)
            Z2_stable, N2_stable = get_stable_endpoint(Z2, N2)
            
            bulk_results.append({
                "Parent Z": Z_p, "Parent N": N_p, "Parent Mass (A)": Z_p + N_p,
                "Light Frag Z": Z1, "Light Frag N": N1,
                "Heavy Frag Z": Z2, "Heavy Frag N": N2,
                "Dropped Prompt Neutrons": free_n,
                "Fission Profit (MeV)": best_Q,
                "Light Stable Z": Z1_stable, "Light Stable N": N1_stable,
                "Heavy Stable Z": Z2_stable, "Heavy Stable N": N2_stable
            })
            
        progress_bar.progress((idx + 1) / total)
        
    return pd.DataFrame(bulk_results)

# --- УЛЬТРА-МИНИМАЛИСТИЧНЫЙ UI ---
st.set_page_config(page_title="Headless Matrix Scanner")
st.title("🗄️ Bulk Validator: Fission + Cascade")
ame_db = load_ame2020()

st.markdown("Скрипт перебирает все изотопы в заданном диапазоне Z, делит их, находит оптимальные осколки и прогоняет каждый через Бета-каскад до полного остывания матрицы. Графиков нет, только жесткие вычисления.")

col1, col2 = st.columns(2)
z_min = col1.number_input("Min Parent Z", value=90, step=1)
z_max = col2.number_input("Max Parent Z", value=100, step=1)

if st.button("🚀 ЗАПУСТИТЬ МАССОВЫЙ ПРОГОН", type="primary", use_container_width=True):
    with st.spinner("Матрица считает. Это может занять несколько минут..."):
        final_df = run_bulk_scan(z_min, z_max, ame_db)
        
    st.success(f"Анализ завершен! Обработано {len(final_df)} транзакций.")
    st.dataframe(final_df)
    
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 СКАЧАТЬ ПОЛНУЮ СТАТИСТИКУ (CSV)",
        data=csv,
        file_name="bulk_matrix_fission_cascade.csv",
        mime="text/csv",
        use_container_width=True
    )
