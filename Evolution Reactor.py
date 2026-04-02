import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: V29.0 BATCH COMPILER (STREAMLIT UI)
# Термодинамический стресс-тест для 50 узлов
# =====================================================================

st.set_page_config(page_title="V29.0 Batch Compiler", layout="wide", page_icon="🧬")

# --- СИСТЕМНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
GAMMA_SYS = 1.0418               
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2
C_LP_CLASH = 30.0                
Z0 = 377.0                       
K_THETA = 2.0

# 50 ИНФОРМАЦИОННЫХ СИСТЕМ
TARGET_MOLECULES = {
    "[HH]": "Водород (H2)", "O=O": "Кислород (O2)", "N#N": "Азот (N2)",
    "FF": "Фтор (F2)", "ClCl": "Хлор (Cl2)", "BrBr": "Бром (Br2)", "II": "Иод (I2)",
    "O=C=O": "Углекислый газ (CO2)", "[C-]#[O+]": "Угарный газ (CO)",
    "C": "Метан (CH4)", "CC": "Этан (C2H6)", "CCC": "Пропан (C3H8)", 
    "CCCC": "Бутан (C4H10)", "CCCCC": "Пентан (C5H12)", "CC(C)C": "Изобутан",
    "C=C": "Этилен (C2H4)", "C=CC": "Пропен (C3H6)", "C#C": "Ацетилен (C2H2)",
    "O": "Вода (H2O)", "CO": "Метанол (CH3OH)", "CCO": "Этанол (C2H5OH)", 
    "CCCO": "Пропанол", "COC": "Диметиловый эфир",
    "C=O": "Формальдегид (CH2O)", "CC=O": "Ацетальдегид", "CC(=O)C": "Ацетон",
    "O=CO": "Муравьиная кислота", "CC(=O)O": "Уксусная кислота",
    "N": "Аммиак (NH3)", "CN": "Метиламин", "CNC": "Диметиламин", 
    "C#N": "Синильная кислота (HCN)", "N=[N+]=[O-]": "Закись азота (N2O)",
    "S": "Сероводород (H2S)", "CS": "Метантиол", "S=C=S": "Сероуглерод (CS2)",
    "F": "Фтороводород (HF)", "Cl": "Хлороводород (HCl)", "Br": "Бромоводород (HBr)",
    "CCl": "Хлорметан", "C(Cl)(Cl)(Cl)Cl": "Тетрахлорметан (CCl4)", "FC(F)(F)F": "Тетрафторметан (CF4)",
    "C1CC1": "Циклопропан (C3H6)", "C1CCC1": "Циклобутан (C4H8)", 
    "C1CCCC1": "Циклопентан (C5H10)", "C1CCCCC1": "Циклогексан (C6H12)",
    "C1=CC=CC=C1": "Бензол (C6H6)", "CC1=CC=CC=C1": "Толуол", 
    "Oc1ccccc1": "Фенол", "Nc1ccccc1": "Анилин", "c1ccncc1": "Пиридин"
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
    h1, h2 = r1 - d1, r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def get_ideal_angle(hyb):
    if hyb == Chem.rdchem.HybridizationType.SP: return 180.0
    if hyb == Chem.rdchem.HybridizationType.SP2: return 120.0
    return 109.47

def evaluate_lifecycle_tick(smiles, T_sys):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return 0.0, "Error"
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0: return 0.0, "Error"
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    total_hw, total_repulsion, total_desync, total_pi_strain = 0.0, 0.0, 0.0, 0.0
    active_bonds = 0
    is_aromatic = any(atom.GetIsAromatic() for atom in mol_h.GetAtoms())

    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
        bo = bond.GetBondTypeAsDouble()
        
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_base = np.linalg.norm(pos1 - pos2)
        
        mass1 = pt.GetAtomicWeight(z1) if z1 != 1 else 1.008
        mass2 = pt.GetAtomicWeight(z2) if z2 != 1 else 1.008
        reduced_mass = (mass1 * mass2) / (mass1 + mass2)
        mass_asym = abs(mass1 - mass2) / (mass1 + mass2)
        
        thermal_stretch = 1.0 + ((T_sys / 3500.0) / math.sqrt(reduced_mass))
        d_actual = d_base * thermal_stretch
        
        if d_actual >= VACUUM_GATE: continue
            
        active_bonds += 1
        r_cov1, r_cov2 = pt.GetRcovalent(z1), pt.GetRcovalent(z2)
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        exc1 = 0.0 if z1 == 1 else calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        exc2 = 0.0 if z2 == 1 else calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - exc1 - exc2)
        
        raw_hw = (bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
        total_hw += raw_hw * GAMMA_SYS

        lp1, lp2 = get_lone_pairs(z1), get_lone_pairs(z2)
        if lp1 > 0 and lp2 > 0:
            base_clash = (C_LP_CLASH * lp1 * lp2) / d_actual
            total_repulsion += base_clash * (1.0 + (T_sys / 1200.0)**1.2)

        if mass_asym > 0.5:
            total_desync += bo * (mass_asym * 120.0) * (T_sys / 1000.0)**1.5
        else:
            total_desync += bo * 15.0 * (T_sys / 1000.0)**1.2

        if not is_aromatic:
            if bo == 2.0: total_pi_strain += 78.1 * (1.0 + (T_sys / 1500.0))
            elif bo == 3.0: total_pi_strain += 199.5 * (1.0 + (T_sys / 1500.0))

    if active_bonds == 0: return 0.0, "💥 KERNEL PANIC"

    total_tension = 0.0
    for atom in mol_h.GetAtoms():
        hyb = atom.GetHybridization()
        ideal_angle = get_ideal_angle(hyb)
        neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
        if len(neighbors) >= 2:
            pos_c = np.array(conf.GetAtomPosition(atom.GetIdx()))
            max_dev = 0.0
            for i in range(len(neighbors)):
                for j in range(i+1, len(neighbors)):
                    v1, v2 = np.array(conf.GetAtomPosition(neighbors[i])) - pos_c, np.array(conf.GetAtomPosition(neighbors[j])) - pos_c
                    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if n1 != 0 and n2 != 0:
                        val = max(-1.0, min(1.0, np.dot(v1, v2) / (n1 * n2)))
                        angle = math.degrees(math.acos(val))
                        dev = abs(angle - ideal_angle)
                        if dev > max_dev: max_dev = dev
            total_tension += K_THETA * max_dev * (1.0 + (T_sys / 2000.0))

    global_bonus = 0.0
    if is_aromatic: global_bonus += 210.0                 
    if "O=C=O" in smiles.upper(): global_bonus += 250.0   
    if "N#N" in smiles.upper(): global_bonus += 150.0     
    if mol_h.GetNumHeavyAtoms() > 0: global_bonus += (Z0 / 2.0)

    sigma_k = total_hw + global_bonus - total_repulsion - total_tension - total_pi_strain - total_desync
    
    if sigma_k <= 0: return 0.0, "🔥 РАСПАД"
    return sigma_k, "✅ СТАБИЛЬНО"

# --- UI RENDERING ---
st.title("🧬 V29.0: Global Batch Compiler")
st.markdown("Потоковый анализ 50 топологических узлов. Расчет базового профита (0 K) и точки распада ($T_{deg}$) через деградацию TCP-связей и рассинхронизацию масс (Clock Drift).")

if st.button("🚀 Начать пакетную компиляцию (50 макро-графов)", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    total_items = len(TARGET_MOLECULES)
    
    for idx, (smiles, name) in enumerate(TARGET_MOLECULES.items()):
        status_text.text(f"Компиляция: {name} ({idx+1}/{total_items})")
        
        e_0k, stat_0k = evaluate_lifecycle_tick(smiles, 0)
        
        if "Error" in stat_0k:
            results.append({
                "Информационная Система": name,
                "ΣK (0 K) кДж": "ERROR",
                "T_deg (Пиролиз)": "ERROR",
                "Статус Матрицы": "Сбой 3D-матрицы RDKit"
            })
            progress_bar.progress((idx + 1) / total_items)
            continue
            
        t_deg = "Бессмертна (>6000K)"
        final_stat = "Архив Матрицы (Железный Пик)"
        
        for t in range(100, 6100, 100):
            e_t, stat_t = evaluate_lifecycle_tick(smiles, t)
            if "PANIC" in stat_t or "РАСПАД" in stat_t:
                t_deg = f"{t} K"
                if t < 1500: final_stat = "Хрупкая (DDoS / Clock Drift)"
                elif t < 3500: final_stat = "Органика (Сгорает при перегрузке)"
                else: final_stat = "Термостойкий каркас"
                break
                
        results.append({
            "Информационная Система": name,
            "ΣK (0 K) кДж": f"{e_0k:.1f}",
            "T_deg (Пиролиз)": t_deg,
            "Статус Матрицы": final_stat
        })
        
        progress_bar.progress((idx + 1) / total_items)
        
    status_text.text("✅ Компиляция успешно завершена.")
    
    df_results = pd.DataFrame(results)
    
    def color_matrix_status(row):
        stat = str(row['Статус Матрицы'])
        if 'Хрупкая' in stat:
            return ['background-color: #ffe6e6'] * len(row)
        elif 'Архив' in stat:
            return ['background-color: #e6ffe6'] * len(row)
        else:
            return [''] * len(row)
            
    st.dataframe(
        df_results.style.apply(color_matrix_status, axis=1),
        use_container_width=True,
        height=600
    )
    
    csv_data = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Скачать полный лог (CSV)",
        data=csv_data,
        file_name="v29_batch_results.csv",
        mime="text/csv"
    )
