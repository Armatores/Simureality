import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: V15.0 HOMOLYTIC CLEAVAGE ENGINE (ДИНАМИЧЕСКИЙ РАЗРЫВ)
# =====================================================================

st.set_page_config(page_title="V15.0 Dynamic Graph Cleavage", layout="wide", page_icon="✂️")

VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             

def get_graph_complexity(smiles):
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        return mol.GetNumBonds() if mol else -1
    except:
        return -1

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2) ** 3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def calculate_mol_total_energy(mol):
    """
    Оптимизирует 3D-каркас и считает суммарную энергию (Сложность) всех связей в графе.
    """
    pt = Chem.GetPeriodicTable()
    
    # Пытаемся оптимизировать. Если молекула - радикал, MMFF94 может капризничать,
    # но RDKit обычно справляется с базовой геометрией.
    if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(mol)
    except:
        pass # Если силовое поле не справилось с радикалом, берем сырую 3D геометрию
        
    conf = mol.GetConformer()
    total_energy = 0.0
    
    for bond in mol.GetBonds():
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        r_cov1 = pt.GetRcovalent(a1.GetAtomicNum())
        r_cov2 = pt.GetRcovalent(a2.GetAtomicNum())
        interface_type = bond.GetBondTypeAsDouble()
        
        pos1 = np.array(conf.GetAtomPosition(a1.GetIdx()))
        pos2 = np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        v_exc_1 = calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        v_exc_2 = calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - v_exc_1 - v_exc_2)
        
        bond_energy = (interface_type * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
        total_energy += bond_energy
        
    return total_energy

def analyze_cleavage(row):
    """Движок симуляции разрыва графа."""
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return pd.Series([np.nan]*5)
        mol_h = Chem.AddHs(mol)
        
        # 1. Считаем глобальную стабильность целой молекулы ДО разрыва
        mol_intact = Chem.Mol(mol_h)
        energy_intact = calculate_mol_total_energy(mol_intact)
        if energy_intact is None: return pd.Series([np.nan]*5)
        
        # Запоминаем локальную прочность самой целевой связи (для аналитики кэшбека)
        bond = mol_intact.GetBondWithIdx(bond_idx)
        a1_idx, a2_idx = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        
        # 2. РАЗРЫВ СВЯЗИ (Cleavage)
        rwmol = Chem.RWMol(mol_h)
        rwmol.RemoveBond(a1_idx, a2_idx)
        
        # Разбиваем на два отдельных радикала
        frags = Chem.GetMolFrags(rwmol, asMols=True, sanitizeFrags=False)
        
        # 3. Считаем энергию обломков ПОСЛЕ релаксации в вакууме
        energy_fragments = 0.0
        for frag in frags:
            frag_e = calculate_mol_total_energy(frag)
            if frag_e is None: return pd.Series([np.nan]*5)
            energy_fragments += frag_e
            
        # 4. Истинный BDE Матрицы: Разница общей сложности
        bde_dynamic = energy_intact - energy_fragments
        
        return pd.Series([energy_intact, energy_fragments, bde_dynamic, True])
    except:
        return pd.Series([np.nan]*5)

@st.cache_data(show_spinner=False)
def load_base_data(file_path):
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path, compression='gzip')
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df.dropna(subset=['Actual_BDE_kJ']).copy()
    df_valid['Graph_Complexity'] = df_valid['molecule'].apply(get_graph_complexity)
    return df_valid[df_valid['Graph_Complexity'] > 0]

def compile_unit_test(df_tier):
    start = time.time()
    
    df_tier[['E_intact', 'E_frags', 'Grid_BDE_Final', 'valid']] = df_tier.apply(analyze_cleavage, axis=1)
    df_tier = df_tier.dropna(subset=['valid']).copy()
    
    if len(df_tier) == 0: return df_tier, time.time() - start
        
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("✂️ V15.0: Движок Гомолитического Разрыва Графов")
st.markdown("Модель вычисляет истинный BDE как $\Delta \Sigma K$: разницу между суммарной прочностью целой молекулы и суммарной прочностью двух расслабленных радикалов после разрыва.")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Синхронизация с базой..."):
    df_base = load_base_data(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    
    col_ui1, col_ui2 = st.columns([2, 1])
    with col_ui1:
        target_bonds = st.slider("Сложность графа", 1, max_bonds, 1, step=1)
    
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    with col_ui2:
        st.info(f"Транзакций: {len(df_filtered)}")
    
    if st.button(f"🚀 Симулировать Разрыв (N={target_bonds})"):
        if len(df_filtered) == 0:
            st.warning("Отсутствуют данные.")
        else:
            with st.spinner("Оптимизация графов до и после разрыва... Это требует времени процессора."):
                df_result, calc_time = compile_unit_test(df_filtered)
                
            if len(df_result) > 0:
                mae = df_result['Abs_Error'].mean()
                mape = df_result['Rel_Error_Pct'].mean()
                ss_res = np.sum((df_result['Actual_BDE_kJ'] - df_result['Grid_BDE_Final']) ** 2)
                ss_tot = np.sum((df_result['Actual_BDE_kJ'] - df_result['Actual_BDE_kJ'].mean()) ** 2)
                r2_score = (1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
                
                st.success(f"Завершено за {calc_time:.2f} сек.")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("МАЕ", f"{mae:.2f} kJ/mol")
                col2.metric("MAPE", f"{mape:.2f}%")
                col3.metric("R² Score", f"{r2_score:.3f}")
                col4.metric("Точность", f"{df_result['Accuracy'].mean():.2f}%")
                
                fig = px.scatter(df_result, x="Actual_BDE_kJ", y="Grid_BDE_Final", color="bond_clean", 
                                 hover_data=["E_intact", "E_frags"],
                                 opacity=0.7, title=f"V15 Динамический Разрыв vs Факт (Сложность: {target_bonds})")
                min_val = min(df_result['Actual_BDE_kJ'].min(), df_result['Grid_BDE_Final'].min())
                max_val = max(df_result['Actual_BDE_kJ'].max(), df_result['Grid_BDE_Final'].max())
                fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🔍 Лог Симуляции $\Delta \Sigma K$")
                display_cols = ['molecule', 'bond_clean', 'E_intact', 'E_frags', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
                st.dataframe(df_result.sort_values(by='Abs_Error', ascending=False)[display_cols].style.format({
                    "E_intact": "{:.1f}", "E_frags": "{:.1f}",
                    "Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"
                }))
