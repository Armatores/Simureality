import streamlit as st
import pandas as pd
import numpy as np
import os

# =====================================================================
# SIMUREALITY: ULTIMATE MASS ENGINE (V9)
# Phase 1: Cold FCC Geometry | Phase 2: Memory Deduplication (LOD)
# =====================================================================

def generate_fcc_magic():
    base_shells = [int((n+1)*(n+2)*(n+3)/3) for n in range(6)] 
    twist_shifts = [28, 50, 82, 126] 
    return sorted(list(set(base_shells + twist_shifts)))

MAGIC_NODES = generate_fcc_magic()

# --- ФАЗА 1: ХОЛОДНАЯ ГЕОМЕТРИЯ (SPACE AXIS) ---
E_ALPHA = 28.320       
E_MACRO = 2.425        
E_LINK = 2.360 
E_PAIR = 1.180      
J_TAX = 0.0131         

# --- ФАЗА 2: КЭШ МАСТРИЦЫ / ЗАПУТАННОСТЬ (TIME & MEMORY AXIS) ---
L1_ALPHA_CACHE = 1.736      # МэВ за каждый Альфа-префаб
L2_BASE_RATE = 9.7          # МэВ базовая ставка Глобального Указателя
VACUUM_BANDWIDTH = 137.036  # Лимит Шины (Постоянная тонкой структуры)
L3_ORPHAN_SUBSIDY = 0.47    # МэВ компенсации за маршрутизацию висячего порта

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

def compile_ultimate_mass(Z, N):
    if Z <= 0 or N <= 0: return None
    A = Z + N
    
    # ---------------------------------------------------------
    # ШАГ 1: СБОРКА ХОЛОДНОГО ГРАФА (RAW TOPOLOGY)
    # ---------------------------------------------------------
    n_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * n_alpha - 6)
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    l_lost = (dist_Z + dist_N) * 0.4
    
    raw_profit = (n_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO)
    
    halo_n = N - Z
    if halo_n > 0: 
        max_strong_links = int(Z * 0.4) 
        strong_halo = min(halo_n, max_strong_links)
        weak_halo = halo_n - strong_halo
        raw_profit += strong_halo * E_LINK
        raw_profit += weak_halo * (E_PAIR / 2.0)
        
    base_ports = 10.0 * (A**(2/3))
    jitter_tax = (base_ports + (15.0 * ((dist_Z + dist_N)**1.6))) * J_TAX
    
    # ЖЕСТКИЙ КУЛОНОВСКИЙ НАЛОГ (Без оптимизации)
    coulomb_tax = (E_LINK * np.sqrt(2)) * ((Z * (Z - 1)) / 2.0) / get_discrete_graph_diameter(A)
    
    cold_geometry_be = raw_profit - jitter_tax - coulomb_tax
    
    # ---------------------------------------------------------
    # ШАГ 2: ИЕРАРХИЧЕСКАЯ ДЕДУПЛИКАЦИЯ ПАМЯТИ (ENTANGLEMENT)
    # ---------------------------------------------------------
    # 1. L1 Cache: Замыкание локальных тетраэдров
    l1_subsidy = n_alpha * L1_ALPHA_CACHE
    
    # 2. L2 Cache: Стяжка на Барицентр + Штраф перегрузки Шины 137
    l2_subsidy = n_alpha * L2_BASE_RATE * (1.0 + (A / VACUUM_BANDWIDTH))
    
    # 3. L3 Cache: Динамическая балансировка непарных "сирот"
    unpaired_ports = (Z % 2) + (N % 2)
    l3_subsidy = unpaired_ports * L3_ORPHAN_SUBSIDY
    
    # ---------------------------------------------------------
    # ИТОГОВЫЙ КОММИТ
    # ---------------------------------------------------------
    ultimate_be = cold_geometry_be + l1_subsidy + l2_subsidy + l3_subsidy
    
    return {
        "Z": Z, "N": N, "A": A,
        "Cold Geometry BE": cold_geometry_be,
        "L1 Cache Subsidy": l1_subsidy,
        "L2 Cache Subsidy": l2_subsidy,
        "L3 Routing Bonus": l3_subsidy,
        "Ultimate BE": ultimate_be
    }

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
                db[(Z, N)] = (float(be_str) * (N + Z)) / 1000.0
            except ValueError: continue
    return db

# --- STREAMLIT UI ---
st.set_page_config(page_title="Simureality Ultimate Engine", layout="wide")
st.title("💠 Simureality V9: Ultimate Mass Defect Engine")
st.markdown("Полный рендер массы: Холодная Геометрия ГЦК-решетки + Иерархический Кэш Матрицы (Запутанность).")

ame_db = load_ame2020()

if st.button("🚀 ЗАПУСТИТЬ ГЛОБАЛЬНЫЙ БЕНЧМАРК", type="primary"):
    if not ame_db:
        st.error("Файл mass.txt не найден!")
    else:
        with st.spinner("Компиляция ядерной архитектуры..."):
            results = []
            for (Z, N), exp_be in ame_db.items():
                if Z < 2: continue
                data = compile_ultimate_mass(Z, N)
                if not data: continue
                
                error_mev = exp_be - data["Ultimate BE"]
                error_pct = (abs(error_mev) / exp_be) * 100 if exp_be > 0 else 0
                
                data["AME2020 BE"] = exp_be
                data["Error (MeV)"] = error_mev
                data["Accuracy (%)"] = 100.0 - error_pct
                results.append(data)
                
            df = pd.DataFrame(results)
            
        st.success(f"Рендер завершен. Обработано {len(df)} изотопов.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Средняя Точность", f"{df['Accuracy (%)'].mean():.4f}%")
        c2.metric("Медианная Ошибка", f"{df['Error (MeV)'].median():.3f} MeV")
        c3.metric("L2 Кэш (Максимум)", f"{df['L2 Cache Subsidy'].max():.1f} MeV")
        
        st.dataframe(df.sort_values("A").style.background_gradient(subset=['Accuracy (%)'], cmap='Greens'), use_container_width=True)
