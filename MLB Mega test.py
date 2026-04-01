import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
from rdkit import Chem

# =====================================================================
# SIMUREALITY: V9.3 HEAVY NODE COMPRESSION & CACHE PATCH (N=2)
# =====================================================================

st.set_page_config(page_title="V9.3 Unit Tester", layout="wide", page_icon="🧱")

GAMMA_SYS = 1.0418
GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11, "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58, "C=C": 655.02, "C#C": 982.53
}
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5

# --- АППАРАТНЫЕ НАЛОГИ НА КОМПРЕССИЮ (Водород vs Тяжелый Узел) ---
TAX_COMPRESSION_SP_H = 136.0   
TAX_COMPRESSION_SP2_H = 40.0   
TAX_COMPRESSION_SP_HEAVY = 192.0   
TAX_COMPRESSION_SP2_HEAVY = 82.0   

def get_graph_complexity(smiles):
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        return mol.GetNumBonds() if mol else -1
    except:
        return -1

def analyze_node_compression(row):
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return pd.Series(['UNKNOWN', False, False, False, 0.0])
        
    try:
        is_o_sink = False
        is_n_sink = False
        has_no_group = False
        
        # Сканируем весь граф на сливы и кэш
        for b in mol.GetBonds():
            if b.GetBondType() == Chem.rdchem.BondType.DOUBLE:
                syms = {b.GetBeginAtom().GetSymbol(), b.GetEndAtom().GetSymbol()}
                if 'O' in syms: is_o_sink = True
                if 'N' in syms: is_n_sink = True
                if 'N' in syms and 'O' in syms: has_no_group = True
                
        mol_h = Chem.AddHs(mol) 
        bond = mol_h.GetBondWithIdx(bond_idx)
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        
        # Читаем гибридизацию
        hyb = 'UNKNOWN'
        if 'H' in [a1.GetSymbol(), a2.GetSymbol()]:
            # Водородная связь
            carbon_atom = a2 if a1.GetSymbol() == 'H' else a1
            hyb = str(carbon_atom.GetHybridization())
        else:
            # Тяжелая связь
            hyb1 = str(a1.GetHybridization())
            hyb2 = str(a2.GetHybridization())
            if 'SP' in [hyb1, hyb2]: hyb = 'SP' # Берем максимальное сжатие
            elif 'SP2' in [hyb1, hyb2]: hyb = 'SP2'
            else: hyb = 'SP3'
            
        is_ring = bond.IsInRing()
        ring_relief = 0.0
        if is_ring:
            if bond.IsInRingSize(3): ring_relief = 143.1
            elif bond.IsInRingSize(4): ring_relief = 128.8
            elif bond.IsInRingSize(5): ring_relief = 20.0
            else: ring_relief = 30.0 
            
        return pd.Series([hyb, is_o_sink, is_n_sink, has_no_group, ring_relief])
    except:
        return pd.Series(['UNKNOWN', False, False, False, 0.0])

