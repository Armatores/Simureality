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
# SIMUREALITY: V16.0 HARDWARE RIGIDITY INDEX
# =====================================================================

st.set_page_config(page_title="V16.0 Rigidity Index", layout="wide", page_icon="🔗")

VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  # 1.6625 Å
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

def analyze_v16(row):
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    pt = Chem.GetPeriodicTable()
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return pd.Series([np.nan]*7)
        
        mol_h = Chem.AddHs(mol)
        bond = mol_h.GetBondWithIdx(bond_idx)
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        
        r_cov1 = pt.GetRcovalent(a1.GetAtomicNum())
        r_cov2 = pt.GetRcovalent(a2.GetAtomicNum())
        interface_type = bond.GetBondTypeAsDouble()
        
        # --- БЛОК V16: ИНДЕКС ГИБКОСТИ (Шарниры vs Сварка) ---
        flex_score = 0.0
        
        def parse_flexibility(atom, exclude_idx):
            score = 0.0
            for n in atom.GetNeighbors():
                if n.GetIdx() == exclude_idx: continue
                b_order = mol_h.GetBondBetweenAtoms(atom.GetIdx(), n.GetIdx()).GetBondTypeAsDouble()
                # Только одинарные связи дают кэшбек при релаксации (работают как шарниры)
                if b_order == 1.0:
                    score += pt.GetRcovalent(n.GetAtomicNum())
            return score

        flex_score += parse_flexibility(a1, a2.GetIdx())
        flex_score += parse_flexibility(a2, a1.GetIdx())
        # ---------------------------------------------------
        
        if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0:
            return pd.Series([np.nan]*7)
        AllChem.MMFFOptimizeMolecule(mol_h)
        
        conf = mol_h.GetConformer()
        pos1 = np.array(conf.GetAtomPosition(a1.GetIdx()))
        pos2 = np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        
        # Объем чистого железа (V_net)
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        v_exc_1 = calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        v_exc_2 = calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - v_exc_1 - v_exc_2)
        
        return pd.Series([d_actual, v_net, r_cov1, r_cov2, interface_type, flex_score, True])
    except:
        return pd.Series([np.nan]*7)

@st.cache_data(show_spinner=False)
def load_base_data(file_path):
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path, compression='gzip')
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    df['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df.dropna(subset=['Actual_BDE_kJ']).copy()
    df_valid['Graph_Complexity'] = df_valid['molecule'].apply(get_graph_complexity)
    return df_valid[df_valid['Graph_Complexity'] > 0]

def compile_unit_test(df_tier, relax_coeff):
    start = time.time()
    
    df_tier[['d_actual', 'v_net', 'r1', 'r2', 'interface_type', 'flex_score', 'valid']] = df_tier.apply(analyze_v16, axis=1)
    df_tier = df_tier.dropna(subset=['valid']).copy()
    
    if len(df_tier) == 0: return df_tier, time.time() - start
        
    # ОНТОЛОГИЯ V16
    df_tier['Hardware_BDE'] = (df_tier['interface_type'] * STATIC_BASE_LOCK) + (VOLUME_BONUS * df_tier['v_net'])
    df_tier['Cashback'] = df_tier['flex_score'] * relax_coeff
    df_tier['Grid_BDE_Final'] = df_tier['Hardware_BDE'] - df_tier['Cashback']
    
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("🔗 V16.0: Индекс Аппаратной Жесткости")
st.markdown("Двойные/тройные связи — это блокираторы. Одинарные — шарниры, дающие кэшбек релаксации.")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Синхронизация с базой..."):
    df_
