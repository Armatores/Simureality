import streamlit as st
import pandas as pd
import numpy as np
import math
import os
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# V30.1: LIFECYCLE BATCH COMPILER (GZIP DB ENGINE)
# =====================================================================

st.set_page_config(page_title="V30.1 Lifecycle Compiler", layout="wide", page_icon="🗄️")

# --- КОНСТАНТЫ ---
GAMMA_SYS = 1.0418               
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2
C_LP_CLASH = 30.0                
Z0 = 377.0                       
K_THETA = 2.0
FILE_NAME = "bde-db2.csv.gz"

def get_graph_complexity(smiles):
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        return mol.GetNumBonds() if mol else -1
    except:
        return -1

@st.cache_data(show_spinner=False)
def load_and_prepare_db(file_path):
    if not os.path.exists(file_path): return None
    
    # Парсинг аналогично V20.0
    df = pd.read_csv(file_path, compression='gzip')
    df['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df.dropna(subset=['Actual_BDE_kJ']).copy()
    
    # Для стресс-теста нужны только уникальные макро-графы
    unique_mols = df_valid[['molecule']].drop_duplicates()
    unique_mols['Graph_Complexity'] = unique_mols['molecule'].apply(get_graph_complexity)
    
    return unique_mols[unique_mols['Graph_Complexity'] > 0]

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

# --- UI ---
st.title("🗄️ V30.1: GZIP Database Lifecycle Engine")

with st.spinner("Чтение и распаковка bde-db2.csv.gz..."):
    df_base = load_and_prepare_db(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    st.success(f"✅ База загружена. Уникальных макро-графов: {len(df_base)}")
    
    col_ui1, col_ui2 = st.columns(2)
    with col_ui1:
        target_bonds = st.slider("Сложность графа (Кол-во связей)", 1, max_bonds, 2, step=1)
    with col_ui2:
        batch_size = st.slider("Размер батча (случайная выборка)", 5, 200, 20, step=5)
        
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    if st.button(f"🚀 Запустить стресс-тест для {min(batch_size, len(df_filtered))} узлов", type="primary"):
        if len(df_filtered) == 0:
            st.warning("Нет молекул с такой сложностью.")
        else:
            # Случайная выборка из отфильтрованного пула
            sample_df = df_filtered.sample(n=min(batch_size, len(df_filtered)))
            target_smiles = sample_df['molecule'].tolist()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            total_items = len(target_smiles)
            
            for idx, smiles in enumerate(target_smiles):
                status_text.text(f"Компиляция: {smiles} ({idx+1}/{total_items})")
                e_0k, stat_0k = evaluate_lifecycle_tick(smiles, 0)
                
                if "Error" in stat_0k:
                    results.append({"SMILES": smiles, "ΣK (0 K) кДж": "ERROR", "T_deg (Пиролиз)": "ERROR", "Статус": "Сбой 3D-матрицы"})
                    progress_bar.progress((idx + 1) / total_items)
                    continue
                    
                t_deg = "Бессмертна (>6000K)"
                final_stat = "Архив (Железный Пик)"
                
                # Шаг 200 K для скорости
                for t in range(100, 6100, 200):
                    e_t, stat_t = evaluate_lifecycle_tick(smiles, t)
                    if "PANIC" in stat_t or "РАСПАД" in stat_t:
                        t_deg = f"{t} K"
                        if t < 1500: final_stat = "Хрупкая (DDoS / Drift)"
                        elif t < 3500: final_stat = "Органика (Сгорает)"
                        else: final_stat = "Термостойкий каркас"
                        break
                        
                results.append({"SMILES": smiles, "ΣK (0 K) кДж": f"{e_0k:.1f}", "T_deg (Пиролиз)": t_deg, "Статус": final_stat})
                progress_bar.progress((idx + 1) / total_items)
                
            status_text.text("✅ Вычислительный цикл завершен.")
            df_results = pd.DataFrame(results)
            
            def color_matrix_status(row):
                stat = str(row['Статус'])
                if 'Хрупкая' in stat: return ['background-color: #ffe6e6'] * len(row)
                elif 'Архив' in stat: return ['background-color: #e6ffe6'] * len(row)
                else: return [''] * len(row)
                    
            st.dataframe(df_results.style.apply(color_matrix_status, axis=1), use_container_width=True, height=600)
            
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(label="💾 Скачать выборку (CSV)", data=csv_data, file_name="v30_1_lifecycle_sample.csv", mime="text/csv")
else:
    st.error(f"Файл {FILE_NAME} не найден в директории.")
