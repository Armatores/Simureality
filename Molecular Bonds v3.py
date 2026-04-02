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
# SIMUREALITY: V22.0 NETWORK ROUTING (BRIDGES & PLANAR CLASHES)
# =====================================================================

st.set_page_config(page_title="V22.0 Network Routing", layout="wide", page_icon="🕸️")

GAMMA_SYS = 1.0418               
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

# 1. АНАЛИЗ УЗЛОВ (Локальные эффекты)
def parse_node_topology(mol_h, atom, exclude_idx):
    t_pen = 0.0
    r_cash = 0.0
    atomic_num = atom.GetAtomicNum()
    hyb = atom.GetHybridization()
    
    if atomic_num == 1: return 0.0, 0.0

    if atom.GetNumRadicalElectrons() > 0:
        c_pen = 70.0 
        for n in atom.GetNeighbors():
            if n.GetIdx() == exclude_idx: continue
            if n.GetAtomicNum() in [7, 8, 9, 17, 35, 53]:
                c_pen -= 50.0
                break
        t_pen += max(0, c_pen)

    if atomic_num == 6:
        if hyb == Chem.rdchem.HybridizationType.SP:
            t_pen += 140.0
        elif hyb == Chem.rdchem.HybridizationType.SP2:
            # Одиночные алкены получают штраф. Сопряженные мосты обрабатываются в edge_topology!
            has_O_sink = False
            for n in atom.GetNeighbors():
                if n.GetIdx() == exclude_idx: continue
                if mol_h.GetBondBetweenAtoms(atom.GetIdx(), n.GetIdx()).GetBondTypeAsDouble() == 2.0 and n.GetAtomicNum() == 8:
                    has_O_sink = True
            if has_O_sink: r_cash += 40.0 
            else: t_pen += 45.0  
        elif hyb == Chem.rdchem.HybridizationType.SP3:
            best_cash = 0.0
            for n in atom.GetNeighbors():
                if n.GetIdx() == exclude_idx: continue
                n_hyb = n.GetHybridization()
                if n_hyb in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP] or n.GetIsAromatic():
                    best_cash = max(best_cash, 50.0)
                elif n_hyb == Chem.rdchem.HybridizationType.SP3:
                    if n.GetAtomicNum() == 7: best_cash = max(best_cash, 25.0)
                    elif n.GetAtomicNum() == 8: best_cash = max(best_cash, 10.0)
            r_cash += best_cash

    elif atomic_num in [7, 8]:
        exclude_atom = mol_h.GetAtomWithIdx(exclude_idx)
        # Если прямой разрыв (N-O) -> это обрабатывается в edge_topology
        if exclude_atom.GetAtomicNum() not in [7, 8, 9, 17, 35, 53]:
            # Смежный разрыв
            has_clash_adjacent = False
            clash_z = 0
            for n in atom.GetNeighbors():
                if n.GetIdx() == exclude_idx: continue
                if n.GetAtomicNum() in [7, 8, 9, 17, 35, 53]:
                    has_clash_adjacent = True
                    clash_z = max(clash_z, n.GetAtomicNum())
                    break

            if hyb in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]:
                if has_clash_adjacent:
                    if clash_z == 8: r_cash += 225.0 
                    else: r_cash += 185.0            
                else: r_cash += 50.0  
            else:
                if has_clash_adjacent:
                    if atomic_num == 8: r_cash += 115.0  
                    else: r_cash += 70.0                 

    elif atomic_num == 9:  t_pen += 85.0
    elif atomic_num == 17: t_pen += 12.0
    elif atomic_num == 35: r_cash += 30.0
    elif atomic_num == 53: r_cash += 80.0

    return t_pen, r_cash

