import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
from rdkit import Chem

# =====================================================================
# SIMUREALITY: V8.1 L1 GRAPH TOPOLOGY ROUTER (The Monolith)
# Deterministic BDE Calculation via Exact FCC Node Strain & Context
# =====================================================================

st.set_page_config(page_title="V8.1 Grid Topology Engine", layout="wide", page_icon="🕸️")

# --- 1. ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ (L0) ---
GAMMA_SYS = 1.0418

GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11,
    "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58,
    "C=C": 655.02, "C#C": 982.53
}

STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5
STRAIN_CYCLO3 = 143.1
STRAIN_CYCLO4 = 128.8
STRAIN_CONJUGATION = STRAIN_PI / 2  # Штраф за разрушение Token Ring

# --- 2. НОВЫЕ АППАРАТНЫЕ ПАТЧИ (L1 CONTEXT) ---
TAX_DANGLING_POINTER = 320.0  # Штраф за ионное переполнение буфера [O-], [NH-]
STRAIN_SP_SP = 290.0          # Экстремальное натяжение струны (между двумя тройными связями)
STRAIN_SP2_SP2 = 60.0         # Натяжение струны (между двумя двойными связями)
REFUND_RESONANCE = 80.0       # Скидка за кэширование радикала (Dynamic Load Balancing)

def analyze_topology(row):
    """
    RDKit-парсер: Считывает точный топологический контекст узла L1.
    """
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return pd.Series([False, 0.0, False, False, 0.0, False])
    
    try:
        bond = mol.GetBondWithIdx(bond_idx)
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        
        # ПАТЧ 1: Детектор Ионов (Buffer Overflow)
        has_ion = (a1.GetFormalCharge() != 0) or (a2.GetFormalCharge() != 0)
        
        # ПАТЧ 2: Множитель Топологического Сжатия (Натянутая струна)
        hyb1 = a1.GetHybridization()
        hyb2 = a2.GetHybridization()
        sp_strain = 0.0
        if hyb1 == Chem.rdchem.HybridizationType.SP and hyb2 == Chem.rdchem.HybridizationType.SP:
            sp_strain = STRAIN_SP_SP
        elif hyb1 == Chem.rdchem.HybridizationType.SP2 and hyb2 == Chem.rdchem.HybridizationType.SP2:
            sp_strain = STRAIN_SP2_SP2
            
        # ПАТЧ 3: Статус Кольца и Излом (Graph Relaxation)
        is_ring = bond.IsInRing()
        ring_relief = 0.0
        if is_ring:
            if bond.IsInRingSize(3): ring_relief = STRAIN_CYCLO3
            elif bond.IsInRingSize(4): ring_relief = STRAIN_CYCLO4
            elif bond.IsInRingSize(5): ring_relief = 20.0
            else: ring_relief = 30.0 # Базовый сброс напряжения
            
        # ПАТЧ 4: Динамическое Кэширование (Резонанс Радикала)
        is_bond_conj = bond.GetIsConjugated()
        # Если связь рвется рядом с Token Ring (атомы сопряжены), но сама связь не часть кольца (например, отрыв водорода)
        is_radical_cached = (a1.GetIsConjugated() or a2.GetIsConjugated()) and not is_bond_conj
        
        return pd.Series([has_ion, sp_strain, is_bond_conj, is_ring, ring_relief, is_radical_cached])
    except:
        return pd.Series([False, 0.0, False, False, 0.0, False])

