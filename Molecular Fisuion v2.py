import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: AUTO-PATHFINDER V6 (TERMINATOR ONTOLOGY)
# =====================================================================

st.set_page_config(page_title="Assembler V6: Terminator Rule", layout="wide", page_icon="🛑")

GAMMA_SYS = 1.0418               
Z0 = 377.0                       
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             
K_THETA = 2.0                    
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
C_LP = 12.5                      # Базовый штраф за коллизию ОДНОЙ пары портов

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
    "BrBr": ("Бром (Br2)", 193.0),
    "II": ("Иод (I2)", 151.0),
    "F": ("Фтороводород (HF)", 568.0),
    "C=O": ("Формальдегид (CH2O)", 1503.0),
    "N=[N+]=[O-]": ("Закись азота (N2O)", 1045.0),
    "C1CC1": ("Циклопропан (C3H6)", 3400.0), 
    "C1=CC=CC=C1": ("Бензол (C6H6)", 5535.0),
    "Cl": ("Хлороводород (HCl)", 431.0),
    "FC(F)(F)F": ("Тетрафторметан (CF4)", 1950.0),
    "S": ("Сероводород (H2S)", 730.0),
    "P": ("Фосфин (PH3)", 960.0),
    "S=C=S": ("Сероуглерод (CS2)", 1150.0),
    "CCO": ("Этанол (C2H5OH)", 3220.0),
    "COC": ("Диметиловый эфир", 3180.0),
    "CCC": ("Пропан (C3H8)", 4000.0),
    "C=CC": ("Пропен (C3H6)", 3430.0),
    "C#CC": ("Пропин (C3H4)", 2820.0),
    "CC(=O)C": ("Ацетон (C3H6O)", 3900.0),
    "C1CCCC1": ("Циклопентан (C5H10)", 5600.0),
    "CC1=CC=CC=C1": ("Толуол (C7H8)", 6700.0),
    "CNC": ("Диметиламин", 2800.0),
    "CS": ("Метантиол (CH3SH)", 1880.0),
    "[N]=O": ("Оксид азота(II) (NO)", 630.0),
    "[O-][N+]=O": ("Диоксид азота (NO2)", 934.0),
    "C(Cl)(Cl)(Cl)Cl": ("Тетрахлорметан", 1300.0)
}

def get_lone_pairs(atomic_num):
    if atomic_num in [9, 17, 35, 53]: return 3  
    if atomic_num in [8, 16, 34]: return 2      
    if atomic_num in [7, 15]: return 1          
    return 0                                    

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
            total_tension += K_THETA * abs(max_angle - 109.47)
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

    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
        bo = bond.GetBondTypeAsDouble()
        
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        r_cov1, r_cov2 = pt.GetRcovalent(z1), pt.GetRcovalent(z2)
        
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        exc1 = 0.0 if z1 == 1 else calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        exc2 = 0.0 if z2 == 1 else calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - exc1 - exc2)
        
        # ОНТОЛОГИЯ ТЕРМИНАТОРОВ: Если оба узла - галогены (1 порт), Базовый Замок не выдается
        is_term1 = z1 in [9, 17, 35, 53]
        is_term2 = z2 in [9, 17, 35, 53]
        base_lock = 0.0 if (is_term1 and is_term2) else STATIC_BASE_LOCK
        
        raw_hw = (bo * base_lock) + (VOLUME_BONUS * v_net)
        tax_sys = raw_hw * (GAMMA_SYS - 1.0)
        total_hw += (raw_hw - tax_sys)

        # ГЕОМЕТРИЧЕСКИЙ CUTOFF ДЖИТТЕРА: Начисляется только если порты протыкают друг друга
        if d_actual < BUFFER_RADIUS:
            lp1, lp2 = get_lone_pairs(z1), get_lone_pairs(z2)
            total_repulsion += C_LP * (lp1 * lp2)

    total_tension = get_angular_tension(mol_h, conf)
    
    # Водород не получает субсидию изоляции (у него нет внутренних оболочек для маршрутизации)
    heavy_atoms = mol_h.GetNumHeavyAtoms()
    final_cashback = (Z0 / 2.0) if heavy_atoms > 0 else 0.0

    sigma_k = total_hw - total_tension - total_repulsion + final_cashback
    return sigma_k

# --- UI ---
st.title("🛑 Auto-Assembler V6.0: Terminator Ontology")
st.markdown("Внедрено Правило Терминаторов для Галогенов и геометрический Cutoff барьер ($1.6625$ Å) для эфирного джиттера.")

if st.button("🚀 Компилировать Матрицу"):
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
    }), height=600, use_container_width=True)
