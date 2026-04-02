import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: THERMODYNAMIC ASSEMBLER V7 (DYNAMIC METABOLISM)
# =====================================================================

st.set_page_config(page_title="Assembler V7: Thermodynamics", layout="wide", page_icon="🔥")

# --- СИСТЕМНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
GAMMA_SYS = 1.0418               
Z0 = 377.0                       
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             
K_THETA = 2.0                    
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
C_LP = 12.5                      

# Загрузка кастомной таблицы метаболизма (отказ от официальной науки)
@st.cache_data
def load_metabolism_table():
    try:
        df = pd.read_csv("simureality_metabolism.csv")
        # Возвращаем словарь T_crit для быстрого доступа
        return dict(zip(df['Z'], df['T_crit (Порог Активации/Температура)']))
    except:
        st.error("Файл simureality_metabolism.csv не найден! Сначала сгенерируйте таблицу.")
        return {}

T_CRIT_MAP = load_metabolism_table()

# Для узлов, которых нет в нашей таблице, ставим заглушку среднего метаболизма
def get_t_crit(Z):
    return T_CRIT_MAP.get(Z, 1500.0) 

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

def get_angular_tension(mol_h, conf):
    total_tension = 0.0
    for atom in mol_h.GetAtoms():
        neighbors = [n.GetIdx() for n in atom.GetNeighbors()]
        if len(neighbors) >= 2:
            pos_c = np.array(conf.GetAtomPosition(atom.GetIdx()))
            max_angle = 109.47
            for i in range(len(neighbors)):
                for j in range(i+1, len(neighbors)):
                    v1 = np.array(conf.GetAtomPosition(neighbors[i])) - pos_c
                    v2 = np.array(conf.GetAtomPosition(neighbors[j])) - pos_c
                    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if n1 == 0 or n2 == 0: continue
                    val = max(-1.0, min(1.0, np.dot(v1, v2) / (n1 * n2)))
                    angle = math.degrees(math.acos(val))
                    if angle > max_angle: max_angle = angle
            total_tension += K_THETA * abs(max_angle - 109.47)
    return total_tension

def assemble_molecule_thermodynamically(smiles, T_sys, P_sys):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0: return None
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    total_hw = 0.0
    total_repulsion = 0.0
    max_t_activation = 0.0 # Температура, при которой молекула начнет собираться
    bonds_formed = 0

    # Модификатор Давления (Сжимает дистанции)
    # При 1.0 ATM дистанции стандартные. При 10 ATM дистанции сжимаются на 5%
    p_modifier = 1.0 - (math.log10(P_sys) * 0.05) if P_sys >= 1.0 else 1.0

    for bond in mol_h.GetBonds():
        a1, a2 = bond.GetBeginAtom(), bond.GetEndAtom()
        z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
        bo = bond.GetBondTypeAsDouble()
        
        pos1, pos2 = np.array(conf.GetAtomPosition(a1.GetIdx())), np.array(conf.GetAtomPosition(a2.GetIdx()))
        d_actual = np.linalg.norm(pos1 - pos2) * p_modifier
        
        # Модификатор Температуры (Перегретые ядра расширяют эфирный буфер портов)
        # Если T_sys высокое, атомы "распухают" на доли Ангстрема
        t_expansion_1 = 1.0 + (T_sys / get_t_crit(z1)) * 0.05
        t_expansion_2 = 1.0 + (T_sys / get_t_crit(z2)) * 0.05
        
        r_cov1 = pt.GetRcovalent(z1) * t_expansion_1
        r_cov2 = pt.GetRcovalent(z2) * t_expansion_2
        
        # Термодинамический барьер: Реакция слияния выгодна, только если T_sys 
        # раскачала хотя бы один из атомов достаточно близко к его T_crit
        bond_activation_temp = min(get_t_crit(z1), get_t_crit(z2)) * 0.35 # Эмпирический порог активации 35% от критического
        if bond_activation_temp > max_t_activation:
            max_t_activation = bond_activation_temp

        if T_sys < bond_activation_temp:
            # Отказ транзакции. Метаболизм атомов еще справляется сам.
            continue
            
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

    total_tension = get_angular_tension(mol_h, conf) if bonds_formed > 0 else 0.0
    heavy_atoms = mol_h.GetNumHeavyAtoms()
    final_cashback = (Z0 / 2.0) if heavy_atoms > 0 and bonds_formed > 0 else 0.0

    sigma_k = total_hw - total_tension - total_repulsion + final_cashback if bonds_formed > 0 else 0.0
    
    status = "СБОРКА УСПЕШНА" if bonds_formed > 0 else "ОТКАЗ (Слишком холодно)"
    
    return {
        "status": status,
        "energy": sigma_k,
        "t_activation": max_t_activation,
        "bonds_formed": bonds_formed
    }

# --- UI ---
st.title("🔥 ThermoSynthesizer V7.0")
st.markdown("Молекулы собираются только тогда, когда нагрузка на метаболизм (Температура) заставляет одиночные ядра искать сброс кэша. Атомы считываются из кастомной БД метаболизма.")

col1, col2 = st.columns(2)
T_sys = col1.slider("🌡 Температура Системы (T_sys)", min_value=10, max_value=6000, value=300, step=10, help="Накачка системы джиттером. Чем выше, тем охотнее атомы сливаются.")
P_sys = col2.slider("🗜 Давление (P_sys, ATM)", min_value=1.0, max_value=100.0, value=1.0, step=1.0, help="Сжимает 3D-решетку, провоцируя сближение буферов.")

test_mols = {
    "FF": "Фтор (F2)",
    "ClCl": "Хлор (Cl2)",
    "[HH]": "Водород (H2)",
    "O=O": "Кислород (O2)",
    "C": "Метан (CH4)",
    "O=C=O": "Углекислый газ (CO2)",
}

if st.button("Запустить Симуляцию Реактора"):
    results = []
    for smiles, name in test_mols.items():
        res = assemble_molecule_thermodynamically(smiles, T_sys, P_sys)
        if res:
            results.append({
                "Молекула": name,
                "Барьер Активации (T_act)": f"{res['t_activation']:.1f}",
                "Статус Транзакции": res['status'],
                "Выделенная Энергия (kJ)": f"{res['energy']:.1f}" if res['bonds_formed'] > 0 else "0.0"
            })
    
    st.dataframe(pd.DataFrame(results), use_container_width=True)
    
    st.info("""
    **Как это читать:** При 300 (комнатная) тяжелые галогены (Хлор, Бром) и Водород будут собираться охотно, потому что их $T_{act}$ низок. 
    Но Углекислый газ ($CO_2$) или Кислород ($O_2$) не смогут собраться "из воздуха" при $300$ — их метаболизм ядер слишком устойчив. Вам придется раскачать Температуру (нагреть реактор), чтобы запустить сборку (горение)!
    """)
