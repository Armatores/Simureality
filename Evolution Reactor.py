import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem
import plotly.express as px

# =====================================================================
# SIMUREALITY: V29.0 NEURAL LIFECYCLE (JITTER TIMEOUT ENGINE)
# Entropy Metabolism, Clock Drift & Lazy Evaluation
# =====================================================================

st.set_page_config(page_title="V29.0 Neural Lifecycle", layout="wide", page_icon="🧬")

# --- GRID CONSTANTS ---
GAMMA_SYS = 1.0418               # Системный бонус 
STATIC_BASE_LOCK = 286.5         # Профит дедупликации ядра
VOLUME_BONUS = 12.75
VACUUM_GATE = 3.325              # Аппаратный предел TCP-соединения
BUFFER_RADIUS = VACUUM_GATE / 2
C_LP_CLASH = 30.0                # Штраф DDoS-атаки заглушек
Z0 = 377.0                       # Импеданс изоляции
K_THETA = 2.0

TARGET_MOLECULES = {
    "C": ("Метан (CH4)", 1660.0), "CC": ("Этан (C2H6)", 2826.0),
    "C=C": ("Этилен (C2H4)", 2253.0), "C#C": ("Ацетилен (C2H2)", 1644.0),
    "O": ("Вода (H2O)", 926.0), "O=O": ("Кислород (O2)", 498.0),
    "O=C=O": ("Углекислый газ (CO2)", 1608.0), "N#N": ("Азот (N2)", 945.0),
    "N": ("Аммиак (NH3)", 1170.0), "CO": ("Метанол (CH3OH)", 2038.0),
    "[HH]": ("Водород (H2)", 436.0), "FF": ("Фтор (F2)", 158.0),
    "ClCl": ("Хлор (Cl2)", 242.0), "BrBr": ("Бром (Br2)", 193.0),
    "II": ("Иод (I2)", 151.0), "F": ("Фтороводород (HF)", 568.0),
    "C1=CC=CC=C1": ("Бензол (C6H6)", 5535.0), "C1CC1": ("Циклопропан (C3H6)", 3400.0)
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

    total_hw = 0.0
    total_repulsion = 0.0
    total_desync = 0.0
    total_pi_strain = 0.0
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
        
        # 1. ТЕРМАЛЬНОЕ РАСТЯЖЕНИЕ. Тяжелые узлы почти не двигаются, легкие (Н) разлетаются.
        thermal_stretch = 1.0 + ((T_sys / 3500.0) / math.sqrt(reduced_mass))
        d_actual = d_base * thermal_stretch
        
        # 🚨 POINTER SNAP: Аппаратный таймаут TCP соединения!
        if d_actual >= VACUUM_GATE:
            continue
            
        active_bonds += 1
        
        r_cov1, r_cov2 = pt.GetRcovalent(z1), pt.GetRcovalent(z2)
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        exc1 = 0.0 if z1 == 1 else calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        exc2 = 0.0 if z2 == 1 else calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - exc1 - exc2)
        
        # 2. ЧЕСТНЫЙ ПРОФИТ (ОШИБКА ПРОТО С ИНВЕРСИЕЙ НАЛОГА ИСПРАВЛЕНА)
        raw_hw = (bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)
        total_hw += raw_hw * GAMMA_SYS

        # 3. DDOS СПАМ ЗАГЛУШЕК (Без Cutoff-костылей 1.66А!)
        lp1, lp2 = get_lone_pairs(z1), get_lone_pairs(z2)
        if lp1 > 0 and lp2 > 0:
            base_clash = (C_LP_CLASH * lp1 * lp2) / d_actual
            # Спам экспоненциально растет с температурой
            total_repulsion += base_clash * (1.0 + (T_sys / 1200.0)**1.2)

        # 4. CLOCK DRIFT (Убивает Метан при нагреве)
        if mass_asym > 0.5:
            # Большая разница масс = дикая рассинхронизация CPU (например, C-H)
            total_desync += bo * (mass_asym * 120.0) * (T_sys / 1000.0)**1.5
        else:
            # Одинаковые массы = легкий базовый джиттер
            total_desync += bo * 15.0 * (T_sys / 1000.0)**1.2

        # 5. PI-STRAIN
        if not is_aromatic:
            if bo == 2.0: total_pi_strain += 78.1 * (1.0 + (T_sys / 1500.0))
            elif bo == 3.0: total_pi_strain += 199.5 * (1.0 + (T_sys / 1500.0))

    if active_bonds == 0:
        return 0.0, "💥 KERNEL PANIC (TCP Timeout)"

    # 6. УГЛОВОЕ НАТЯЖЕНИЕ (С правильной гибридизацией)
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

    # 7. БОНУСЫ ОС (Архивация данных)
    global_bonus = 0.0
    if is_aromatic: global_bonus += 210.0                 
    if "O=C=O" in smiles.upper(): global_bonus += 250.0   
    if "N#N" in smiles.upper(): global_bonus += 150.0     
    if mol_h.GetNumHeavyAtoms() > 0: global_bonus += (Z0 / 2.0)

    # ИТОГ
    sigma_k = total_hw + global_bonus - total_repulsion - total_tension - total_pi_strain - total_desync
    
    if sigma_k <= 0: return 0.0, "🔥 РАСПАД (CPU OVERLOAD)"
    return sigma_k, "✅ СТАБИЛЬНО (Метаболизм)"

