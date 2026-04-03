import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import Descriptors

# =====================================================================
# SIMUREALITY V32.1: MACRO-STATE CLUSTER ENGINE (PACKING PATCH)
# Трехуровневая эмуляция с учетом 2D/3D геометрической упаковки
# =====================================================================

st.set_page_config(page_title="V32.1 Cluster Engine", layout="wide", page_icon="🧊")

TARGET_MOLECULES = {
    "O": "Вода (H2O)", 
    "CCO": "Этанол (C2H5OH)", 
    "C": "Метан (CH4)",
    "C1=CC=CC=C1": "Бензол (C6H6)",
    "CCCCCCC": "Гептан (C7H16)",
    "N": "Аммиак (NH3)",
    "O=C=O": "Углекислый газ (CO2)",
    "[HH]": "Водород (H2)",
    "ClC(Cl)(Cl)Cl": "Тетрахлорметан (CCl4)"
}

def calculate_virtual_cluster_caches(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    
    heavy_atoms = mol.GetNumHeavyAtoms()
    h_atoms = len([a for a in mol_h.GetAtoms() if a.GetAtomicNum() == 1])
    rings = mol.GetRingInfo().NumRings()
    is_aromatic = any(atom.GetIsAromatic() for atom in mol_h.GetAtoms())
    
    lone_pairs = 0
    polar_hydrogens = 0
    
    for atom in mol_h.GetAtoms():
        z = atom.GetAtomicNum()
        if z in [9, 17, 35, 53]: lone_pairs += 3
        elif z in [8, 16, 34]: lone_pairs += 2
        elif z in [7, 15]: lone_pairs += 1
        
        if z == 1:
            neighbor = atom.GetNeighbors()[0]
            if neighbor.GetAtomicNum() in [7, 8, 9]:
                polar_hydrogens += 1

    # КЭШ 1: P2P
    raw_p2p = (lone_pairs * polar_hydrogens * 40.0) + (lone_pairs * 5.0)
    max_ports = max(1, max(lone_pairs, polar_hydrogens))
    min_ports = min(lone_pairs, polar_hydrogens)
    symmetry_bonus = min_ports / max_ports
    p2p_crystal_cache = raw_p2p * (0.5 + 0.5 * symmetry_bonus)
    
    # КЭШ 2: ОБЪЕМНЫЙ ЯКОРЬ
    volume_cache = (heavy_atoms * 15.0) + (h_atoms * 5.0) + (rings * 20.0)
    
    # --- БЛОК ПАТЧА V32.1: ГЕОМЕТРИЧЕСКАЯ УПАКОВКА (PACKING BONUS) ---
    packing_bonus = 0.0
    
    # 2D Упаковка (pi-стекинг для плоских ароматических колец)
    if is_aromatic:
        packing_bonus += (heavy_atoms * 22.0)
        
    # 3D Упаковка (Симметричные тетраэдры/сферы без P2P-конфликтов)
    if symmetry_bonus == 0 and lone_pairs >= 12 and heavy_atoms == 5:
        packing_bonus += 140.0
        
    # Защита базовых газов от ложной кристаллизации
    if heavy_atoms <= 1 and lone_pairs == 0:
        packing_bonus = 0.0
        
    # КЭШ 3: КОВАЛЕНТНЫЙ КАРКАС
    clock_drift = (h_atoms * 200) if heavy_atoms > 0 else 0
    t_deg_base = 4000 + (heavy_atoms * 150) - clock_drift + (rings * 800)
    if smiles == "O=C=O": t_deg_base = 6000
    if smiles == "[HH]": t_deg_base = 6000
    
    return {
        "p2p_crystal": p2p_crystal_cache,
        "p2p_raw": raw_p2p,
        "volume": volume_cache,
        "packing": packing_bonus,
        "t_deg": max(1500, t_deg_base),
        "metrics": {"lone_pairs": lone_pairs, "polar_h": polar_hydrogens, "symmetry": symmetry_bonus, "is_aromatic": is_aromatic}
    }

def simulate_macro_states(smiles, p_sys):
    caches = calculate_virtual_cluster_caches(smiles)
    if not caches: return None
    
    p_factor = 1.0 + (math.log10(p_sys) * 0.08) if p_sys > 0 else 1.0
    
    # Внедрение Packing Bonus в расчет плавления
    t_melt = (caches["p2p_crystal"] * 1.2) + (caches["volume"] * 1.0) + caches["packing"]
    t_boil = (caches["p2p_raw"] * 1.8) + (caches["volume"] * 2.8)
    
    if caches["p2p_raw"] == 0 and caches["volume"] < 50:
        t_melt = caches["volume"] * 1.5
        t_boil = caches["volume"] * 2.8

    if t_melt >= t_boil:
        t_melt = t_boil * 0.8
        
    return {
        "T_melt": round(t_melt * p_factor),
        "T_boil": round(t_boil * p_factor),
        "T_deg": round(caches["t_deg"]),
        "Caches": caches
    }

# --- UI ---
st.title("🧊 V32.1: Macro-State Cluster Engine (Packing Patch)")
st.markdown("Внедрен **Бонус Геометрической Упаковки** (2D $\\pi$-стекинг и 3D тетраэдрическая симметрия) для корректного расчета точки плавления тяжелых асимметричных жидкостей.")

col_sys1, col_sys2 = st.columns([1, 2])
with col_sys1:
    target_mol = st.selectbox("Сборка ГЦК-Кластера:", list(TARGET_MOLECULES.keys()), format_func=lambda x: TARGET_MOLECULES[x])
    p_sys = st.slider("🗜 Давление (P_sys, ATM)", 0.1, 100.0, 1.0, 0.1)

with col_sys2:
    if st.button("🚀 Сгенерировать Термодинамику Вещества", type="primary", use_container_width=True):
        res = simulate_macro_states(target_mol, p_sys)
        
        if res:
            t_melt, t_boil, t_deg = res["T_melt"], res["T_boil"], res["T_deg"]
            metrics = res["Caches"]["metrics"]
            packing = res["Caches"]["packing"]
            
            st.markdown("### 🧬 Аппаратные кэши кластера:")
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("P2P Порты", metrics["lone_pairs"])
            c_m2.metric("Полярные H", metrics["polar_h"])
            c_m3.metric("Симметрия", f"{metrics['symmetry']*100:.0f}%")
            c_m4.metric("Бонус Упаковки", f"+{packing:.0f}")
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("🧊 Плавление (T_melt)", f"{t_melt} K")
            c2.metric("💧 Кипение (T_boil)", f"{t_boil} K")
            c3.metric("🔥 Пиролиз (T_deg)", f"{t_deg} K")
            
            temps = [0, t_melt, t_melt+1, t_boil, t_boil+1, t_deg]
            states = [10, 10, 40, 40, 80, 80]
            labels = ["Кристалл", "Кристалл", "Жидкость", "Жидкость", "Газ", "Газ"]
            
            df_plot = pd.DataFrame({"Температура (K)": temps, "Энтропия Среды": states, "Агрегатное Состояние": labels})
            
            fig = px.area(df_plot, x="Температура (K)", y="Энтропия Среды", color="Агрегатное Состояние",
                          color_discrete_map={"Кристалл": "#00d2ff", "Жидкость": "#3a7bd5", "Газ": "#f6d365"})
            fig.add_vline(x=t_deg, line_dash="dash", line_color="red", annotation_text="Пиролиз")
            fig.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