@st.cache_data(show_spinner=False)
def load_base_data(file_path):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path, compression='gzip')
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    df_valid['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df_valid.dropna(subset=['Actual_BDE_kJ'])
    
    df_valid['Graph_Complexity'] = df_valid['molecule'].apply(get_graph_complexity)
    return df_valid[df_valid['Graph_Complexity'] > 0]

def compile_unit_test(df_tier):
    start = time.time()
    
    df_tier[['c_hybridization', 'is_o_sink', 'is_n_sink', 'has_no_group', 'ring_relief']] = df_tier.apply(analyze_node_compression, axis=1)
    
    df_tier['Grid_BDE_Base'] = df_tier['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    df_tier['Grid_BDE_Final'] = df_tier['Grid_BDE_Base']
    
    df_tier.loc[df_tier['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_tier.loc[df_tier['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # --- ПАТЧ КОМПРЕССИИ И КЭШИРОВАНИЯ (L1 / L2) ---
    for idx, row in df_tier.iterrows():
        b_type = row['bond_clean']
        hyb = row['c_hybridization']
        o_sink = row['is_o_sink']
        n_sink = row['is_n_sink']
        has_no = row['has_no_group']
        
        penalty = 0.0
        
        # Логика для ВОДОРОДНЫХ портов (Сжатие малой массы)
        if b_type == 'C-H':
            if hyb == 'SP':
                penalty = TAX_COMPRESSION_SP_H
                if n_sink: penalty -= 8.0 
            elif hyb == 'SP2':
                if o_sink: penalty = -50.0  # Экстремальный слив кислорода
                elif n_sink: penalty = 0.0  
                else: penalty = TAX_COMPRESSION_SP2_H
            if has_no: penalty -= 130.0 # Скидка за кэш N=O
            
        # Логика для ТЯЖЕЛЫХ портов (Сжатие большой массы)
        elif b_type in ['C-C', 'C-O', 'C-N']:
            if hyb == 'SP':
                penalty = TAX_COMPRESSION_SP_HEAVY
            elif hyb == 'SP2':
                penalty = TAX_COMPRESSION_SP2_HEAVY
                if b_type == 'C-O' and o_sink: penalty += 40.0 # Кислота (O=C-O)
            if has_no: penalty -= 160.0 # Гигантская скидка за отрыв NO-радикала
                
        df_tier.at[idx, 'Grid_BDE_Final'] += penalty
    
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("🧱 V9.3 Unit Tester: Heavy Compression & Cache")
st.markdown("Мы научили систему дифференцировать сжатие легких (H) и тяжелых (C/N/O) узлов, а также выдавать скидку за Радикальный Кэш (NO).")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Загрузка и индексация датасета..."):
    df_base = load_base_data(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    col_ui1, col_ui2 = st.columns([2, 1])
    with col_ui1:
        target_bonds = st.slider("Сложность графа (Количество тяжелых связей)", 1, max_bonds, 2, step=1)
    
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    with col_ui2:
        st.info(f"Найдено молекул: {len(df_filtered)}")
    
    if st.button(f"🚀 Декомпилировать графы (N={target_bonds})"):
        if len(df_filtered) == 0:
            st.warning("В датасете нет молекул с такой сложностью.")
        else:
            with st.spinner(f"Расчет физики с учетом тяжелой компрессии для N={target_bonds}..."):
                df_result, calc_time = compile_unit_test(df_filtered)
                
            mae = df_result['Abs_Error'].mean()
            mape = df_result['Rel_Error_Pct'].mean()
            ss_res = np.sum((df_result['Actual_BDE_kJ'] - df_result['Grid_BDE_Final']) ** 2)
            ss_tot = np.sum((df_result['Actual_BDE_kJ'] - df_result['Actual_BDE_kJ'].mean()) ** 2)
            r2_score = (1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
            
            st.success(f"Анализ завершен за {calc_time:.2f} сек.")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("МАЕ", f"{mae:.2f} kJ/mol")
            col2.metric("MAPE", f"{mape:.2f}%")
            col3.metric("R² Score", f"{r2_score:.3f}")
            col4.metric("Средняя точность", f"{df_result['Accuracy'].mean():.2f}%")
            
            fig = px.scatter(df_result, x="Actual_BDE_kJ", y="Grid_BDE_Final", color="bond_clean", 
                             opacity=0.7, title=f"Grid Physics vs Data (Графы сложности {target_bonds})")
            min_val = min(df_result['Actual_BDE_kJ'].min(), df_result['Grid_BDE_Final'].min())
            max_val = max(df_result['Actual_BDE_kJ'].max(), df_result['Grid_BDE_Final'].max())
            fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 🔍 Журнал Транзакций (Топ ошибок)")
            display_cols = ['molecule', 'bond_clean', 'c_hybridization', 'has_no_group', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error', 'Accuracy']
            st.dataframe(df_result.sort_values(by='Abs_Error', ascending=False).head(15)[display_cols].style.format({
                "Actual_BDE_kJ": "{:.2f}", 
                "Grid_BDE_Final": "{:.2f}", 
                "Abs_Error": "{:.2f}",
                "Accuracy": "{:.2f}%"
            }))
