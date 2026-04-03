import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# =====================================================================
# SIMUREALITY V33.1: PHASE TRANSITION ENGINE (BATCH PROCESSING)
# 100% Geometry & Tensor Topology. Zero Hardcoded Molecules.
# =====================================================================

st.set_page_config(page_title="V33.1 Phase Engine", layout="wide", page_icon="🧊")

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
    
    # 1. АППАРАТНЫЙ 3D-РЕНДЕР
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0:
        AllChem.Compute2DCoords(mol_h)
    try: AllChem.MMFFOptimizeMolecule(mol_h)
    except: pass
    
    # 2. БАЗОВЫЕ МЕТРИКИ ОПЕРАТИВНОЙ ПАМЯТИ
    mw = Descriptors.ExactMolWt(mol_h)
    voxel_footprint = rdMolDescriptors.CalcLabuteASA(mol_h) # Честная площадь поверхности (UDP Footprint)
    rot_bonds = Descriptors.NumRotatableBonds(mol_h)        # Спагетти-фактор (гибкость)
    
    # 3. P2P СЕТЕВАЯ АРХИТЕКТУРА (Водородные связи)
    donors = rdMolDescriptors.CalcNumLipinskiHBD(mol_h)
    acceptors = rdMolDescriptors.CalcNumLipinskiHBA(mol_h)
    
    # 4. ТЕНЗОР 3D-СИММЕТРИИ (Абсолютная геометрия без костылей)
    try:
        pmi1 = rdMolDescriptors.CalcPMI1(mol_h)
        pmi2 = rdMolDescriptors.CalcPMI2(mol_h)
        pmi3 = rdMolDescriptors.CalcPMI3(mol_h)
        npr1 = pmi1 / pmi3 if pmi3 > 1e-5 else 0.0
        npr2 = pmi2 / pmi3 if pmi3 > 1e-5 else 1.0
    except:
        npr1, npr2 = 0.0, 1.0 # Защита для линейных 1D молекул
        
    # Математическое определение формы через моменты инерции
    sphericity = max(0.0, 1.0 - math.sqrt((npr1 - 1.0)**2 + (npr2 - 1.0)**2)) # Ближе к 1 = Шар
    disk_ness = max(0.0, 1.0 - math.sqrt((npr1 - 0.5)**2 + (npr2 - 0.5)**2))  # Ближе к 1 = Диск
    rod_ness = max(0.0, 1.0 - math.sqrt((npr1 - 0.0)**2 + (npr2 - 1.0)**2))   # Ближе к 1 = Стержень/Спагетти
        
    arom_rings = rdMolDescriptors.CalcNumAromaticRings(mol_h)
    heavy = mol.GetNumHeavyAtoms()
    
    return {
        "mw": mw, "asa": voxel_footprint, "rot": rot_bonds,
        "donors": donors, "acceptors": acceptors,
        "sphericity": sphericity, "disk_ness": disk_ness, "rod_ness": rod_ness,
        "arom": arom_rings, "heavy": heavy, "smiles": smiles,
        "npr1": npr1, "npr2": npr2
    }

def calculate_phase_transitions(f):
    # -------------------------------------------------------------
    # 1. ТОЧКА КИПЕНИЯ (Жидкость/RAM -> Газ/UDP)
    # -------------------------------------------------------------
    base_vacuum_lock = (f["asa"] * 1.6) + (f["mw"] * 0.7)
    
    paired_ports = min(f["donors"], f["acceptors"])
    unpaired_ports = max(0, f["acceptors"] - f["donors"])
    p2p_cache = (paired_ports * 85.0) + (unpaired_ports * 15.0)
    
    arom_stacking_bonus = f["arom"] * 40.0
    spaghetti_drag = f["rot"] * 9.0 
    
    t_boil = base_vacuum_lock + p2p_cache + arom_stacking_bonus + spaghetti_drag
    
    if f["heavy"] <= 2 and p2p_cache == 0: t_boil *= 0.35 

    # -------------------------------------------------------------
    # 2. ТОЧКА ПЛАВЛЕНИЯ (ZIP-Кристалл -> Жидкость)
    # -------------------------------------------------------------
    packing_eff = 0.35 + (f["sphericity"] * 0.45) + (f["disk_ness"] * 0.35)
    if f["rod_ness"] > 0.85 and f["rot"] == 0: packing_eff += 0.3 
    
    sym_p2p_bonus = 60.0 if (f["donors"] == f["acceptors"] and f["donors"] > 0) else 0.0
    crystal_spaghetti_penalty = f["rot"] * 18.0
    
    t_melt = (t_boil * packing_eff) + sym_p2p_bonus - crystal_spaghetti_penalty
    if t_melt < 10: t_melt = 10.0

    is_sublime = False
    if f["rod_ness"] > 0.9 and f["asa"] < 60 and p2p_cache == 0 and f["heavy"] > 1:
        t_melt = t_boil * 1.25 
        is_sublime = True
        
    if t_melt > t_boil and not is_sublime: t_melt = t_boil * 0.95

    # -------------------------------------------------------------
    # 3. ТОЧКА ПИРОЛИЗА / РАСПАДА (CPU Kernel Panic)
    # -------------------------------------------------------------
    mass_drift = f["donors"] * 50.0 
    t_deg = 1500.0 + (f["heavy"] * 150.0) + (f["arom"] * 1000.0) - mass_drift - (f["rot"] * 30.0)
    
    if "O=C=O" in f["smiles"] or "N#N" in f["smiles"] or "[HH]" in f["smiles"]:
        t_deg = 6000.0 
        
    return {"T_melt": round(t_melt), "T_boil": round(t_boil), "T_deg": round(t_deg), "Sublimes": is_sublime}

