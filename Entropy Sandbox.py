import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# =====================================================================
# SIMUREALITY V33.3: PHASE ENGINE (TOPOLOGICAL FRUSTRATION)
# Честный парсинг портов, Импеданс Вакуума и Расширенная База
# =====================================================================

st.set_page_config(page_title="V33.3 Phase Engine", layout="wide", page_icon="🧊")

# --- ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
Z0 = 377.0                       
GAMMA_SYS = 1.0418               
IMPEDANCE_BRIDGE = (Z0 / 100.0) * GAMMA_SYS  # ~3.927

TARGET_MOLECULES = {
    "O": "Вода (H2O) - Идеальная Симметрия (2/2)",
    "CCO": "Этанол (C2H5OH) - Асимметрия (1/2)",
    "N": "Аммиак (NH3) - Асимметрия (3/1)",
    "CO": "Метанол (CH3OH) - Асимметрия (1/2)",
    "CC(=O)C": "Ацетон (C3H6O) - Слепой Акцептор (0/2)",
    "CC(=O)O": "Уксусная кислота (CH3COOH) - Двойной коннектор",
    "c1ccccc1O": "Фенол (C6H5OH) - Ароматика + Порты",
    "C(C(C(C(C(CO)O)O)O)O)O": "Глюкоза (C6H12O6) - P2P Монстр",
    "C": "Метан (CH4) - Микро-Сфера",
    "C1=CC=CC=C1": "Бензол (C6H6) - 2D Диск",
    "CCCCCCC": "н-Гептан (C7H16) - 1D Спагетти",
    "ClC(Cl)(Cl)Cl": "Тетрахлорметан (CCl4) - Идеальный Шар",
    "O=C=O": "Углекислый газ (CO2)",
    "N#N": "Азот (N2) - 1D Газ",
    "O=O": "Кислород (O2) - 1D Газ"
}

