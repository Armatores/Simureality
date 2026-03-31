import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
from rdkit import Chem

# =====================================================================
# SIMUREALITY: V8.0 L1 GRAPH TOPOLOGY ROUTER (RDKit Integration)
# Deterministic BDE Calculation via Exact FCC Node Strain
# =====================================================================

st.set_page_config(page_title="V8.0 Grid Topology", layout="wide", page_icon="🕸️")

# --- ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
GAMMA_SYS = 1.0418

GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11,
    "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58,
    "C=C": 655.02, "C#C": 982.53
}

# Аппаратные штрафы ГЦК-решетки (Routing Lag)
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5
STRAIN_CYCLO3 = 143.1  # Экстремальный излом 60 градусов
STRAIN_CYCLO4 = 128.8  # Излом 90 градусов
STRAIN_CONJUGATION = STRAIN_PI / 2  # Штраф за разрушение Token Ring

def analyze_bond_topology(row):
    """
    RDKit-парсер: Считывает точную топологическую нагрузку на конкретный линк.
    """
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return pd.Series([False, False, 0])
    
    try:
        bond = mol.GetBondWithIdx(bond_idx)
        is_conj = bond.GetIsConjugated()
        is_ring = bond.IsInRing()
        
        ring_strain = 0
        # Точное вычисление геометрического релифа (сброса напряжения при разрыве)
        if is_ring:
            if bond.IsInRingSize(3):
                ring_strain = STRAIN_CYCLO3
            elif bond.IsInRingSize(4):
                ring_strain = STRAIN_CYCLO4
            elif bond.IsInRingSize(5):
                ring_strain = 20.0  # Легкий излом циклопентана
                
        return pd.Series([is_conj, is_ring, ring_strain])
    except:
        return pd.Series([False, False, 0])

@st.cache_data(show_spinner=False)
def load_and_compile(file_path, sample_size):
    start_time = time.time()
    
    if not os.path.exists(file_path):
        return None, "Файл не найден.", 0
        
    df = pd.read_csv(file_path, compression='gzip')
    
    # Жесткая адресация (из V-Probe)
    col_bond = 'bond_type'
    col_bde = 'bde'
    
    df['bond_clean'] = df[col_bond].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    df_valid['Actual_BDE_kJ'] = pd.to_numeric(df_valid[col_bde], errors='coerce') * 4.184
    df_valid = df_valid.dropna(subset=['Actual_BDE_kJ'])
    
    # Ограничение выборки для тяжелого RDKit-парсинга
    if sample_size > 0 and sample_size < len(df_valid):
        df_valid = df_valid.sample(sample_size, random_state=42)
        
    # --- L1 TOPOLOGY PARSING (RDKIT) ---
    df_valid[['is_conj', 'is_ring', 'ring_strain_relief']] = df_valid.apply(analyze_bond_topology, axis=1)
    
    # --- ВЫЧИСЛЕНИЕ ПРОФИТА (GRID PHYSICS) ---
    df_valid['Grid_BDE_Base'] = df_valid['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    df_valid['Grid_BDE_Final'] = df_valid['Grid_BDE_Base']
    
    # 1. Прямые штрафы кратных связей
    df_valid.loc[df_valid['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_valid.loc[df_valid['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # 2. Штраф за разрушение Token Ring (Ароматика/Конъюгация)
    # Разрыв одинарной связи в сопряженной системе ломает динамический роутинг
    df_valid.loc[df_valid['is_conj'] & (df_valid['bond_clean'] == 'C-C'), 'Grid_BDE_Final'] += STRAIN_CONJUGATION
    
    # 3. Сброс топологического напряжения (Graph Relaxation)
    # Разрыв связи в тесном цикле ВОЗВРАЩАЕТ Матрице потраченные на излом такты
    df_valid.loc[df_valid['is_ring'] & ~df_valid['is_conj'], 'Grid_BDE_Final'] -= df_valid['ring_strain_relief']

    # --- МЕТРИКИ ---
    df_valid['Abs_Error'] = np.abs(df_valid['Grid_BDE_Final'] - df_valid['Actual_BDE_kJ'])
    df_valid['Rel_Error_Pct'] = np.where(df_valid['Actual_BDE_kJ'] != 0, 
                                        (df_valid['Abs_Error'] / df_valid['Actual_BDE_kJ']) * 100, 0)
    
    calc_time = time.time() - start_time
    return df_valid, "OK", calc_time

# --- UI ---
st.title("🕸️ V8.0 L1 Graph Topology: Exact Node Strain Engine")
st.markdown("Интеграция RDKit для прямого чтения 3D-напряжений графа. $\Sigma$-Алгоритм теперь видит точный излом каждого узла.")

FILE_NAME = "bde-db2.csv.gz"
sample_limit = st.slider("Размер выборки (RDKit работает медленнее Pandas)", 1000, 100000, 10000, step=1000)

if st.button("🚀 Декомпилировать Топологию"):
    with st.spinner(f"RDKit анализирует {sample_limit} графов..."):
        df, status, calc_time = load_and_compile(FILE_NAME, sample_limit)

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
        
        st.markdown("### ⚠️ Аномалии маршрутизации (Top 20 ошибок)")
        st.dataframe(df.nlargest(20, 'Abs_Error')[['molecule', 'bond_clean', 'is_conj', 'is_ring', 'ring_strain_relief', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']])
