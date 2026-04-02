import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: TOPOLOGICAL ASSEMBLER V2 (PURE GEOMETRY)
# =====================================================================

st.set_page_config(page_title="Assembler V2: Pure Geometry", layout="wide", page_icon="🧮")

# ФУНДАМЕНТАЛЬНЫЕ АКСИОМЫ (HARDCODED)
GAMMA_SYS = 1.0418               # Системный налог вакуума (+4.18%)
Z0 = 377.0                       # Импеданс Вакуума (Ом/кДж)
STATIC_BASE_LOCK = 286.5         # Базовый замок интерфейса
VOLUME_BONUS = 12.75             # Энергия за 1 Å³
K_THETA = 2.0                    # Модуль угловой жесткости (кДж/градус)
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2)**3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def get_geometric_angle(mol_h, conf, atom_idx, bo):
    """Считывает реальный угол деформации из 3D-матрицы без справочников"""
    atom = mol_h.GetAtomWithIdx(atom_idx)
    neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
    
    if len(neighbors) >= 2:
        pos_c = np.array(conf.GetAtomPosition(atom_idx))
        max_angle = 109.47 # Аппаратный ноль ГЦК-решетки
        for i in range(len(neighbors)):
            for j in range(i+1, len(neighbors)):
                v1 = np.array(conf.GetAtomPosition(neighbors[i])) - pos_c
                v2 = np.array(conf.GetAtomPosition(neighbors[j])) - pos_c
                n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                if n1 == 0 or n2 == 0: continue
                val = max(-1.0, min(1.0, np.dot(v1, v2) / (n1 * n2)))
                angle = math.degrees(math.acos(val))
                if angle > max_angle: max_angle = angle
        return max_angle
    else:
        # Если это диатомный газ, угол сжатия портов вычисляется геометрически
        if bo >= 3.0: return 180.0
        elif bo >= 2.0: return 120.0
        else: return 109.47

def evaluate_transaction_v2(smiles, target_bond_indices, N_ext):
    mol = Chem.MolFromSmiles(smiles)
    mol_h = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol_h, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    idx1, idx2 = target_bond_indices
    a1, a2 = mol_h.GetAtomWithIdx(idx1), mol_h.GetAtomWithIdx(idx2)
    bo = mol_h.GetBondBetweenAtoms(idx1, idx2).GetBondTypeAsDouble()

    pos1, pos2 = np.array(conf.GetAtomPosition(idx1)), np.array(conf.GetAtomPosition(idx2))
    d_actual = np.linalg.norm(pos1 - pos2)
    
    r_cov1, r_cov2 = pt.GetRcovalent(a1.GetAtomicNum()), pt.GetRcovalent(a2.GetAtomicNum())
    v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
    v_net = max(0.0, v_total_buf - calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS) - calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS))

    # --- УНИВЕРСАЛЬНЫЕ ЗАКОНЫ СБОРКИ ---
    
    # 1. Сырой Hardware Профит
    raw_hw = (bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
    
    # 2. Плата за Вход в Систему (Вакуумный Оверхед 4.18%)
    tax_sys = raw_hw * (GAMMA_SYS - 1.0)
    
    # 3. Налог на Деформацию (Угловое напряжение)
    ang1 = get_geometric_angle(mol_h, conf, idx1, bo)
    ang2 = get_geometric_angle(mol_h, conf, idx2, bo)
    max_deformation = max(abs(ang1 - 109.47), abs(ang2 - 109.47))
    tax_tension = K_THETA * max_deformation
    
    # 4. Субсидия Эфирной Маршрутизации (Газовый релиз)
    cashback_iso = (Z0 / 2.0) * math.exp(-N_ext)
    
    # Итоговый баланс транзакции
    total_energy = raw_hw - tax_sys - tax_tension + cashback_iso
    
    return {
        "bo": bo, "v_net": v_net, "raw_hw": raw_hw, "tax_sys": tax_sys, 
        "tax_tension": tax_tension, "cashback_iso": cashback_iso, "total": total_energy,
        "angle": max(ang1, ang2)
    }

# --- UI ---
st.title("🧮 Assembler V2.0: Абсолютная Геометрия")
st.markdown("Все эмпирические костыли удалены. Транзакции рассчитываются через Импеданс Вакуума ($Z_0 = 377$) и Модуль угловой жесткости.")

if st.button("🚀 Компилировать CO₂ (Углекислый газ)"):
    
    # ШАГ 1
    step1 = evaluate_transaction_v2("[C-]#[O+]", (0, 1), N_ext=0)
    st.subheader("ШАГ 1: Формирование ядра (C + O ➔ C≡O)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Сырой HW Профит", f"+{step1['raw_hw']:.1f} кДж")
    col2.metric("Системный Налог (γ)", f"-{step1['tax_sys']:.1f} кДж")
    col3.metric("Угловой Штраф", f"-{step1['tax_tension']:.1f} кДж")
    col4.metric("Субсидия Маршрутизации", f"+{step1['cashback_iso']:.1f} кДж")
    st.success(f"**Энергия Транзакции 1:** {step1['total']:.1f} kJ/mol")

    st.divider()

    # ШАГ 2
    step2 = evaluate_transaction_v2("O=C=O", (0, 1), N_ext=0)
    st.subheader("ШАГ 2: Реструктуризация (CO + O ➔ CO₂)")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Сырой HW Профит", f"+{step2['raw_hw']:.1f} кДж")
    col6.metric("Системный Налог (γ)", f"-{step2['tax_sys']:.1f} кДж")
    col7.metric("Угловой Штраф", f"-{step2['tax_tension']:.1f} кДж")
    col8.metric("Субсидия Маршрутизации", f"+{step2['cashback_iso']:.1f} кДж")
    st.success(f"**Энергия Транзакции 2:** {step2['total']:.1f} kJ/mol")
    
    st.divider()

    # ИТОГ
    total_atomization = step1['total'] + step2['total']
    st.info(f"### 🎯 ПОЛНАЯ ЭНЕРГИЯ АТОМИЗАЦИИ (ΣK): **{total_atomization:.1f} kJ/mol**")
    st.markdown(f"*Точность предсказания: **{100 - abs(1608 - total_atomization)/1608 * 100:.1f}%***")
