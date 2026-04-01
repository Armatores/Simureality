import streamlit as st
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
import math

# ==========================================
# SIMUREALITY HARDCODED CONSTANTS
# ==========================================
GAMMA_SYS = 1.0418          # Системный налог Матрицы
NODE_COST = 327.51          # Базовая вычислительная стоимость 1 узла интерфейса (кДж/моль)
VACUUM_GATE = 3.325         # Гармоника вакуумных врат (Å)
BUFFER_RADIUS = VACUUM_GATE / 2  # 1.6625 Å - Радиус кулоновского опроса

# ==========================================
# ОНТОЛОГИЧЕСКОЕ ЯДРО
# ==========================================
def calculate_overlap_volume(d, R):
    """Вычисляет объем пересечения двух сфер вакуумного буфера радиусом R на расстоянии d."""
    if d >= 2 * R:
        return 0.0
    v_int = (math.pi / 12) * (4 * R + d) * ((2 * R - d) ** 2)
    return v_int

def analyze_molecule(smiles):
    """Рендерит 3D координаты и вычисляет геометрический BDE для каждой связи."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None, "Ошибка: Невалидный SMILES"
    
    mol = Chem.AddHs(mol)
    # Симуляция геометрии (MMFF94) для получения реальных расстояний
    if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
        return None, "Ошибка: Не удалось сгенерировать 3D конформер"
    AllChem.MMFFOptimizeMolecule(mol)
    
    conf = mol.GetConformer()
    results = []
    
    for bond in mol.GetBonds():
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        
        # Пропускаем связи с водородом для чистоты анализа тяжелого каркаса (опционально)
        # if a1.GetAtomicNum() == 1 or a2.GetAtomicNum() == 1: continue
            
        idx1, idx2 = a1.GetIdx(), a2.GetIdx()
        pos1 = np.array(conf.GetAtomPosition(idx1))
        pos2 = np.array(conf.GetAtomPosition(idx2))
        
        d_actual = np.linalg.norm(pos1 - pos2)
        interface_type = bond.GetBondTypeAsDouble() # 1.0, 2.0, 3.0
        
        # 1. Считаем объем пересечения (Shared Bus)
        v_int = calculate_overlap_volume(d_actual, BUFFER_RADIUS)
        
        # 2. Базовая аппаратная стоимость (узлы * база * налог)
        base_energy = NODE_COST * interface_type * GAMMA_SYS
        
        # 3. Топологическое трение (Aliasing Penalty)
        # Штраф за деформацию: чем дальше реальная длина от идеального шага ГЦК, тем выше лаг
        ideal_d = 1.54 / (interface_type ** (1/3)) 
        friction_penalty = 150.0 * (d_actual - ideal_d)**2 
        
        final_bde = base_energy - friction_penalty
        
        bond_label = f"{a1.GetSymbol()}-{a2.GetSymbol()}"
        if interface_type == 2.0: bond_label = f"{a1.GetSymbol()}={a2.GetSymbol()}"
        if interface_type == 3.0: bond_label = f"{a1.GetSymbol()}#{a2.GetSymbol()}"
        
        results.append({
            "Связь": bond_label,
            "Интерфейс (Узлов)": interface_type,
            "3D Расстояние (Å)": round(d_actual, 3),
            "Объем Наложения (Å³)": round(v_int, 2),
            "База (кДж)": round(base_energy, 1),
            "Трение (кДж)": round(friction_penalty, 1),
            "BDE Предсказание": round(final_bde, 1)
        })
        
    return pd.DataFrame(results), "Успех"

# ==========================================
# STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Simureality V10: Geometric BDE", layout="wide")

st.title("Simureality V10: Онтология Ковалентной Связи")
st.markdown(f"""
**Базовые параметры ГЦК-Матрицы:**
* Системный налог ($\gamma_{{sys}}$): **{GAMMA_SYS}**
* Стоимость 1 узла: **{NODE_COST} кДж/моль**
* Вакуумные Врата ($\Gamma$): **{VACUUM_GATE} Å** (Радиус опроса буфера: **{BUFFER_RADIUS} Å**)
""")

smiles_input = st.text_input("Введите SMILES молекулы (например: CC, C=C, CCO, c1ccccc1):", "CCO")

if st.button("Декомпилировать Геометрию"):
    with st.spinner("Рендеринг 3D-решетки и расчет пересечения буферов..."):
        df_res, status = analyze_molecule(smiles_input)
        
        if df_res is not None:
            st.success("Матрица успешно рассчитала топологию.")
            st.dataframe(df_res, use_container_width=True)
            
            st.markdown("### Декодинг Метрик:")
            st.markdown("""
            * **Объем Наложения (Å³):** Физический объем пересечения двух сфер радиусом 1.6625 Å. Это тот самый "сэкономленный" кэш, перешедший в Shared Bus.
            * **База (кДж):** Дефолтная энергия, которая выделяется при идеальном наложении (Узлы * 327.51 * 1.0418).
            * **Трение (кДж):** Алиасинг. Налог за то, что реальное межатомное расстояние не совпадает с идеальной гармоникой вакуума $\Gamma$.
            """)
        else:
            st.error(status)