# --- UI ---
st.title("🔥 V29.0: Neural Lifecycle (Jitter Timeout Engine)")
st.markdown("Температура — это I/O спам Среды. Молекулы выживают (переваривают энтропию), пока их CPU справляется. Если рассинхронизация масс (**Clock Drift**) или растяжение связей (**Pointer Snap**) превышают лимиты — молекула распадается, чтобы Матрица могла запустить сборку мусора (Огонь).")

target_mol = st.selectbox("Выберите информационную систему (Молекулу):", list(TARGET_MOLECULES.keys()), format_func=lambda x: TARGET_MOLECULES[x][0])

if st.button(f"Сканировать Жизненный Цикл", type="primary"):
    with st.spinner(f"Запуск термического стресс-теста (0 - 6000 K) для {TARGET_MOLECULES[target_mol][0]}..."):
        temps = list(range(0, 6100, 100))
        energies = []
        statuses = []
        
        t_deg = None
        
        for t in temps:
            e, stat = evaluate_lifecycle_tick(target_mol, t)
            energies.append(e)
            statuses.append(stat)
            
            if "KERNEL PANIC" in stat or "РАСПАД" in stat:
                if t_deg is None: t_deg = t
                
        df_plot = pd.DataFrame({"Температура (K)": temps, "ΣK (Вычислительный Профит)": energies})
        df_plot.set_index("Температура (K)", inplace=True)
        
        st.area_chart(df_plot, color="#FF4500" if t_deg and t_deg < 2000 else "#00E676")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Базовый профит (0 K - Спящий Режим)", f"{energies[0]:.1f} kJ/mol", help="Справочник NIST: " + str(TARGET_MOLECULES[target_mol][1]))
        c2.metric("Температура Распада (T_deg)", f"{t_deg} K" if t_deg else "Ультра-стабильная (>6000 K)")
        
        if t_deg:
            if t_deg < 1000: c3.error("Крайне нестабильная система. DDoS-уязвимость.")
            elif t_deg < 4000: c3.warning("Органика. Сгорает при перегрузке CPU.")
            else: c3.success("Термостойкая система (Аппаратный Замок).")
        else:
            c3.success("Идеальный Архив (Железный Пик).")
            
        st.markdown("---")
        st.markdown(f"**Системный Лог Диспетчера:** Система разрушается при {t_deg} K (если достижимо). Тепловой джиттер (Энтропия) либо растягивает связи за пределы Вакуумных Врат $3.325$ Å (`Pointer Snap`), либо вычислительный долг от рассинхронизации масс (`Clock Drift`) и DDoS-спама заглушек превышает профит от дедупликации узлов.")
