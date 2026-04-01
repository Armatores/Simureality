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
# SIMUREALITY: V18.0 TOPOLOGICAL DECOMPILER (TENSION vs CASHBACK)
# =====================================================================

st.set_page_config(page_title="V18.0 Matrix Core", layout="wide", page_icon="🧬")

# ХАРДКОД КОНСТАНТЫ СИМУЛЯЦИИ
GAMMA_SYS = 1.0418               # Системный Налог (Lattice Impedance)
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  # 1.6625 Å
STATIC_BASE_LOCK = 286.5         # Цена Shared Pointer
VOLUME_BONUS = 12.75             # Энергия за 1 Å³ чистого V_net

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

def analyze_v18(row):
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    pt = Chem.GetPeriodicTable()
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return pd.Series([np.nan]*8)
        
        mol_h = Chem.AddHs(mol)
        bond = mol_h.GetBondWithIdx(bond_idx)
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        
        r_cov1 = pt.GetRcovalent(a1.GetAtomicNum())
        r_cov2 = pt.GetRcovalent(a2.GetAtomicNum())
        interface_type = bond.GetBondTypeAsDouble()
        
        # --- БЛОК V18.0: АППАРАТНОЕ НАТЯЖЕНИЕ VS РЕЗОНАНСНЫЙ КЭШБЕК ---
        def parse_node_topology(atom, exclude_idx):
            t_pen = 0.0
            r_cash = 0.0
            atomic_num = atom.GetAtomicNum()
            
            if atomic_num == 1: return 0.0, 0.0

            hyb = atom.GetHybridization()
            
            # ПРАВИЛО 1: УГЛЕРОДНОЕ СЖАТИЕ (Vinylic/Alkynyl Tension)
            if atomic_num == 6:
                if hyb == Chem.rdchem.HybridizationType.SP:
                    t_pen += 140.0
                elif hyb == Chem.rdchem.HybridizationType.SP2:
                    t_pen += 45.0
                elif hyb == Chem.rdchem.HybridizationType.SP3:
                    for n in atom.GetNeighbors():
                        if n.GetIdx() == exclude_idx: continue
                        n_hyb = n.GetHybridization()
                        if n_hyb in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP] or n.GetIsAromatic():
                            r_cash += 50.0 
                            break

            # ПРАВИЛО 2: РАЗРЯДКА ГЕТЕРОАТОМОВ (Lone Pair Relief)
            elif atomic_num in [7, 8]:
                if hyb in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]:
                    r_cash += 225.0
                else:
                    r_cash += 20.0

            # ПРАВИЛО 3: ГАЛОГЕНЫ И СТЕРИКА
            elif atomic_num == 9:  t_pen += 85.0
            elif atomic_num == 17: t_pen += 12.0
            elif atomic_num == 35: r_cash += 30.0
            elif atomic_num == 53: r_cash += 80.0

            return t_pen, r_cash

        t_pen1, r_cash1 = parse_node_topology(a1, a2.GetIdx())
        t_pen2, r_cash2 = parse_node_topology(a2, a1.GetIdx())
        
        tension_penalty = t_pen1 + t_pen2
        resonance_cashback = r_cash1 + r_cash2
        # -----------------------------------------------------------
        
        if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0:
            return pd.Series([np.nan]*8)
        AllChem.MMFFOptimizeMolecule(mol_h)
        
        conf = mol_h.GetConformer()
        pos1 = np.array(conf.GetAtomPosition(a1.GetIdx()))
        pos2 = np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        v_exc_1 = calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        v_exc_2 = calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - v_exc_1 - v_exc_2)
        
        return pd.Series([d_actual, v_net, r_cov1, r_cov2, interface_type, tension_penalty, resonance_cashback, True])
    except:
        return pd.Series([np.nan]*8)

@st.cache_data(show_spinner=False)
def load_base_data(file_path):
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path, compression='gzip')
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df.dropna(subset=['Actual_BDE_kJ']).copy()
    df_valid['Graph_Complexity'] = df_valid['molecule'].apply(get_graph_complexity)
    return df_valid[df_valid['Graph_Complexity'] > 0]

