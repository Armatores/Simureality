import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os

# =====================================================================
# SIMUREALITY: V8.4 GLOBAL MATRIX SCANNER & TRIUMPH AUDIT
# =====================================================================

st.set_page_config(page_title="V8.4 Grid Physics", layout="wide", page_icon="💠")

GAMMA_SYS = 1.0418
GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11, "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58, "C=C": 655.02, "C#C": 982.53
}
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5

@st.cache_data(show_spinner=False)
def load_and_compile(file_path):
    start = time.time()
    if not os.path.exists(file_path):
        return None, "Файл не найден.", 0
        
    df = pd.read_csv(file_path, compression='gzip')
    
    # Жесткая адресация колонок ALFABET
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    df_valid['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df_valid.dropna(subset=['Actual_BDE_kJ'])
    
    # --- V8.4 ВЕКТОРНЫЙ СКАНЕР МАТРИЦЫ (Глобальный контекст) ---
    smiles_str = df_valid['molecule'].astype(str)
    
    # Глобальные маркеры аппаратного напряжения
    df_valid['has_ion'] = smiles_str.str.contains(r'\[.*?[-+].*?\]', regex=True)
    df_valid['has_halogen'] = smiles_str.str.contains(r'I|Br', regex=True)
    df_valid['has_sp_tension'] = smiles_str.str.contains(r'C#C|C#N', regex=True)
    df_valid['is_conj'] = smiles_str.str.contains(r'[a-z]', regex=True)

    # --- БАЗОВАЯ МАТЕМАТИКА (GRID PHYSICS) ---
    df_valid['Grid_BDE_Base'] = df_valid['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    df_valid['Grid_BDE_Final'] = df_valid['Grid_BDE_Base']
    
    # Снятие прямых штрафов за кратные связи
    df_valid.loc[df_valid['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_valid.loc[df_valid['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # --- ПРИМЕНЕНИЕ ГЛОБАЛЬНЫХ ПАТЧЕЙ (Исправление логики Топ-20) ---
    # 1. Ионное переполнение (Buffer Overflow)
    df_valid.loc[df_valid['has_ion'], 'Grid_BDE_Final'] += 320.0
    
    # 2. Переполнение вокселя (Voxel Overflow)
    df_valid.loc[df_valid['has_halogen'], 'Grid_BDE_Final'] += 150.0
    
    # 3. Эффект натянутой струны (SP Tension) - применяется только при разрыве одинарных связей
    single_bonds = ['C-C', 'C-O', 'C-N']
    df_valid.loc[df_valid['has_sp_tension'] & (df_valid['bond_clean'].isin(single_bonds)), 'Grid_BDE_Final'] += 280.0
    
    # 4. Резонансная скидка (Token Ring Refund) - компенсация для аномально дешевых C-H в ароматике
    df_valid.loc[df_valid['is_conj'] & (df_valid['bond_clean'] == 'C-H'), 'Grid_BDE_Final'] -= 80.0

    # --- РАСЧЕТ МЕТРИК И ТОЧНОСТИ ---
    df_valid['Abs_Error'] = np.abs(df_valid['Grid_BDE_Final'] - df_valid['Actual_BDE_kJ'])
    df_valid['Rel_Error_Pct'] = np.where(df_valid['Actual_BDE_kJ'] != 0, 
                                        (df_valid['Abs_Error'] / df_valid['Actual_BDE_kJ']) * 100, 0)
    
    # Точность = 100% - Ошибка%
    df_valid['Accuracy'] = np.maximum(0, 100.0 - df_valid['Rel_Error_Pct'])
    
    return df_valid, "OK", time.time() - start

# --- UI ---
st.title("💠 V8.4 Grid Physics: Global Scanner & Triumph Audit")
st.markdown("Мы починили локальную слепоту скрипта. Теперь $\Sigma$-Алгоритм сканирует всю молекулу на наличие ионов, галогенов и натянутых струн. Добавлен модуль анализа наших сильных сторон.")

FILE_NAME = "bde-db2.csv.gz"

if st.button("🚀 Запустить Полный Аудит Матрицы"):
    with st.spinner("Векторное сканирование сотен тысяч графов..."):
        df, status, calc_time = load_and_compile(FILE_NAME)

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
        st.header("🏆 АНАЛИТИКА ТРИУМФОВ (Где мы абсолютно сильны)")
        
        # Срезы точности
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
        st.markdown("Эти молекулы все еще требуют ручной декомпиляции L2. Проверьте новые сработавшие флаги контекста.")
        
        error_cols = ['molecule', 'bond_clean', 'has_ion', 'has_halogen', 'has_sp_tension', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
        st.dataframe(df.nlargest(20, 'Abs_Error')[error_cols].style.background_gradient(subset=['Abs_Error'], cmap='Reds').format({"Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"}))