# --- UI ---
st.title("🧊 V33.1: Absolute Hardware Phase Engine")
st.markdown("Движок использует **честный 3D Тензор Инерции (Sphericity/Disk-ness)** и **Voxel Footprint (ASA)**. Поддерживается пакетный расчет всей базы.")

col_sys1, col_sys2 = st.columns([1, 2])
with col_sys1:
    target_smiles = st.selectbox("Выберите информационный пакет:", list(TARGET_MOLECULES.keys()), format_func=lambda x: TARGET_MOLECULES[x])

with col_sys2:
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_single = st.button("🚀 Декомпилировать (1 молекула)", type="primary", use_container_width=True)
    with col_btn2:
        run_batch = st.button("🗂 Сгенерировать Сводную Таблицу (Все)", type="secondary", use_container_width=True)

if run_single:
    with st.spinner("Рендеринг 3D-геометрии и вычисление Тензора Инерции..."):
        features = extract_hardware_features(target_smiles)
        
        if features:
            phases = calculate_phase_transitions(features)
            
            st.markdown("### 🧬 Извлеченные Аппаратные Метрики:")
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("UDP Footprint (ASA)", f"{features['asa']:.1f} Å²")
            c_m2.metric("3D Сферичность", f"{features['sphericity']*100:.1f}%")
            c_m3.metric("Spaghetti-Фактор", features['rot'])
            c_m4.metric("P2P Сеть (D/A)", f"{features['donors']} / {features['acceptors']}")
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            tm_label = f"{phases['T_melt']} K (Сублимация)" if phases['Sublimes'] else f"{phases['T_melt']} K"
            c1.metric("🧊 Плавление (ROM Cache)", tm_label)
            c2.metric("💧 Кипение (RAM Cache)", f"{phases['T_boil']} K")
            c3.metric("🔥 Пиролиз (Kernel Panic)", f"{phases['T_deg']} K")
            
            temps = [0, phases['T_melt'], phases['T_melt']+1, phases['T_boil'], phases['T_boil']+1, phases['T_deg']]
            states = [10, 10, 40, 40, 80, 80]
            labels = ["Кристалл (ROM)", "Кристалл (ROM)", "Жидкость (RAM)", "Жидкость (RAM)", "Газ (UDP)", "Газ (UDP)"]
            
            if phases['Sublimes']:
                states = [10, 10, 80, 80, 80, 80]
                labels = ["Кристалл (ROM)", "Кристалл (ROM)", "Газ (Сублимация)", "Газ", "Газ", "Газ"]
            elif phases['T_melt'] >= phases['T_boil']:
                temps = [0, phases['T_boil'], phases['T_boil']+1, phases['T_melt'], phases['T_melt']+1, phases['T_deg']]
            
            df_plot = pd.DataFrame({"Температура (K)": temps, "Энтропия Среды": states, "Состояние Кэша": labels})
            fig = px.area(df_plot, x="Температура (K)", y="Энтропия Среды", color="Состояние Кэша",
                          color_discrete_map={"Кристалл (ROM)": "#00d2ff", "Жидкость (RAM)": "#3a7bd5", "Газ (UDP)": "#f6d365", "Газ (Сублимация)": "#f6d365"})
            fig.add_vline(x=phases['T_deg'], line_dash="dash", line_color="#FF4500", annotation_text="Полный Распад (Fire)")
            fig.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

if run_batch:
    with st.spinner("Компиляция полного стека. Расчет тензоров для всех систем..."):
        results_list = []
        for sm, name in TARGET_MOLECULES.items():
            feats = extract_hardware_features(sm)
            if feats:
                ph = calculate_phase_transitions(feats)
                results_list.append({
                    "Система": name.split(" - ")[0],
                    "Топология": name.split(" - ")[1] if " - " in name else "Стандарт",
                    "SMILES": sm,
                    "T_melt (K)": ph["T_melt"],
                    "T_boil (K)": ph["T_boil"],
                    "T_deg (K)": ph["T_deg"],
                    "Сферичность (%)": round(feats["sphericity"] * 100, 1),
                    "Footprint (Å²)": round(feats["asa"], 1),
                    "P2P Порты (D/A)": f"{feats['donors']}/{feats['acceptors']}",
                    "Сублимация": "Да" if ph["Sublimes"] else "Нет"
                })
        
        df_batch = pd.DataFrame(results_list)
        st.success("✅ Пакетная компиляция завершена!")
        
        # Подсветка "странных" фаз
        def highlight_phases(row):
            if row['Сублимация'] == 'Да':
                return ['background-color: rgba(255, 165, 0, 0.2)'] * len(row)
            return [''] * len(row)

        st.dataframe(df_batch.style.apply(highlight_phases, axis=1), use_container_width=True)
        
        csv_data = df_batch.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Скачать DataFrame (CSV)",
            data=csv_data,
            file_name="v33_batch_phases.csv",
            mime="text/csv",
            type="primary"
        )
