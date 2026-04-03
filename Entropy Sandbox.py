import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import Descriptors

# =====================================================================
# SIMUREALITY V32.0: MACRO-STATE CLUSTER ENGINE
# Трехуровневая эмуляция виртуального ГЦК-кластера (Вещества)
# =====================================================================

st.set_page_config(page_title="V32.0 Cluster Engine", layout="wide", page_icon="🧊")

# База тестовых информационных систем
TARGET_MOLECULES = {
    "O": "Вода (H2O) — Идеальный 3D-кристалл", 
    "CCO": "Этанол (C2H5OH) — Асимметричная цепь", 
    "C": "Метан (CH4) — Газовый шар",
    "C1=CC=CC=C1": "Бензол (C6H6) — Ароматический диск",
    "CCCCCCC": "Гептан (C7H16) — Длинная макаронина",
    "N": "Аммиак (NH3)",
    "O=C=O": "Углекислый газ (CO2)",
    "[HH]": "Водород (H2)",
    "ClC(Cl)(Cl)Cl": "Тетрахлорметан (CCl4)"
}

def calculate_virtual_cluster_caches(smiles):
    """
    Рассчитывает 3 аппаратных кэша для симуляции виртуального кластера.
    """
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    
    # 1. Парсинг микро-топологии
    heavy_atoms = mol.GetNumHeavyAtoms()
    h_atoms = len([a for a in mol_h.GetAtoms() if a.GetAtomicNum() == 1])
    rings = mol.GetRingInfo().NumRings()
    
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

    # --- КЭШ 1: P2P-МАРШРУТИЗАЦИЯ (Отвечает за Кристалл/Плавление) ---
    raw_p2p = (lone_pairs * polar_hydrogens * 40.0) + (lone_pairs * 5.0)
    
    # Расчет аппаратной симметрии портов. Вода (2:2) = 1.0. Спирт (2:1) = 0.5.
    max_ports = max(1, max(lone_pairs, polar_hydrogens))
    min_ports = min(lone_pairs, polar_hydrogens)
    symmetry_bonus = min_ports / max_ports
    
    p2p_crystal_cache = raw_p2p * (0.5 + 0.5 * symmetry_bonus)
    
    # --- КЭШ 2: ОБЪЕМНЫЙ ЯКОРЬ (Отвечает за Жидкость/Кипение) ---
    volume_cache = (heavy_atoms * 15.0) + (h_atoms * 5.0) + (rings * 20.0)
    
    # --- КЭШ 3: КОВАЛЕНТНЫЙ КАРКАС (Отвечает за Пиролиз) ---
    clock_drift = (h_atoms * 200) if heavy_atoms > 0 else 0
    t_deg_base = 4000 + (heavy_atoms * 150) - clock_drift + (rings * 800)
    if smiles == "O=C=O": t_deg_base = 6000
    if smiles == "[HH]": t_deg_base = 6000
    
    return {
        "p2p_crystal": p2p_crystal_cache,
        "p2p_raw": raw_p2p,
        "volume": volume_cache,
        "t_deg": max(1500, t_deg_base),
        "metrics": {"lone_pairs": lone_pairs, "polar_h": polar_hydrogens, "symmetry": symmetry_bonus}
    }

def simulate_macro_states(smiles, p_sys):
    caches = calculate_virtual_cluster_caches(smiles)
    if not caches: return None
    
    p_factor = 1.0 + (math.log10(p_sys) * 0.08) if p_sys > 0 else 1.0
    
    # Математика перехода (Эмпирические множители Матрицы)
    # Плавление: разрушение жесткого P2P кристалла
    t_melt = (caches["p2p_crystal"] * 1.2) + (caches["volume"] * 1.0)
    
    # Кипение: полный отрыв от объемного якоря и остаточных P2P связей
    t_boil = (caches["p2p_raw"] * 1.8) + (caches["volume"] * 2.8)
    
    # Корректировка для сверхмалых симметричных молекул (Метан)
    if caches["p2p_raw"] == 0 and caches["volume"] < 50:
        t_melt = caches["volume"] * 1.5
        t_boil = caches["volume"] * 2.8

    # Принудительная физика (плавление не может быть выше кипения)
    if t_melt >= t_boil:
        t_melt = t_boil * 0.8 # Сублимация (упрощенно)
        
    return {
        "T_melt": round(t_melt * p_factor),
        "T_boil": round(t_boil * p_factor),
        "T_deg": round(caches["t_deg"]),
        "Caches": caches
    }

# --- UI ---
st.title("🧊 V32.0: Macro-State Cluster Engine")
st.markdown("Переход от одной молекулы к виртуальному кластеру (Веществу). Матрица разделяет стабильность на **Кэш P2P-портов** (Твердое тело) и **Объемный Якорь** (Жидкость).")

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
            
            # --- ВИЗУАЛИЗАЦИЯ КЭШЕЙ ---
            st.markdown("### 🧬 Внутренние параметры маршрутизации:")
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Свободные Порты", metrics["lone_pairs"])
            c_m2.metric("Полярные Водороды", metrics["polar_h"])
            c_m3.metric("Симметрия Кристалла", f"{metrics['symmetry']*100:.0f}%")
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("🧊 Плавление (T_melt)", f"{t_melt} K", help="Разрушение жесткого кристалла")
            c2.metric("💧 Кипение (T_boil)", f"{t_boil} K", help="Преодоление объемного якоря")
            c3.metric("🔥 Пиролиз (T_deg)", f"{t_deg} K", help="Уничтожение самой молекулы")
            
            # --- ПОСТРОЕНИЕ ГРАФИКА ФАЗ ---
            temps = [0, t_melt, t_melt+1, t_boil, t_boil+1, t_deg]
            states = [10, 10, 40, 40, 80, 80]
            labels = ["Кристалл", "Кристалл", "Жидкость", "Жидкость", "Газ", "Газ"]
            
            df_plot = pd.DataFrame({"Температура (K)": temps, "Энтропия Среды": states, "Агрегатное Состояние": labels})
            
            fig = px.area(df_plot, x="Температура (K)", y="Энтропия Среды", color="Агрегатное Состояние",
                          color_discrete_map={
                              "Кристалл": "#00d2ff", "Жидкость": "#3a7bd5", "Газ": "#f6d365"
                          }, title="Поэтапный сброс аппаратных кэшей")
            
            # Добавляем границу Пиролиза
            fig.add_vline(x=t_deg, line_dash="dash", line_color="red", annotation_text="Пиролиз")
            fig.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
