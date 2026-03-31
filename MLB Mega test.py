import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
from rdkit import Chem

# =====================================================================
# SIMUREALITY: V8.9 PURIST ENGINE (No Hacks, Only Grid Physics)
# =====================================================================

st.set_page_config(page_title="V8.9 Purist Grid Physics", layout="wide", page_icon="💠")

# ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ
GAMMA_SYS = 1.0418
GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11, "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58, "C=C": 655.02, "C#C": 982.53
}

# Геометрические штрафы решетки
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5

def analyze_pure_topology(row):
    """
    Хирургический RDKit-парсер: ищет только истинное кольцевое напряжение (Ring Strain)
    для конкретной разрываемой связи. Восстанавливает водороды для точности индексов.
    """
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return pd.Series([False, 0.0])
    
    try:
        mol_h = Chem.AddHs(mol) # Восстанавливаем 3D-каркас
        bond = mol_h.GetBondWithIdx(bond_idx)
        
        is_ring = bond.IsInRing()
        ring_relief = 0.0
        # Сброс напряжения при разрыве тесного кольца
        if is_ring:
            if bond.IsInRingSize(3): ring_relief = 143.1
            elif bond.IsInRingSize(4): ring_relief = 128.8
            elif bond.IsInRingSize(5): ring_relief = 20.0
            else: ring_relief = 30.0 
            
        return pd.Series([is_ring, ring_relief])
    except:
        return pd.Series([False, 0.0])

@st.cache_data(show_spinner=False)
def load_and_compile(file_path, sample_limit):
    start = time.time()
    if not os.path.exists(file_path):
        return None, "Файл не найден.", 0
        
    df = pd.read_csv(file_path, compression='gzip')
    
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    df_valid['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df_valid.dropna(subset=['Actual_BDE_kJ'])
    
    # Batch Limiter для скорости
    if 0 < sample_limit < len(df_valid):
        df_valid = df_valid.sample(sample_limit, random_state=42)
    
    # --- RDKIT ТОПОЛОГИЯ ---
    df_valid[['is_ring', 'ring_relief']] = df_valid.apply(analyze_pure_topology, axis=1)
    
    # --- ЧИСТАЯ МАТЕМАТИКА GRID PHYSICS ---
    df_valid['Grid_BDE_Base'] = df_valid['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    df_valid['Grid_BDE_Final'] = df_valid['Grid_BDE_Base']
    
    # 1. Штрафы кратных связей
    df_valid.loc[df_valid['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_valid.loc[df_valid['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # 2. Локальное кольцевое напряжение (Relaxation Profile)
    df_valid.loc[df_valid['is_ring'], 'Grid_BDE_Final'] -= df_valid['ring_relief']

    # --- МЕТРИКИ ---
    df_valid['Abs_Error'] = np.abs(df_valid['Grid_BDE_Final'] - df_valid['Actual_BDE_kJ'])
    df_valid['Rel_Error_Pct'] = np.where(df_valid['Actual_BDE_kJ'] != 0, 
                                        (df_valid['Abs_Error'] / df_valid['Actual_BDE_kJ']) * 100, 0)
    df_valid['Accuracy'] = np.maximum(0, 100.0 - df_valid['Rel_Error_Pct'])
    
    return df_valid, "OK", time.time() - start

# --- UI ---
st.title("💠 V8.9 Purist Engine: The True Grid Physics")
st.markdown("Мы удалили все AI-хаки и оставили только чистые константы решетки + хирургический расчет локального кольцевого излома.")

FILE_NAME = "bde-db2.csv.gz"
sample_limit = st.slider("Аппаратный Батч", 1000, 100000, 10000, step=1000)

if st.button("🚀 Запустить Чистую Декомпиляцию"):
    with st.spinner(f"Диспетчер применяет базовые константы ({sample_limit} узлов)..."):
        df, status, calc_time = load_and_compile(FILE_NAME, sample_limit)

    if df is not None:
        mae = df['Abs_Error'].mean()
        mape = df['Rel_Error_Pct'].mean()
        
        ss_res = np.sum((df['Actual_BDE_kJ'] - df['Grid_BDE_Final']) ** 2)
        ss_tot = np.sum((df['Actual_BDE_kJ'] - df['Actual_BDE_kJ'].mean()) ** 2)
        r2_score = 1 - (ss_res / ss_tot)
        
        st.success(f"Анализ завершен за {calc_time:.2f} сек. Обработано {len(df):,} связей.")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("МАЕ (Средняя Ошибка)", f"{mae:.2f} kJ/mol")
        col2.metric("MAPE (Относ. Ошибка)", f"{mape:.2f}%")
        col3.metric("R² Score", f"{r2_score:.3f}")
        col4.metric("Общая средняя точность", f"{df['Accuracy'].mean():.2f}%")
        
        st.markdown("---")
        st.header("🏆 АНАЛИТИКА ТРИУМФОВ (Мощь базовой геометрии)")
        
        tier_99 = df[df['Accuracy'] >= 99.0]
        tier_96 = df[(df['Accuracy'] >= 96.0) & (df['Accuracy'] < 99.0)]
        tier_93 = df[(df['Accuracy'] >= 93.0) & (df['Accuracy'] < 96.0)]
        
        t_col1, t_col2, t_col3 = st.columns(3)
        t_col1.metric("Точность 99% (Идеал)", f"{len(tier_99):,} связей")
        t_col2.metric("Точность 96% (Отлично)", f"{len(tier_96):,} связей")
        t_col3.metric("Точность 93% (Хорошо)", f"{len(tier_93):,} связей")
        
        display_cols = ['molecule', 'bond_clean', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Accuracy']
        
        with st.expander("Посмотреть Топ-10 идеальных предсказаний (99% Точность)", expanded=True):
            st.dataframe(tier_99.nlargest(10, 'Accuracy')[display_cols].style.format({"Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Accuracy": "{:.2f}%"}))
            
        with st.expander("Посмотреть Топ-10 отличных предсказаний (96% Точность)"):
            st.dataframe(tier_96.nlargest(10, 'Accuracy')[display_cols].style.format({"Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Accuracy": "{:.2f}%"}))
            
        with st.expander("Посмотреть Топ-10 хороших предсказаний (93% Точность)"):
            st.dataframe(tier_93.nlargest(10, 'Accuracy')[display_cols].style.format({"Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Accuracy": "{:.2f}%"}))

        st.markdown("---")
        st.header("⚠️ АНАЛИТИКА АНОМАЛИЙ (Топ-20 Ошибок)")
        st.markdown("Эти экстремальные квантовые флуктуации требуют разработки L2-роутера. Мы больше не пытаемся заткнуть их грязными патчами.")
        error_cols = ['molecule', 'bond_clean', 'is_ring', 'ring_relief', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
        st.dataframe(df.nlargest(20, 'Abs_Error')[error_cols].style.background_gradient(subset=['Abs_Error'], cmap='Reds').format({"Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"}))
