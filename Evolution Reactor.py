import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: EVOLUTIONARY REACTOR V8 (CASCADE STATE MACHINE)
# =====================================================================

st.set_page_config(page_title="V8: Evolutionary Reactor", layout="wide", page_icon="⚛️")

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
        return {6: 5907.0, 8: 3611.0, 1: 50.0} # Fallback для C, O, H

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

def evaluate_transaction(smiles, T_sys):
    """Оценивает ΣK конкретного макро-графа с учетом T_sys"""
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return 0, 0, "Error"
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0: return 0, 0, "Error"
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    total_hw, total_repulsion, max_t_activation = 0.0, 0.0, 0.0
    bonds_formed = 0

    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
        bo = bond.GetBondTypeAsDouble()
        
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2)
        
        t_expansion_1 = 1.0 + (T_sys / get_t_crit(z1)) * 0.05
        t_expansion_2 = 1.0 + (T_sys / get_t_crit(z2)) * 0.05
        r_cov1 = pt.GetRcovalent(z1) * t_expansion_1
        r_cov2 = pt.GetRcovalent(z2) * t_expansion_2
        
        bond_activation_temp = min(get_t_crit(z1), get_t_crit(z2)) * 0.35 
        if bond_activation_temp > max_t_activation: max_t_activation = bond_activation_temp

        if T_sys < bond_activation_temp: return 0, max_t_activation, "Отклонено (T_sys < T_act)"
            
        bonds_formed += 1
        v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
        exc1 = 0.0 if z1 == 1 else calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
        exc2 = 0.0 if z2 == 1 else calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
        v_net = max(0.0, v_total_buf - exc1 - exc2)
        
        is_term1, is_term2 = z1 in [9, 17, 35, 53], z2 in [9, 17, 35, 53]
        base_lock = 0.0 if (is_term1 and is_term2) else STATIC_BASE_LOCK
        
        raw_hw = (bo * base_lock) + (VOLUME_BONUS * v_net)
        tax_sys = raw_hw * (GAMMA_SYS - 1.0)
        total_hw += (raw_hw - tax_sys)

        if d_actual < BUFFER_RADIUS:
            lp1, lp2 = get_lone_pairs(z1), get_lone_pairs(z2)
            total_repulsion += C_LP * (lp1 * lp2)

    # Упрощенный расчет деформации для MVP-реактора
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
            total_tension += K_THETA * abs(max_angle - 109.47)

    heavy_atoms = mol_h.GetNumHeavyAtoms()
    final_cashback = (Z0 / 2.0) if heavy_atoms > 0 and bonds_formed > 0 else 0.0
    sigma_k = total_hw - total_tension - total_repulsion + final_cashback if bonds_formed > 0 else 0.0
    
    return sigma_k, max_t_activation, "Успех"

# --- UI ---
st.title("⚛️ Evolutionary Reactor: Каскадная Сборка")
st.markdown("Симуляция адаптивного распределения энтропии. Диспетчер Матрицы ищет путь с максимальным сбросом вычислительного долга на каждом такте.")

T_sys = st.slider("🌡 Температура Системы (T_sys)", min_value=300, max_value=2000, value=1500, step=50, help="Накачка системы. 1264+ необходимо для горения углерода.")

st.subheader("Сценарий: Горение Углерода (C + O + O)")
st.markdown("В вакууме встретились 1 атом Углерода и 2 атома Кислорода. Как Матрица их соединит?")

if st.button("Запустить Такт Времени"):
    # ТАКТ 1: Оценка первых столкновений
    st.write("### Такт 1: Анализ первичных столкновений")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Путь А (O + O ➔ O₂)**")
        e_o2, t_o2, status_o2 = evaluate_transaction("O=O", T_sys)
        st.metric("Барьер (T_act)", f"{t_o2:.0f}")
        st.metric("Профит (ΔΣK)", f"+{e_o2:.1f} кДж" if status_o2 == "Успех" else status_o2)

    with col2:
        st.success("**Путь Б (C + O ➔ CO)**")
        e_co, t_co, status_co = evaluate_transaction("[C-]#[O+]", T_sys)
        st.metric("Барьер (T_act)", f"{t_co:.0f}")
        st.metric("Профит (ΔΣK)", f"+{e_co:.1f} кДж" if status_co == "Успех" else status_co)

    if status_co == "Успех" and e_co > e_o2:
        st.markdown(f"**Решение Диспетчера:** Матрица выбирает Путь Б. Образование $C \equiv O$ сбрасывает **{e_co:.1f} кДж** вычислительного долга, что в два раза эффективнее $O_2$. Формируется Угарный газ.")
        
        st.divider()
        # ТАКТ 2: Каскадное слияние
        st.write("### Такт 2: Вторичный захват")
        st.warning("**Сценарий (CO + O ➔ CO₂)**")
        e_co2, t_co2, status_co2 = evaluate_transaction("O=C=O", T_sys)
        
        # Энергия второго шага = Энергия полной молекулы минус энергия ядра CO
        step_2_profit = e_co2 - e_co
        st.metric("Профит вторичного такта (ΔΣK)", f"+{step_2_profit:.1f} кДж" if status_co2 == "Успех" else status_co2)
        
        st.markdown(f"**Итог Эволюции:** Молекула $CO$ работает как нейросеть — она поглощает еще один атом кислорода из среды, чтобы перераспределить энтропию и достичь финального оптимума $CO_2$ с общей стабильностью **{e_co2:.1f} кДж**.")
    else:
        st.error("**Решение Диспетчера:** Недостаточно Температуры (T_sys) для активации узлов. Атомы остаются в состоянии изолированного газа. Повысьте T_sys.")
