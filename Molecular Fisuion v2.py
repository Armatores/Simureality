import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: AUTO-PATHFINDER V3 (LONE PAIR MATRIX INCLUDED)
# =====================================================================

st.set_page_config(page_title="Assembler V3: Jitter Tax", layout="wide", page_icon="⚡")

# --- ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ РЕШЕТКИ ---
GAMMA_SYS = 1.0418               
Z0 = 377.0                       
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             
K_THETA = 2.0                    
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
C_LP = 42.5                      # Константа Эфирного Джиттера (кДж за 1 конфликтную пару)

TARGET_MOLECULES = {
    "C": ("Метан (CH4)", 1660.0),
    "O": ("Вода (H2O)", 926.0),
    "N#N": ("Азот (N2)", 945.0),
    "O=O": ("Кислород (O2)", 498.0),
    "O=C=O": ("Углекислый газ (CO2)", 1608.0),
    "CC": ("Этан (C2H6)", 2826.0),
    "C=C": ("Этилен (C2H4)", 2253.0),
    "C#C": ("Ацетилен (C2H2)", 1644.0),
    "N": ("Аммиак (NH3)", 1170.0),
    "CO": ("Метанол (CH3OH)", 2038.0),
    "[C-]#[O+]": ("Угарный газ (CO)", 1076.0),
    "C#N": ("Синильная кислота (HCN)", 1305.0),
    "[HH]": ("Водород (H2)", 436.0),
    "FF": ("Фтор (F2)", 158.0),
    "ClCl": ("Хлор (Cl2)", 242.0),
    "F": ("Фтороводород (HF)", 568.0),
    "C=O": ("Формальдегид (CH2O)", 1503.0),
    "N=[N+]=[O-]": ("Закись азота (N2O)", 1045.0),
    "C1CC1": ("Циклопропан (C3H6)", 3400.0), 
    "C1=CC=CC=C1": ("Бензол (C6H6)", 5535.0)  
}

def get_lone_pairs(atomic_num):
    """Определяет количество открытых портов (Lone Pairs) по номеру узла"""
    if atomic_num in [9, 17, 35, 53]: return 3  # Галогены
    if atomic_num in [8, 16, 34]: return 2      # Халькогены
    if atomic_num in [7, 15]: return 1          # Пниктогены
    return 0                                    # Углерод, Водород и т.д.

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2)**3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def get_angular_tension(mol_h, conf):
    total_tension = 0.0
    for atom in mol_h.GetAtoms():
        neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
        if len(neighbors) >= 2:
            pos_c = np.array(conf.GetAtomPosition(atom.GetIdx()))
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
            
            deformation = abs(max_angle - 109.47)
            total_tension += K_THETA * deformation
    return total_tension

def auto_assemble_molecule(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0: return None
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    total_hw = 0.0
    total_repulsion = 0.0

    # 1. Сканируем интерфейсы
    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        bo = bond.GetBondTypeAsDouble()
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        
        r_cov1, r_cov2 = pt.GetRcovalent(a1.GetAtomicNum()), pt.GetRcovalent(a2.GetAtomicNum())
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS) - calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS))
        
        # Хардверный профит и системный налог
        raw_hw = (bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
        tax_sys = raw_hw * (GAMMA_SYS - 1.0)
        total_hw += (raw_hw - tax_sys)

        # РАСЧЕТ ЭФИРНОГО ДЖИТТЕРА (Port Repulsion)
        lp1 = get_lone_pairs(a1.GetAtomicNum())
        lp2 = get_lone_pairs(a2.GetAtomicNum())
        total_repulsion += C_LP * (lp1 * lp2)

    # 2. Глобальный налог на деформацию (Angular Tension)
    total_tension = get_angular_tension(mol_h, conf)

    # 3. Субсидия Изоляции
    final_cashback = (Z0 / 2.0) 

    # 4. Итоговый баланс: Профит - Деформация - Джиттер + Изоляция
    sigma_k = total_hw - total_tension - total_repulsion + final_cashback
    return sigma_k

# --- UI ---
st.title("⚡ Auto-Assembler V3.0: Lone Pair Matrix")
st.markdown("Внедрен алгоритм `Port Repulsion Tax` для расчета эфирного джиттера открытых портов (свободных электронных пар).")

if st.button("🚀 Компилировать 20 Графов"):
    results = []
    progress_bar = st.progress(0)
    
    items = list(TARGET_MOLECULES.items())
    for idx, (smiles, (name, exp_energy)) in enumerate(items):
        pred_energy = auto_assemble_molecule(smiles)
        if pred_energy is not None:
            accuracy = max(0, 100 - (abs(pred_energy - exp_energy) / exp_energy * 100))
            results.append({
                "SMILES": smiles,
                "Молекула": name,
                "ΣK_pred": pred_energy,
                "ΣK_exp": exp_energy,
                "Точность (%)": accuracy
            })
        progress_bar.progress((idx + 1) / len(items))
        
    df_res = pd.DataFrame(results)
    st.dataframe(df_res.style.format({
        "ΣK_pred": "{:.1f}", 
        "ΣK_exp": "{:.1f}", 
        "Точность (%)": "{:.2f}%"
    }), use_container_width=True)
    
    mean_acc = df_res['Точность (%)'].mean()
    st.success(f"**Средняя точность: {mean_acc:.2f}%**")
