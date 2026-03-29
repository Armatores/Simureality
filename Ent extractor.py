import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================================
# SIMUREALITY: NESTED ENTANGLEMENT EXTRACTOR (L1 / L2 CACHE)
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

# L1 Cache Constant (Derived from He-4 baseline)
L1_ALPHA_CACHE_MEV = 1.736 

def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    base_ports = 10.0 * ((Z + N)**(2/3))
    return (base_ports + (15.0 * ((dist_Z + dist_N)**1.6))) * J_TAX

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
    if A <= 0: return 1
    diameter = 1
    for magic_size in MAGIC_NODES:
        if A > magic_size: diameter += 1
        else: break
    current_layer_base = MAGIC_NODES[diameter - 2] if diameter > 1 else 0
    next_layer_base = MAGIC_NODES[diameter - 1] if diameter <= len(MAGIC_NODES) else A
    layer_progress = (A - current_layer_base) / max(1, (next_layer_base - current_layer_base))
    return diameter + layer_progress

def get_total_matrix_energy(Z, N):
    if Z <= 0 or N <= 0: return 0
    base_profit = calculate_topological_profit(Z, N)
    A = Z + N
    C_TAX = E_LINK * np.sqrt(2) 
    coulomb_penalty = C_TAX * ((Z * (Z - 1)) / 2.0) / get_discrete_graph_diameter(A)
    return base_profit - coulomb_penalty

def scan_nested_entanglement(ame_db):
    results = []
    for (Z, N), be_exp in ame_db.items():
        if Z < 4 or Z > 100: continue # Пропускаем совсем мелкие (H, He, Li) чтобы смотреть на макро-сеть
        if N < Z or N > Z * 1.6: continue
        
        be_grid = get_total_matrix_energy(Z, N)
        total_entanglement = be_exp - be_grid 
        
        # Разделение кэша (Hierarchical LOD)
        n_alpha_clusters = min(Z // 2, N // 2)
        n_halo_neutrons = max(0, N - Z) # L3 Cache (слабые ссылки, пока считаем их влияние нулевым)
        
        L1_energy = n_alpha_clusters * L1_ALPHA_CACHE_MEV
        L2_energy = total_entanglement - L1_energy
        
        # Энергия на один указатель Глобального Барицентра (Звездная Топология: все Альфы смотрят в центр)
        L2_per_alpha_pointer = L2_energy / n_alpha_clusters if n_alpha_clusters > 0 else 0
        
        results.append({
            "Protons (Z)": Z, "Neutrons (N)": N, "Mass (A)": Z + N,
            "Alpha Clusters (L1 Nodes)": n_alpha_clusters,
            "Total Entanglement (MeV)": total_entanglement,
            "L1 Cache (Local Prefabs)": L1_energy,
            "L2 Cache (Global Barycenter)": L2_energy,
            "L2 Energy per Global Pointer (MeV)": L2_per_alpha_pointer
        })
    return pd.DataFrame(results)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Nested Entanglement: L1/L2 Cache", layout="wide")
st.title("🌳 Hierarchical LOD: L1 & L2 Cache Separation")
st.markdown("Мы отделили фиксированный бонус Альфа-префабов (L1) от глобальной скидки за удержание всего ядра (L2). Ищем константу Глобального Барицентра.")

ame_db = load_ame2020()
if not ame_db:
    st.error("Файл mass.txt не найден!")
else:
    df = scan_nested_entanglement(ame_db)
    
    # Визуализация 1: Разделение L1 и L2
    df_sorted = df.sort_values("Mass (A)")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_sorted["Mass (A)"], y=df_sorted["L1 Cache (Local Prefabs)"], name="L1 Cache (Alpha Prefabs)", fill='tozeroy', mode='none', fillcolor='rgba(0, 255, 127, 0.5)'))
    fig1.add_trace(go.Scatter(x=df_sorted["Mass (A)"], y=df_sorted["L2 Cache (Global Barycenter)"], name="L2 Cache (Global Pointers)", fill='tonexty', mode='none', fillcolor='rgba(0, 191, 255, 0.5)'))
    fig1.update_layout(title="Архитектура Памяти: Доля L1 и L2 кэша в стабильности ядра", xaxis_title="Mass (A)", yaxis_title="Entanglement Energy (MeV)", template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

    # Визуализация 2: Идеальная Константа L2?
    fig2 = px.scatter(df, x="Mass (A)", y="L2 Energy per Global Pointer (MeV)", color="Protons (Z)", 
                      title="Энергия на ОДИН Указатель Глобального Барицентра (Очищенный L2)",
                      trendline="lowess", trendline_color_override="yellow")
    fig2.update_layout(template="plotly_dark", yaxis_title="L2 Bonus per Alpha Cluster (MeV)")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df.sort_values(by="Mass (A)", ascending=True).head(50), use_container_width=True)
