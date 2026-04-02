import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: BATCH TEST V2.0 (FUNDAMENTAL GEOMETRY)
# =====================================================================

GAMMA_SYS = 1.0418               
Z0 = 377.0                       
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             
K_THETA = 2.0                    
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2)**3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def get_geometric_angle(mol_h, conf, atom_idx, bo):
    atom = mol_h.GetAtomWithIdx(atom_idx)
    neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
    
    if len(neighbors) >= 2:
        pos_c = np.array(conf.GetAtomPosition(atom_idx))
        max_angle = 109.47 
        for i in range(len(neighbors)):
            for j in range(i+1, len(neighbors)):
                v1 = np.array(conf.GetAtomPosition(neighbors[i])) - pos_c
                v2 = np.array(conf.GetAtomPosition(neighbors[j])) - pos_c
                n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                if n1 == 0 or n2 == 0: continue
                val = max(-1.0, min(1.0, np.dot(v1, v2) / (n1 * n2)))
                angle = math.degrees(math.acos(val))
                if angle > max_angle: max_angle = angle
        return max_angle
    else:
        if bo >= 3.0: return 180.0
        elif bo >= 2.0: return 120.0
        else: return 109.47

def evaluate_transaction_v2(smiles, target_bond_indices, N_ext):
    mol = Chem.MolFromSmiles(smiles)
    mol_h = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol_h, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    idx1, idx2 = target_bond_indices
    a1, a2 = mol_h.GetAtomWithIdx(idx1), mol_h.GetAtomWithIdx(idx2)
    bo = mol_h.GetBondBetweenAtoms(idx1, idx2).GetBondTypeAsDouble()

    pos1, pos2 = np.array(conf.GetAtomPosition(idx1)), np.array(conf.GetAtomPosition(idx2))
    d_actual = np.linalg.norm(pos1 - pos2)
    
    r_cov1, r_cov2 = pt.GetRcovalent(a1.GetAtomicNum()), pt.GetRcovalent(a2.GetAtomicNum())
    v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
    v_net = max(0.0, v_total_buf - calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS) - calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS))

    raw_hw = (bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
    tax_sys = raw_hw * (GAMMA_SYS - 1.0)
    
    ang1 = get_geometric_angle(mol_h, conf, idx1, bo)
    ang2 = get_geometric_angle(mol_h, conf, idx2, bo)
    max_deformation = max(abs(ang1 - 109.47), abs(ang2 - 109.47))
    tax_tension = K_THETA * max_deformation
    
    cashback_iso = (Z0 / 2.0) * math.exp(-N_ext)
    
    total_energy = raw_hw - tax_sys - tax_tension + cashback_iso
    
    return {"bo": bo, "hw": raw_hw, "tax": tax_tension, "sys": tax_sys, "iso": cashback_iso, "total": total_energy}

# --- МАРШРУТЫ СБОРКИ (HARDCODED ДЛЯ ТЕСТА) ---
def run_batch_test():
    results = []

    # 1. МЕТАН (CH4) - Пошаговая сборка 4 связей
    ch4_total = 0.0
    for step in range(4):
        # N_ext для промежуточных радикалов гасит субсидию
        res = evaluate_transaction_v2("C", (0, step+1), N_ext=abs(3-step)) 
        ch4_total += res['total']
    results.append({"Молекула": "CH₄ (Метан)", "ΣK_pred": ch4_total, "ΣK_exp": 1660.0})

    # 2. ВОДА (H2O) - Пошаговая сборка 2 связей
    h2o_total = 0.0
    res1 = evaluate_transaction_v2("[OH]", (0, 1), N_ext=1) # OH радикал
    res2 = evaluate_transaction_v2("O", (0, 2), N_ext=0)    # Вторая связь закрывает систему
    h2o_total = res1['total'] + res2['total']
    results.append({"Молекула": "H₂O (Вода)", "ΣK_pred": h2o_total, "ΣK_exp": 926.0})

    # 3. АЗОТ (N2) - Одношаговая сборка ядра
    res_n2 = evaluate_transaction_v2("N#N", (0, 1), N_ext=0)
    results.append({"Молекула": "N₂ (Азот)", "ΣK_pred": res_n2['total'], "ΣK_exp": 945.0})

    return pd.DataFrame(results)

st.title("🧪 Пакетный Краш-Тест V2.0")
st.markdown("Валидация геометрического ядра на предельных состояниях ГЦК-решетки.")

if st.button("Запустить Калибровку"):
    with st.spinner("Синтезируем тестовые графы..."):
        df_res = run_batch_test()
        df_res['Точность (%)'] = 100 - (abs(df_res['ΣK_pred'] - df_res['ΣK_exp']) / df_res['ΣK_exp'] * 100)
        
    st.dataframe(df_res.style.format({"ΣK_pred": "{:.1f}", "ΣK_exp": "{:.1f}", "Точность (%)": "{:.1f}%"}), use_container_width=True)
    
    st.info("Ожидаемое поведение: У Метана угловой штраф должен быть равен нулю. У Азота штраф и субсидия должны компенсировать друг друга.")