# 2. АНАЛИЗ ИНТЕРФЕЙСА (Сетевые эффекты связей)
def parse_edge_topology(a1, a2, bo):
    e_pen = 0.0
    e_cash = 0.0
    
    z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
    hyb1, hyb2 = a1.GetHybridization(), a2.GetHybridization()
    
    if bo == 1.0:
        sp2_1 = hyb1 in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]
        sp2_2 = hyb2 in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]
        
        # СЦЕНАРИЙ А: pi-Сопряженная связь (Оба SP2)
        if sp2_1 and sp2_2:
            if z1 == 6 or z2 == 6:
                # Резонансный Мост (Углерод пустой, электроны блокируют связь)
                other_z = z2 if z1 == 6 else z1
                if other_z == 8: e_pen += 80.0     # O=C-O (Эфиры)
                elif other_z == 7: e_pen += 60.0   # O=C-N (Амиды)
                else: e_pen += 20.0                # C=C-C=C (Диены)
                
                # Отменяем ложный O-sink кэшбек для мостов!
                e_cash -= 40.0 
            else:
                # Плоскостной Конфликт (У обоих порты забиты, дикое отталкивание)
                e_cash += 180.0                    # O=N-O, N=N-O
                
        # СЦЕНАРИЙ Б: Прямой Конфликт SP3-Гетероатомов
        elif z1 in [7,8,9,17,35,53] and z2 in [7,8,9,17,35,53]:
            e_cash += 100.0 # Базовое снятие конфликта
            
            # Проверка на Двойной Конфликт (N-O-N, O-O-O)
            def count_clash(atom, exclude):
                return sum(1 for n in atom.GetNeighbors() if n.GetIdx() != exclude and n.GetAtomicNum() in [7,8,9,17,35,53])
            
            if count_clash(a1, a2.GetIdx()) > 0 or count_clash(a2, a1.GetIdx()) > 0:
                e_cash += 140.0 # Взрывное расслабление цепи
                
    return e_pen, e_cash

def analyze_v22(row):
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
        
        # Топология узлов
        tp1, rc1 = parse_node_topology(mol_h, a1, a2.GetIdx())
        tp2, rc2 = parse_node_topology(mol_h, a2, a1.GetIdx())
        # Топология интерфейса
        ep, ec = parse_edge_topology(a1, a2, interface_type)
        
        tension_penalty = tp1 + tp2 + ep
        resonance_cashback = max(0.0, rc1 + rc2 + ec)
        
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
    
    df_tier[['d_actual', 'v_net', 'r1', 'r2', 'interface_type', 'tension_penalty', 'resonance_cashback', 'valid']] = df_tier.apply(analyze_v22, axis=1)
    df_tier = df_tier.dropna(subset=['valid']).copy()
    
    if len(df_tier) == 0: return df_tier, time.time() - start
        
    base_hw = ((df_tier['interface_type'] * STATIC_BASE_LOCK) + (VOLUME_BONUS * df_tier['v_net'])) * GAMMA_SYS
    
    mult_comp = comp_coeff / 50.0 if comp_coeff > 0 else 0
    mult_relax = relax_coeff / 50.0 if relax_coeff > 0 else 0
    
    df_tier['Hardware_BDE'] = base_hw
    df_tier['Penalty'] = df_tier['tension_penalty'] * mult_comp
    df_tier['Cashback'] = df_tier['resonance_cashback'] * mult_relax
    
    df_tier['Grid_BDE_Final'] = df_tier['Hardware_BDE'] + df_tier['Penalty'] - df_tier['Cashback']
    
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("🕸️ V22.0: Network Routing (Bridges & Clashes)")
st.markdown("Движок теперь понимает $\\pi$-сопряженные сети: Резонансные Мосты (штраф) и Плоскостные Конфликты (кэшбек).")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Инициализация Базы..."):
    df_base = load_base_data(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    
    col_ui1, col_ui2, col_ui3 = st.columns([1, 1, 1])
    with col_ui1:
        target_bonds = st.slider("Сложность графа", 1, max_bonds, 2, step=1)
    with col_ui2:
        comp_coeff = st.slider("Множитель Сжатия (Tension Penalty)", 0.0, 100.0, 50.0, step=5.0)
    with col_ui3:
        relax_coeff = st.slider("Множитель Релаксации (Cashback)", 0.0, 100.0, 50.0, step=5.0)
    
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    if st.button(f"🚀 Запустить Маршрутизацию (N={target_bonds})"):
        if len(df_filtered) == 0:
            st.warning("Отсутствуют данные.")
        else:
            with st.spinner("Анализ сопряженных интерфейсов..."):
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
                                 opacity=0.7, title=f"V22.0 Grid Physics (N={target_bonds})")
                min_val = min(df_result['Actual_BDE_kJ'].min(), df_result['Grid_BDE_Final'].min())
                max_val = max(df_result['Actual_BDE_kJ'].max(), df_result['Grid_BDE_Final'].max())
                fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🔍 Журнал Сетевой Топологии (N=2)")
                display_cols = ['molecule', 'bond_clean', 'v_net', 'Hardware_BDE', 'Penalty', 'Cashback', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
                st.dataframe(df_result.sort_values(by='Abs_Error', ascending=False)[display_cols].style.format({
                    "v_net": "{:.2f} Å³",
                    "Hardware_BDE": "{:.1f}", "Penalty": "+{:.1f}", "Cashback": "-{:.1f}",
                    "Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"
                }))