def compile_unit_test(df_tier, comp_coeff, relax_coeff):
    start = time.time()
    
    df_tier[['d_actual', 'v_net', 'r1', 'r2', 'interface_type', 'tension_penalty', 'resonance_cashback', 'valid']] = df_tier.apply(analyze_v18, axis=1)
    df_tier = df_tier.dropna(subset=['valid']).copy()
    
    if len(df_tier) == 0: return df_tier, time.time() - start
        
    # ОНТОЛОГИЯ V18: Системный налог Матрицы применен к базовой геометрии!
    base_hw = ((df_tier['interface_type'] * STATIC_BASE_LOCK) + (VOLUME_BONUS * df_tier['v_net'])) * GAMMA_SYS
    
    # Нормализуем ползунки (значение 50 = множитель 1.0)
    mult_comp = comp_coeff / 50.0 if comp_coeff > 0 else 0
    mult_relax = relax_coeff / 50.0 if relax_coeff > 0 else 0
    
    df_tier['Hardware_BDE'] = base_hw
    df_tier['Penalty'] = df_tier['tension_penalty'] * mult_comp
    df_tier['Cashback'] = df_tier['resonance_cashback'] * mult_relax
    
    # СИНТЕЗ УРАВНЕНИЯ МАТРИЦЫ
    df_tier['Grid_BDE_Final'] = df_tier['Hardware_BDE'] + df_tier['Penalty'] - df_tier['Cashback']
    
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("🧬 V18.0: Топологический Декомпилятор Матрицы")
st.markdown("Уравнение: `BDE = (Аппаратная Геометрия * Налог 1.0418) + Штраф за Сжатие - Кэшбек Релаксации`")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Синхронизация..."):
    df_base = load_base_data(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    
    col_ui1, col_ui2, col_ui3 = st.columns([1, 1, 1])
    with col_ui1:
        target_bonds = st.slider("Сложность графа", 1, max_bonds, 1, step=1)
    with col_ui2:
        comp_coeff = st.slider("Множитель Сжатия (Tension Penalty)", 0.0, 100.0, 50.0, step=5.0)
    with col_ui3:
        relax_coeff = st.slider("Множитель Релаксации (Resonance Cashback)", 0.0, 100.0, 50.0, step=5.0)
    
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    if st.button(f"🚀 Запустить Декомпиляцию (N={target_bonds})"):
        if len(df_filtered) == 0:
            st.warning("Отсутствуют данные.")
        else:
            with st.spinner("Парсинг ГЦК-узлов и расчет термодинамики..."):
                df_result, calc_time = compile_unit_test(df_filtered, comp_coeff, relax_coeff)
                
            if len(df_result) > 0:
                mae = df_result['Abs_Error'].mean()
                mape = df_result['Rel_Error_Pct'].mean()
                ss_res = np.sum((df_result['Actual_BDE_kJ'] - df_result['Grid_BDE_Final']) ** 2)
                ss_tot = np.sum((df_result['Actual_BDE_kJ'] - df_result['Actual_BDE_kJ'].mean()) ** 2)
                r2_score = (1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
                
                st.success(f"Завершено за {calc_time:.2f} сек. Транзакций: {len(df_result)}")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("МАЕ", f"{mae:.2f} kJ/mol")
                col2.metric("MAPE", f"{mape:.2f}%")
                col3.metric("R² Score", f"{r2_score:.3f}")
                col4.metric("Точность", f"{df_result['Accuracy'].mean():.2f}%")
                
                fig = px.scatter(df_result, x="Actual_BDE_kJ", y="Grid_BDE_Final", color="bond_clean", 
                                 hover_data=["v_net", "Penalty", "Cashback"],
                                 opacity=0.7, title=f"V18.0 Grid Physics vs Data")
                min_val = min(df_result['Actual_BDE_kJ'].min(), df_result['Grid_BDE_Final'].min())
                max_val = max(df_result['Actual_BDE_kJ'].max(), df_result['Grid_BDE_Final'].max())
                fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🔍 Журнал Транзакций (Декомпилятор)")
                display_cols = ['molecule', 'bond_clean', 'v_net', 'Hardware_BDE', 'Penalty', 'Cashback', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
                st.dataframe(df_result.sort_values(by='Abs_Error', ascending=False)[display_cols].style.format({
                    "v_net": "{:.2f} Å³",
                    "Hardware_BDE": "{:.1f}", "Penalty": "+{:.1f}", "Cashback": "-{:.1f}",
                    "Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"
                }))