@st.cache_data(show_spinner=False)
def run_compiler(file_path, sample_limit):
    start = time.time()
    if not os.path.exists(file_path):
        return None, "Файл не найден.", 0
        
    df = pd.read_csv(file_path, compression='gzip')
    
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    df_valid['Actual_BDE_kJ'] = pd.to_numeric(df_valid['bde'], errors='coerce') * 4.184
    df_valid = df_valid.dropna(subset=['Actual_BDE_kJ'])
    
    if 0 < sample_limit < len(df_valid):
        df_valid = df_valid.sample(sample_limit, random_state=42)
        
    # --- L1 PARSING (RDKIT) ---
    df_valid[['has_ion', 'sp_strain', 'is_bond_conj', 'is_ring', 'ring_relief', 'is_radical_cached']] = df_valid.apply(analyze_topology, axis=1)
    
    # --- CORE MATH: GRID PHYSICS ---
    df_valid['Grid_BDE_Base'] = df_valid['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    df_valid['Grid_BDE_Final'] = df_valid['Grid_BDE_Base']
    
    # Снятие прямых штрафов для кратных связей
    df_valid.loc[df_valid['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_valid.loc[df_valid['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # Применение Патчей Контекста L1:
    # 1. Штраф за открытый порт (Ионы)
    df_valid.loc[df_valid['has_ion'], 'Grid_BDE_Final'] += TAX_DANGLING_POINTER
    
    # 2. Штраф за топологическую компрессию (SP/SP2 натяжение)
    df_valid['Grid_BDE_Final'] += df_valid['sp_strain']
    
    # 3. Штраф за разрушение Token Ring
    df_valid.loc[df_valid['is_bond_conj'] & (df_valid['bond_clean'] == 'C-C'), 'Grid_BDE_Final'] += STRAIN_CONJUGATION
    
    # 4. Сброс напряжения малых колец
    df_valid.loc[df_valid['is_ring'] & ~df_valid['is_bond_conj'], 'Grid_BDE_Final'] -= df_valid['ring_relief']
    
    # 5. Скидка за кэширование радикала
    df_valid.loc[df_valid['is_radical_cached'], 'Grid_BDE_Final'] -= REFUND_RESONANCE

    # --- МЕТРИКИ ---
    df_valid['Abs_Error'] = np.abs(df_valid['Grid_BDE_Final'] - df_valid['Actual_BDE_kJ'])
    df_valid['Rel_Error_Pct'] = np.where(df_valid['Actual_BDE_kJ'] != 0, 
                                        (df_valid['Abs_Error'] / df_valid['Actual_BDE_kJ']) * 100, 0)
    
    return df_valid, "OK", time.time() - start

# --- UI ---
st.title("🕸️ V8.1 L1 Engine: Topology & Context Router")
st.markdown("Интеграция RDKit с полным пакетом L1-патчей: детектирование ионного переполнения, $sp$-компрессии и резонансного кэширования радикалов.")

FILE_NAME = "bde-db2.csv.gz"
sample_limit = st.slider("Размер выборки (RDKit: Батч-лимит)", 1000, 100000, 10000, step=1000)

if st.button("🚀 Компилировать Топологию (V8.1)"):
    with st.spinner(f"Диспетчер сканирует узлы... ({sample_limit} графов)"):
        df, status, calc_time = run_compiler(FILE_NAME, sample_limit)

    if df is not None:
        mae = df['Abs_Error'].mean()
        mape = df['Rel_Error_Pct'].mean()
        r2_score = 1 - (np.sum((df['Actual_BDE_kJ'] - df['Grid_BDE_Final']) ** 2) / np.sum((df['Actual_BDE_kJ'] - df['Actual_BDE_kJ'].mean()) ** 2))
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Обработано узлов", f"{len(df):,}")
        col2.metric("MAE", f"{mae:.2f} kJ/mol")
        col3.metric("MAPE", f"{mape:.2f}%")
        col4.metric("R² Score", f"{r2_score:.3f}")
        
        fig = px.scatter(df, x="Actual_BDE_kJ", y="Grid_BDE_Final", color="bond_clean", opacity=0.5,
                         title="Grid Physics vs QM (Точечная Валидация Графа)")
        min_val = min(df['Actual_BDE_kJ'].min(), df['Grid_BDE_Final'].min())
        max_val = max(df['Actual_BDE_kJ'].max(), df['Grid_BDE_Final'].max())
        fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ⚠️ Остаточные Аномалии маршрутизации (Top 20 ошибок)")
        display_cols = ['molecule', 'bond_clean', 'has_ion', 'sp_strain', 'is_radical_cached', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
        st.dataframe(df.nlargest(20, 'Abs_Error')[display_cols].style.background_gradient(subset=['Abs_Error'], cmap='Reds'))