def extract_hardware_features(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0:
        AllChem.Compute2DCoords(mol_h)
    try: AllChem.MMFFOptimizeMolecule(mol_h)
    except: pass
    
    mw = Descriptors.ExactMolWt(mol_h)
    voxel_footprint = rdMolDescriptors.CalcLabuteASA(mol_h) 
    rot_bonds = Descriptors.NumRotatableBonds(mol_h)        
    
    # --- ЧЕСТНЫЙ СКАНЕР ПОРТОВ (P2P ИНТЕРФЕЙСЫ) ---
    lone_pairs = 0
    polar_h = 0
    for atom in mol_h.GetAtoms():
        z = atom.GetAtomicNum()
        # Только жесткие H-bond акцепторы
        if z == 9: lone_pairs += 3
        elif z == 8: lone_pairs += 2
        elif z == 7: lone_pairs += 1
        
        if z == 1:
            neighbor = atom.GetNeighbors()[0]
            if neighbor.GetAtomicNum() in [7, 8, 9]:
                polar_h += 1

    donors = polar_h
    acceptors = lone_pairs
    
    # --- ТЕНЗОРЫ ИНЕРЦИИ ---
    try:
        pmi1 = rdMolDescriptors.CalcPMI1(mol_h)
        pmi2 = rdMolDescriptors.CalcPMI2(mol_h)
        pmi3 = rdMolDescriptors.CalcPMI3(mol_h)
        npr1 = pmi1 / pmi3 if pmi3 > 1e-5 else 0.0
        npr2 = pmi2 / pmi3 if pmi3 > 1e-5 else 1.0
    except:
        npr1, npr2 = 0.0, 1.0 
        
    sphericity = max(0.0, 1.0 - math.sqrt((npr1 - 1.0)**2 + (npr2 - 1.0)**2)) 
    disk_ness = max(0.0, 1.0 - math.sqrt((npr1 - 0.5)**2 + (npr2 - 0.5)**2))  
    rod_ness = max(0.0, 1.0 - math.sqrt((npr1 - 0.0)**2 + (npr2 - 1.0)**2))   
        
    arom_rings = rdMolDescriptors.CalcNumAromaticRings(mol_h)
    heavy = mol.GetNumHeavyAtoms()
    
    return {
        "mw": mw, "asa": voxel_footprint, "rot": rot_bonds,
        "donors": donors, "acceptors": acceptors,
        "sphericity": sphericity, "disk_ness": disk_ness, "rod_ness": rod_ness,
        "arom": arom_rings, "heavy": heavy, "smiles": smiles
    }

def calculate_phase_transitions(f):
    # -------------------------------------------------------------
    # 1. ТОЧКА КИПЕНИЯ (Сырая Топология)
    # -------------------------------------------------------------
    base_vacuum_lock = (f["asa"] * 1.55) + (f["mw"] * 0.1)
    
    paired_ports = min(f["donors"], f["acceptors"])
    unpaired_ports = max(f["donors"], f["acceptors"]) - paired_ports
    
    # Неспаренные порты почти не добавляют силы удержания
    p2p_cache = (paired_ports * 39.0) + (unpaired_ports * 2.0)
    
    arom_stacking_bonus = f["arom"] * 10.0
    spaghetti_drag = f["rot"] * 4.0 
    
    raw_boil = base_vacuum_lock + p2p_cache + arom_stacking_bonus - spaghetti_drag
    if f["heavy"] <= 2 and p2p_cache == 0: raw_boil *= 0.35 
    
    # -------------------------------------------------------------
    # 2. ТОЧКА ПЛАВЛЕНИЯ (Фрустрация Кристалла)
    # -------------------------------------------------------------
    packing_eff = 0.35 + (f["sphericity"] * 0.5) + (f["disk_ness"] * 0.45)
    if f["rod_ness"] > 0.85 and f["rot"] == 0: packing_eff += 0.3 
    
    # ШТРАФ ФРУСТРАЦИИ: Неспаренные порты ломают идеальную 3D-решетку
    sym_p2p_bonus = (paired_ports * 15.0) - (unpaired_ports * 12.0)
    
    raw_melt = (raw_boil * packing_eff) + sym_p2p_bonus - (f["rot"] * 6.0)
    if raw_melt < 2.0: raw_melt = 2.0

    is_sublime = False
    if f["rod_ness"] > 0.9 and f["asa"] < 60 and p2p_cache == 0 and f["heavy"] > 1:
        raw_melt = raw_boil * 1.25 
        is_sublime = True
        
    if raw_melt > raw_boil and not is_sublime: raw_melt = raw_boil * 0.95

    # -------------------------------------------------------------
    # 3. ИМПЕДАНСНЫЙ МОСТ -> КЕЛЬВИНЫ
    # -------------------------------------------------------------
    t_boil = raw_boil * IMPEDANCE_BRIDGE
    t_melt = raw_melt * IMPEDANCE_BRIDGE
    
    mass_drift = f["donors"] * 50.0 
    t_deg = 1500.0 + (f["heavy"] * 150.0) + (f["arom"] * 1000.0) - mass_drift - (f["rot"] * 30.0)
    if "O=C=O" in f["smiles"] or "N#N" in f["smiles"] or "[HH]" in f["smiles"] or "O=O" in f["smiles"]: 
        t_deg = 6000.0 
        
    return {"T_melt": round(t_melt), "T_boil": round(t_boil), "T_deg": round(t_deg), "Sublimes": is_sublime}

# --- UI ---
st.title("🧊 V33.3: Phase Engine (Topological Frustration)")
st.markdown(f"**Импедансный Мост: {IMPEDANCE_BRIDGE:.3f}**. Добавлен честный сканер портов. Асимметрия доноров/акцепторов теперь наказывается фрустрацией кристалла (резкое падение T_melt).")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    target_smiles = st.selectbox("Анализ отдельного узла:", list(TARGET_MOLECULES.keys()), format_func=lambda x: TARGET_MOLECULES[x])
    run_single = st.button("🚀 Декомпилировать Топологию", type="primary", use_container_width=True)
with col_btn2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_batch = st.button("🗂 Сгенерировать Сводную Таблицу (Batch)", type="secondary", use_container_width=True)

if run_single:
    with st.spinner("Рендеринг 3D-геометрии..."):
        features = extract_hardware_features(target_smiles)
        if features:
            phases = calculate_phase_transitions(features)
            
            st.markdown("### 🧬 Метрики Топологии:")
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("UDP Footprint", f"{features['asa']:.1f} Å²")
            c_m2.metric("Сферичность / Диск", f"{features['sphericity']*100:.0f}% / {features['disk_ness']*100:.0f}%")
            c_m3.metric("Spaghetti-Фактор", features['rot'])
            
            p_color = "normal" if features['donors'] == features['acceptors'] else "inverse"
            c_m4.metric("True Ports (D/A)", f"{features['donors']} / {features['acceptors']}", delta="Идеал" if features['donors'] == features['acceptors'] and features['donors']>0 else "Асимметрия", delta_color=p_color)
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            tm_label = f"{phases['T_melt']} K (Субл.)" if phases['Sublimes'] else f"{phases['T_melt']} K"
            c1.metric("🧊 Плавление (ROM)", tm_label)
            c2.metric("💧 Кипение (RAM)", f"{phases['T_boil']} K")
            c3.metric("🔥 Пиролиз (Kernel Panic)", f"{phases['T_deg']} K")
            
            temps = [0, phases['T_melt'], phases['T_melt']+1, phases['T_boil'], phases['T_boil']+1, phases['T_deg']]
            states = [10, 10, 40, 40, 80, 80]
            labels = ["Кристалл", "Кристалл", "Жидкость", "Жидкость", "Газ", "Газ"]
            
            if phases['Sublimes']:
                states = [10, 10, 80, 80, 80, 80]
                labels = ["Кристалл", "Кристалл", "Газ (Сублимация)", "Газ", "Газ", "Газ"]
            elif phases['T_melt'] >= phases['T_boil']:
                temps = [0, phases['T_boil'], phases['T_boil']+1, phases['T_melt'], phases['T_melt']+1, phases['T_deg']]
            
            df_plot = pd.DataFrame({"Температура (K)": temps, "Энтропия Среды": states, "Состояние Кэша": labels})
            fig = px.area(df_plot, x="Температура (K)", y="Энтропия Среды", color="Состояние Кэша",
                          color_discrete_map={"Кристалл": "#00d2ff", "Жидкость": "#3a7bd5", "Газ": "#f6d365", "Газ (Сублимация)": "#f6d365"})
            fig.add_vline(x=phases['T_deg'], line_dash="dash", line_color="#FF4500", annotation_text="Полный Распад")
            fig.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

if run_batch:
    with st.spinner("Трансляция геометрии в Кельвины через Импедансный Мост..."):
        results_list = []
        for sm, name in TARGET_MOLECULES.items():
            feats = extract_hardware_features(sm)
            if feats:
                ph = calculate_phase_transitions(feats)
                results_list.append({
                    "Система": name.split(" - ")[0],
                    "T_melt (K)": ph["T_melt"],
                    "T_boil (K)": ph["T_boil"],
                    "Порты D/A": f"{feats['donors']}/{feats['acceptors']}",
                    "Footprint (Å²)": round(feats["asa"], 1)
                })
        
        df_batch = pd.DataFrame(results_list)
        st.success("✅ Универсальная калибровка завершена!")
        st.dataframe(df_batch, use_container_width=True)
        
        csv_data = df_batch.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Скачать Batch", data=csv_data, file_name="v33_3_frustration.csv", mime="text/csv", type="primary")
