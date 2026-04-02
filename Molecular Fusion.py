import streamlit as st
import pandas as pd
import numpy as np
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: TOPOLOGICAL ASSEMBLER (WEB ENGINE)
# =====================================================================

st.set_page_config(page_title="Топологический Ассемблер", layout="wide", page_icon="🏗️")

GAMMA_SYS = 1.0418               
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2)**3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def get_topology_modifiers(mol_h, a1, a2, bo):
    tax = 0.0
    subsidy = 0.0
    z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
    hyb1, hyb2 = a1.GetHybridization(), a2.GetHybridization()

    if bo > 1.0:
        if hyb1 == Chem.rdchem.HybridizationType.SP or hyb2 == Chem.rdchem.HybridizationType.SP:
            tax += 140.0
        elif hyb1 == Chem.rdchem.HybridizationType.SP2 or hyb2 == Chem.rdchem.HybridizationType.SP2:
            if z1 == 8 or z2 == 8: subsidy += 40.0
            else: tax += 45.0

    if bo == 1.0:
        if z1 in [7,8] and z2 in [7,8]:
            tax += 100.0

    return tax, subsidy

st.title("🏗️ Топологический Ассемблер (Stellar Forge)")
st.markdown("Симулятор пошаговой сборки макро-узлов на ГЦК-решетке. Расчет полной энтальпии образования.")

smiles_input = st.text_input("SMILES Целевого Графа:", "O=C=O")

if st.button("Инициировать Сборку"):
    try:
        with st.spinner("Рендеринг 3D-матрицы и расчет вакуумного профита..."):
            mol = Chem.MolFromSmiles(smiles_input)
            mol_h = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol_h, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol_h)
            conf = mol_h.GetConformer()
            pt = Chem.GetPeriodicTable()

            log_data = []
            total_cohesive_energy = 0.0

            for bond in mol_h.GetBonds():
                a1 = bond.GetBeginAtom()
                a2 = bond.GetEndAtom()
                z1, z2 = a1.GetAtomicNum(), a2.GetAtomicNum()
                bo = bond.GetBondTypeAsDouble()

                r_cov1 = pt.GetRcovalent(z1)
                r_cov2 = pt.GetRcovalent(z2)
                pos1 = np.array(conf.GetAtomPosition(a1.GetIdx()))
                pos2 = np.array(conf.GetAtomPosition(a2.GetIdx()))
                d_actual = np.linalg.norm(pos1 - pos2)

                v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
                v_exc_1 = calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS)
                v_exc_2 = calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS)
                v_net = max(0.0, v_total_buf - v_exc_1 - v_exc_2)

                hardware_profit = ((bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)) * GAMMA_SYS
                tax, subsidy = get_topology_modifiers(mol_h, a1, a2, bo)
                
                transaction_energy = hardware_profit - tax + subsidy
                total_cohesive_energy += transaction_energy

                log_data.append({
                    "Интерфейс": f"{a1.GetSymbol()}-{a2.GetSymbol()}",
                    "bo": bo,
                    "V_net (Å³)": f"{v_net:.2f}",
                    "HW Профит (кДж)": f"+{hardware_profit:.1f}",
                    "Налог Сжатия": f"-{tax:.1f}" if tax > 0 else "0",
                    "Субсидия Стока": f"+{subsidy:.1f}" if subsidy > 0 else "0",
                    "Итог (кДж)": f"{transaction_energy:.1f}"
                })

            st.success("Синтез успешно скомпилирован.")
            
            col1, col2 = st.columns(2)
            col1.metric(label="Энергия Атомизации (ΣK)", value=f"{total_cohesive_energy:.1f} kJ/mol")
            col2.metric(label="Количество Транзакций", value=mol_h.GetNumBonds())

            df_log = pd.DataFrame(log_data)
            st.dataframe(df_log, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка компиляции графа: {e}")
