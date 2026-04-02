import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: FULL CYCLE ENGINE V9 (SYNTHESIS & DEGRADATION)
# =====================================================================

st.set_page_config(page_title="V9: Full Cycle Engine", layout="wide", page_icon="🌪️")

GAMMA_SYS = 1.0418               
Z0 = 377.0                       
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             
K_THETA = 2.0                    
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
C_LP = 12.5                      

@st.cache_data
def load_metabolism_table():
    try:
        df = pd.read_csv("simureality_metabolism.csv")
        return dict(zip(df['Z'], df['T_crit (Порог Активации/Температура)']))
    except:
        return {6: 5907.0, 8: 3611.0, 1: 50.0, 7: 2356.0} 

T_CRIT_MAP = load_metabolism_table()

def get_t_crit(Z): return T_CRIT_MAP.get(Z, 1500.0) 
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
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def evaluate_lifecycle_tick(smiles, T_sys, P_sys=1.0):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return 0.0, "Error"
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0: return 0.0, "Error"
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    total_hw, total_repulsion, total_thermal_tax = 0.0, 0.0, 0.0
    bonds_formed = 0
    p_modifier = 1.0 - (math.log10(max(1.0, P_sys)) * 0.05)

    max_t_activation = 0.0

    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
        bo = bond.GetBondTypeAsDouble()
        
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        
        # Термальное растяжение связей (Джиттер дистанции)
        d_actual = np.linalg.norm(pos1 - pos2) * p_modifier * (1.0 + (T_sys / 20000.0))
        
        # Эфирное распухание атомов под нагрузкой
        t_expansion_1 = 1.0 + (T_sys / get_t_crit(z1)) * 0.12 
        t_expansion_2 = 1.0 + (T_sys / get_t_crit(z2)) * 0.12
        r_cov1 = pt.GetRcovalent(z1) * t_expansion_1
        r_cov2 = pt.GetRcovalent(z2) * t_expansion_2
        
        bond_activation_temp = min(get_t_crit(z1), get_t_crit(z2)) * 0.35 
        if bond_activation_temp > max_t_activation: max_t_activation = bond_activation_temp

        # Если слишком холодно - транзакция отвергается
        if T_sys < bond_activation_temp: continue
            
        bonds_formed += 1
        
        # Пересечение сфер (V_net падает по мере распухания r_cov)
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        exc1 = 0.0 if z1 == 1 else calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        exc2 = 0.0 if z2 == 1 else calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - exc1 - exc2)
        
        is_term1, is_term2 = z1 in [9, 17, 35, 53], z2 in [9, 17, 35, 53]
        base_lock = 0.0 if (is_term1 and is_term2) else STATIC_BASE_LOCK
        
        raw_hw = (bo * base_lock) + (VOLUME_BONUS * v_net)
        tax_sys = raw_hw * (GAMMA_SYS - 1.0)
        total_hw += (raw_hw - tax_sys)

        # Термальный штраф за вибрацию базового замка
        total_thermal_tax += (T_sys / 1000.0) * 35.0 * bo

        if d_actual < BUFFER_RADIUS:
            lp1, lp2 = get_lone_pairs(z1), get_lone_pairs(z2)
            total_repulsion += C_LP * (lp1 * lp2)

    if bonds_formed == 0: return 0.0, "Газ (Холод)"

    total_tension = 0.0
    for atom in mol_h.GetAtoms():
        neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
        if len(neighbors) >= 2:
            pos_c = np.array(conf.GetAtomPosition(atom.GetIdx()))
            max_angle = 109.47
            for i in range(len(neighbors)):
                for j in range(i+1, len(neighbors)):
                    v1, v2 = np.array(conf.GetAtomPosition(neighbors[i])) - pos_c, np.array(conf.GetAtomPosition(neighbors[j])) - pos_c
                    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if n1 != 0 and n2 != 0:
                        val = max(-1.0, min(1.0, np.dot(v1, v2) / (n1 * n2)))
                        angle = math.degrees(math.acos(val))
                        if angle > max_angle: max_angle = angle
            # Термальное усиление углового напряжения
            total_tension += (K_THETA * abs(max_angle - 109.47)) * (1.0 + (T_sys / 3000.0))

    heavy_atoms = mol_h.GetNumHeavyAtoms()
    final_cashback = (Z0 / 2.0) if heavy_atoms > 0 else 0.0

    sigma_k = total_hw - total_tension - total_repulsion - total_thermal_tax + final_cashback
    
    # DROPOUT: Если баланс ушел в минус, Матрица обрывает связи
    if sigma_k < 0: return 0.0, "Плазма (Распад)"
    
    return sigma_k, "Стабильный Макро-Узел"

# --- UI ---
st.title("🌪️ V9: Full Cycle Engine (Термодинамический Жизненный Цикл)")
st.markdown("Движок симулирует полный цикл молекулы: от холодного изолированного состояния до активации (сборки), а затем до критического перегрева и пиролиза (Dropout).")

target_mol = st.selectbox("Выберите макро-граф для сканирования:", ["O=C=O", "C", "O=O", "[HH]", "N#N", "ClCl"])
mol_names = {"O=C=O": "Углекислый газ (CO2)", "C": "Метан (CH4)", "O=O": "Кислород (O2)", "[HH]": "Водород (H2)", "N#N": "Азот (N2)", "ClCl": "Хлор (Cl2)"}

if st.button(f"Сканировать Зону Жизни: {mol_names[target_mol]}"):
    with st.spinner("Прогон термодинамического градиента (0 - 8000 K)..."):
        temps = list(range(100, 8100, 100))
        energies = []
        statuses = []
        
        t_act, t_deg = None, None
        
        for t in temps:
            e, stat = evaluate_lifecycle_tick(target_mol, t)
            energies.append(e)
            statuses.append(stat)
            
            if stat == "Стабильный Макро-Узел" and t_act is None: t_act = t
            if stat == "Плазма (Распад)" and t_act is not None and t_deg is None: t_deg = t
            
        df_plot = pd.DataFrame({"Температура (T_sys)": temps, "ΣK (Энергия Связи)": energies})
        df_plot.set_index("Температура (T_sys)", inplace=True)
        
        # Рендер графика
        st.area_chart(df_plot, color="#00ff88")
        
        # Метрики
        c1, c2, c3 = st.columns(3)
        c1.metric("Точка Сборки (T_act)", f"{t_act} K" if t_act else "N/A")
        c2.metric("Точка Распада (T_deg)", f"{t_deg} K" if t_deg else "Недостижима < 8000")
        habitable = (t_deg - t_act) if (t_act and t_deg) else "N/A"
        c3.metric("Ширина Зоны Жизни", f"{habitable} K" if habitable != "N/A" else "N/A")
        
        st.success(f"**Анализ:** Молекула {mol_names[target_mol]} активируется при **{t_act} K**, достигает оптимума, но при дальнейшем нагреве ее эфирные буферы начинают задыхаться от энтропии. При **{t_deg} K** Диспетчер Матрицы принудительно обрывает связи (Dropout), спасая базовые атомы от перегрузки.")
