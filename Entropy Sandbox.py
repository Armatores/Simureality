import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
from rdkit import Chem
from rdkit.Chem import Descriptors

# =====================================================================
# V31.0: THERMODYNAMIC SANDBOX (HOTFIX)
# Эмуляция макроскопических фазовых переходов на основе ГЦК-параметров
# =====================================================================

st.set_page_config(page_title="V31.0 Sandbox", layout="wide", page_icon="🌡️")

# --- КОНСТАНТЫ МАТРИЦЫ ---
VACUUM_GATE = 3.325
Z0 = 377.0
SYNC_BASE_MULTIPLIER = 42.5  # Базовый коэффициент межсетевой синхронизации
PRESSURE_MODIFIER = 0.05     # Чувствительность фазы к давлению P_sys

TARGET_MOLECULES = {
    "O": "Вода (H2O)", 
    "C": "Метан (CH4)", 
    "CCO": "Этанол (C2H5OH)", 
    "O=C=O": "Углекислый газ (CO2)",
    "[HH]": "Водород (H2)", 
    "C1=CC=CC=C1": "Бензол (C6H6)",
    "ClC(Cl)(Cl)Cl": "Тетрахлорметан (CCl4)",
    "N": "Аммиак (NH3)",
    "CC(=O)C": "Ацетон"
}

def analyze_system_metabolism(smiles):
    """
    Вычисляет параметры макро-узла для симуляции среды.
    Возвращает Кэш Синхронизации (для кипения/плавления) и T_deg (для распада).
    """
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    
    # 1. Сбор топологических данных
    heavy_atoms = mol.GetNumHeavyAtoms()
    h_atoms = len([a for a in mol_h.GetAtoms() if a.GetAtomicNum() == 1])
    
    lone_pairs = 0
    polar_hydrogens = 0 # Водороды, подключенные к N, O, F (узлы высокого джиттера)
    
    for atom in mol_h.GetAtoms():
        z = atom.GetAtomicNum()
        if z in [9, 17, 35, 53]: lone_pairs += 3
        elif z in [8, 16, 34]: lone_pairs += 2
        elif z in [7, 15]: lone_pairs += 1
        
        if z == 1:
            neighbor = atom.GetNeighbors()[0]
            if neighbor.GetAtomicNum() in [7, 8, 9]:
                polar_hydrogens += 1

    # 2. РАСЧЕТ МЕЖСЕТЕВОЙ СИНХРОНИЗАЦИИ (Phase Affinity)
    vdw_volume = heavy_atoms * 15.0 + h_atoms * 5.0
    network_ping = (lone_pairs * polar_hydrogens * 1.5) + (lone_pairs * 0.2)
    
    sync_cash = (vdw_volume * 0.8) + (network_ping * SYNC_BASE_MULTIPLIER)
    
    # 3. ЭМПИРИЧЕСКАЯ КАЛИБРОВКА T_deg
    clock_drift = 0
    if h_atoms > 0 and heavy_atoms > 0: clock_drift = h_atoms * 250
    t_deg_base = 4500 + (heavy_atoms * 100) - clock_drift + (lone_pairs * 50)
    if "O=C=O" in smiles: t_deg_base = 6000 
    if smiles == "[HH]": t_deg_base = 6000
    
    return {
        "sync_cash": sync_cash,
        "t_deg": max(1500, t_deg_base)
    }

def run_environment_simulation(smiles, p_sys):
    params = analyze_system_metabolism(smiles)
    if not params: return None
    
    sync = params["sync_cash"]
    t_deg = params["t_deg"]
    
    # Давление P_sys аппаратно сжимает решетку, повышая температуру кипения
    p_factor = 1.0 + (math.log10(p_sys) * PRESSURE_MODIFIER) if p_sys > 0 else 1.0
    
    t_melt = sync * 0.6 * p_factor
    t_boil = sync * 1.8 * p_factor
    
    if sync < 100: 
        t_melt = sync * 0.4 * p_factor
        t_boil = sync * 1.1 * p_factor
        
    return {
        "T_melt": round(t_melt),
        "T_boil": round(t_boil),
        "T_deg": round(t_deg)
    }

# --- UI ---
st.title("🌡️ V31.0: Thermodynamic Sandbox")
st.markdown("Симуляция макро-состояний. Матрица вычисляет **Кэш Межсетевой Синхронизации** — насколько молекулам выгодно объединяться в жидкие и твердые кластеры для сброса энтропии.")

col_sys1, col_sys2 = st.columns([1, 2])
with col_sys1:
    target_mol = st.selectbox("Выберите Информационную Систему:", list(TARGET_MOLECULES.keys()), format_func=lambda x: TARGET_MOLECULES[x])
    p_sys = st.slider("🗜 Давление (P_sys, ATM)", 0.1, 100.0, 1.0, 0.1)

with col_sys2:
    if st.button("🚀 Запустить Макро-Симуляцию Среды", type="primary", use_container_width=True):
        res = run_environment_simulation(target_mol, p_sys)
        
        if res:
            t_melt = res["T_melt"]
            t_boil = res["T_boil"]
            t_deg = res["T_deg"]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🧊 Точка Плавления (Кристалл -> Жидкость)", f"{t_melt} K", help="Разрушение жесткой макро-решетки")
            c2.metric("💧 Точка Кипения (Жидкость -> Газ)", f"{t_boil} K", help="Разрыв межсетевых TCP-соединений")
            c3.metric("🔥 Точка Пиролиза (Газ -> Плазма)", f"{t_deg} K", help="Внутренний крах молекулы (Pointer Snap)")
            
            temps = list(range(0, int(t_deg) + 1000, 50))
            phases = []
            energy_states = []
            
            for t in temps:
                if t < t_melt:
                    phases.append("Твердое тело (Архив)")
                    energy_states.append(10)
                elif t < t_boil:
                    phases.append("Жидкость (Динамическая Сеть)")
                    energy_states.append(40)
                elif t < t_deg:
                    phases.append("Газ (Изолированные Узлы)")
                    energy_states.append(80)
                else:
                    phases.append("Плазма (Критический Сбой)")
                    energy_states.append(150)
                    
            df_plot = pd.DataFrame({
                "Температура Системы (K)": temps,
                "Уровень Энтропии": energy_states,
                "Фаза": phases
            })
            
            fig = px.area(df_plot, x="Температура Системы (K)", y="Уровень Энтропии", color="Фаза", 
                          color_discrete_map={
                              "Твердое тело (Архив)": "#00d2ff",
                              "Жидкость (Динамическая Сеть)": "#3a7bd5",
                              "Газ (Изолированные Узлы)": "#f6d365",
                              "Плазма (Критический Сбой)": "#ff512f"
                          }, title=f"Термодинамический профиль: {TARGET_MOLECULES[target_mol]}")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"**Анализ Диспетчера:** При давлении {p_sys} ATM система {TARGET_MOLECULES[target_mol]} поддерживает вторичную сеть связей до {t_boil} K. После этого тепловой джиттер превышает Кэш Синхронизации, и система переходит в режим изолированных узлов (Газ). При достижении {t_deg} K происходит аппаратное разрушение самих макро-узлов (Пиролиз).")
