import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# =====================================================================
# SIMUREALITY: ENTANGLEMENT EXTRACTOR (MEMORY DEDUPLICATION)
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

def scan_entanglement_energy(ame_db):
    results = []
    for (Z, N), be_exp in ame_db.items():
        if Z < 2 or Z > 100: continue
        # Сканируем только стабильные и около-стабильные сборки (чтобы исключить экстремальные баги)
        if N < Z or N > Z * 1.6: continue
        
        be_grid = get_total_matrix_energy(Z, N)
        # ИЗВЛЕЧЕНИЕ: Разница между реальным профитом и пространственной геометрией
        entanglement_energy = be_exp - be_grid 
        
        # Считаем количество дедуплицированных пар памяти (Shared Pointers)
        shared_pointers = (Z // 2) + (N // 2)
        quantum_per_pointer = entanglement_energy / shared_pointers if shared_pointers > 0 else 0
        
        results.append({
            "Protons (Z)": Z, "Neutrons (N)": N, "Mass (A)": Z + N,
            "AME2020 Total BE (MeV)": be_exp,
            "Grid Topology BE (MeV)": be_grid,
            "Entanglement Energy (MeV)": entanglement_energy,
            "Shared Memory Pointers": shared_pointers,
            "Energy per Pointer (MeV)": quantum_per_pointer
        })
    return pd.DataFrame(results)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Entanglement Extractor", layout="wide")
st.title("🌌 The Entanglement Extractor: Memory Deduplication")
st.markdown("Извлечение энергии Квантовой Запутанности путем вычитания топологического профиля ГЦК-матрицы из экспериментальных баз AME2020.")

ame_db = load_ame2020()
if not ame_db:
    st.error("Файл mass.txt не найден! Положите базу AME2020 в папку со скриптом.")
else:
    with st.spinner("Декомпиляция энергии запутанности для всех изотопов..."):
        df = scan_entanglement_energy(ame_db)
        
    st.success(f"Анализ завершен. Обработано {len(df)} изотопов.")
    
    # Визуализация: Как Энергия Запутанности растет с массой
    fig1 = px.scatter(df, x="Mass (A)", y="Entanglement Energy (MeV)", color="Protons (Z)", 
                      hover_data=["Protons (Z)", "Neutrons (N)", "Shared Memory Pointers"],
                      title="Абсолютная Энергия Запутанности ядра (Memory Cache Bonus)")
    fig1.update_layout(template="plotly_dark", yaxis_title="Entanglement Offset (MeV)")
    st.plotly_chart(fig1, use_container_width=True)

    # Визуализация: Квант Запутанности на один Указатель (Дедупликацию)
    # Фильтруем экстремальные отклонения для чистоты графика
    df_clean = df[(df["Energy per Pointer (MeV)"] > -2) & (df["Energy per Pointer (MeV)"] < 5)]
    fig2 = px.box(df_clean, x="Protons (Z)", y="Energy per Pointer (MeV)", 
                  title="Энергия на один Shared Pointer (Константа Запутанности)")
    fig2.update_layout(template="plotly_dark", yaxis_title="Energy per Deduplicated Pair (MeV)")
    fig2.add_hline(y=df_clean["Energy per Pointer (MeV)"].median(), line_dash="dash", line_color="yellow", annotation_text="Global Entanglement Quantum")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Raw Entanglement Data")
    st.dataframe(df.sort_values(by="Entanglement Energy (MeV)", ascending=False), use_container_width=True)
