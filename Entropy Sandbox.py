import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# =====================================================================
# SIMUREALITY V33.2: PHASE ENGINE (DIMENSIONAL CALIBRATION)
# Трансляция 3D-Топологии в Температуру через Импеданс Вакуума
# =====================================================================

st.set_page_config(page_title="V33.2 Phase Engine", layout="wide", page_icon="🧊")

# --- ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
Z0 = 377.0                       # Импеданс Вакуума (Ом)
GAMMA_SYS = 1.0418               # Системный Налог (Сопротивление ГЦК-решетки)
IMPEDANCE_BRIDGE = (Z0 / 100.0) * GAMMA_SYS  # Универсальный транслятор: Топология -> Температура (~3.927)

TARGET_MOLECULES = {
    "O": "Вода (H2O) - Идеальная P2P Сеть",
    "C": "Метан (CH4) - Микро-Сфера",
    "C1=CC=CC=C1": "Бензол (C6H6) - 2D Диск",
    "CCCCCCC": "н-Гептан (C7H16) - 1D Спагетти",
    "CC(C)(C)C(C)(C)C": "Гексаметилэтан (C8H18) - Макро-Сфера",
    "O=C=O": "Углекислый газ (CO2) - 1D Ось",
    "ClC(Cl)(Cl)Cl": "Тетрахлорметан (CCl4) - Идеальный Шар",
    "CCO": "Этанол (C2H5OH) - Асимметричная P2P",
    "N": "Аммиак (NH3)",
    "[HH]": "Водород (H2)",
    "F": "Фтороводород (HF)"
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
    
    donors = rdMolDescriptors.CalcNumLipinskiHBD(mol_h)
    acceptors = rdMolDescriptors.CalcNumLipinskiHBA(mol_h)
    
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
    # СЫРАЯ ТОПОЛОГИЯ (Аппаратный счетчик без температуры)
    # -------------------------------------------------------------
    base_vacuum_lock = (f["asa"] * 1.5) + (f["mw"] * 0.1)
    
    paired_ports = min(f["donors"], f["acceptors"])
    unpaired_ports = max(0, f["acceptors"] - f["donors"]) + max(0, f["donors"] - f["acceptors"])
    p2p_cache = (paired_ports * 60.0) + (unpaired_ports * 20.0)
    
    arom_stacking_bonus = f["arom"] * 15.0
    spaghetti_drag = f["rot"] * 4.0 
    
    raw_boil = base_vacuum_lock + p2p_cache + arom_stacking_bonus - spaghetti_drag
    if f["heavy"] <= 2 and p2p_cache == 0: raw_boil *= 0.4 # Защита сверхлегких симметричных узлов
    
    # Эффективность 3D упаковки
    packing_eff = 0.35 + (f["sphericity"] * 0.5) + (f["disk_ness"] * 0.45)
    if f["rod_ness"] > 0.85 and f["rot"] == 0: packing_eff += 0.3 
    
    # Кристаллический профит от P2P портов (Чем ближе к 1:1, тем крепче лед)
    port_ratio = (paired_ports / max(1, f["donors"] + f["acceptors"]))
    sym_p2p_bonus = port_ratio * 100.0
    
    raw_melt = (raw_boil * packing_eff) + sym_p2p_bonus - (f["rot"] * 10.0)
    if raw_melt < 2.0: raw_melt = 2.0

    is_sublime = False
    if f["rod_ness"] > 0.9 and f["asa"] < 60 and p2p_cache == 0 and f["heavy"] > 1:
        raw_melt = raw_boil * 1.25 
        is_sublime = True
        
    if raw_melt > raw_boil and not is_sublime: raw_melt = raw_boil * 0.95

    # -------------------------------------------------------------
    # ИМПЕДАНСНЫЙ МОСТ (Трансляция Топологии в Градусы Кельвина)
    # -------------------------------------------------------------
    t_boil = raw_boil * IMPEDANCE_BRIDGE
    t_melt = raw_melt * IMPEDANCE_BRIDGE
    
    # Пиролиз (Остается в сырых джоулях/кельвинах ковалентных связей)
    mass_drift = f["donors"] * 50.0 
    t_deg = 1500.0 + (f["heavy"] * 150.0) + (f["arom"] * 1000.0) - mass_drift - (f["rot"] * 30.0)
    if "O=C=O" in f["smiles"] or "N#N" in f["smiles"] or "[HH]" in f["smiles"]: t_deg = 6000.0 
        
    return {"T_melt": round(t_melt), "T_boil": round(t_boil), "T_deg": round(t_deg), "Sublimes": is_sublime}

# --- UI ---
st.title("🧊 V33.2: Impedance Calibrated Phase Engine")
st.markdown(f"Движок переводит сырую топологию графа в тепловой шум (Кельвин) через **Импеданс Вакуума (Z0 = 377 Ом)**. Множитель конвертации: **{IMPEDANCE_BRIDGE:.3f}**.")

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
            
            st.markdown("### 🧬 Метрики Топологии (ASA & Тензоры):")
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("UDP Footprint (ASA)", f"{features['asa']:.1f} Å
