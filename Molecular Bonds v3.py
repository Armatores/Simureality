import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
import math
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: V11.0 GEOMETRIC OVERLAP TESTER
# =====================================================================

st.set_page_config(page_title="V11.0 Geometric Tester", layout="wide", page_icon="🧊")

# ОНТОЛОГИЧЕСКИЕ КОНСТАНТЫ V11 (Чистая геометрия, без эмпирики)
VACUUM_GATE = 3.325              # Гармоника вакуумных врат (Å)
BUFFER_RADIUS = VACUUM_GATE / 2  # 1.6625 Å (Радиус 137-узлового буфера)
STATIC_BASE_LOCK = 286.5         # Базовая цена Shared Pointer (кДж/моль)
VOLUME_BONUS = 12.75             # Энергия за 1 Å³ пересечения (кДж/моль)

def get_graph_complexity(smiles):
    """Считает количество тяжелых связей в макроузле"""
    try:
        mol = Chem.MolFromSmiles(str(smiles))
        return mol.GetNumBonds() if mol else -1
    except:
        return -1

def calculate_overlap_volume(d, R):
    """Вычисляет физический объем пересечения двух сфер"""
    if d >= 2 * R or d <= 0:
        return 0.0
    return (math.pi / 12) * (4 * R + d) * ((2 * R - d) ** 2)

def analyze_geometry(row):
    """
    Разворачивает молекулу в 3D, измеряет расстояние между конкретными ядрами
    и считает объем пересечения их кулоновских буферов.
    """
    smiles = str(row['molecule'])
    bond_idx = int(row['bond_index'])
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return pd.Series([np.nan, np.nan, np.nan])
        
        mol_h = Chem.AddHs(mol)
        bond = mol_h.GetBondWithIdx(bond_idx)
        a1 = bond.GetBeginAtomIdx()
        a2 = bond.GetEndAtomIdx()
        interface_type = bond.GetBondTypeAsDouble() # 1.0, 2.0, 3.0
        
        # Симуляция геометрии для получения реальных расстояний
        if AllChem.EmbedMolecule(mol_h, randomSeed=42) != 0:
            return pd.Series([np.nan, np.nan, interface_type])
        AllChem.MMFFOptimizeMolecule(mol_h)
        
        conf = mol_h.GetConformer()
        pos1 = np.array(conf.GetAtomPosition(a1))
        pos2 = np.array(conf.GetAtomPosition(a2))
        
        d_actual = np.linalg.norm(pos1 - pos2)
        v_int = calculate_overlap_volume(d_actual, BUFFER_RADIUS)
        
        return pd.Series([d_actual, v_int, interface_type])
    except:
        return pd.Series([np.nan, np.nan, np.nan])

@st.cache_data(show_spinner=False)
def load_base_data(file_path):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path, compression='gzip')
    df['bond_clean'] = df['bond_type'].astype(str).str.upper().str.strip()
    
    # Переводим BDE в кДж/моль
    df['Actual_BDE_kJ'] = pd.to_numeric(df['bde'], errors='coerce') * 4.184
    df_valid = df.dropna(subset=['Actual_BDE_kJ']).copy()
    
    # Считаем топологическую сложность всего датасета
    df_valid['Graph_Complexity'] = df_valid['molecule'].apply(get_graph_complexity)
    return df_valid[df_valid['Graph_Complexity'] > 0]

def compile_unit_test(df_tier):
    start = time.time()
    
    # 1. Считаем 3D-геометрию (Расстояние, Объем пересечения, Множитель связи)
    df_tier[['d_actual', 'v_int', 'interface_type']] = df_tier.apply(analyze_geometry, axis=1)
    
    # Отбрасываем молекулы, которые RDKit не смог развернуть в 3D
    df_tier = df_tier.dropna(subset=['d_actual', 'v_int']).copy()
    
    if len(df_tier) == 0:
        return df_tier, time.time() - start
        
    # 2. НОВАЯ ОНТОЛОГИЯ: Расчет BDE через объем наложения буферов
    df_tier['Grid_BDE_Final'] = (df_tier['interface_type'] * STATIC_BASE_LOCK) + (VOLUME_BONUS * df_tier['v_int'])
    
    # 3. Подсчет метрик
    df_tier['Abs_Error'] = np.abs(df_tier['Grid_BDE_Final'] - df_tier['Actual_BDE_kJ'])
    df_tier['Rel_Error_Pct'] = np.where(df_tier['Actual_BDE_kJ'] != 0, 
                                        (df_tier['Abs_Error'] / df_tier['Actual_BDE_kJ']) * 100, 0)
    df_tier['Accuracy'] = np.maximum(0, 100.0 - df_tier['Rel_Error_Pct'])
    
    return df_tier, time.time() - start

# --- UI ---
st.title("🧊 V11.0 Unit Tester: Геометрия Кулоновских Буферов")
st.markdown("Никаких эмпирических штрафов. BDE рассчитывается аналитически через объем пересечения $V_{int}$ сфер радиусом 1.6625 Å.")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner("Загрузка и индексация датасета..."):
    df_base = load_base_data(FILE_NAME)

if df_base is not None:
    max_bonds = int(df_base['Graph_Complexity'].max())
    
    col_ui1, col_ui2 = st.columns([2, 1])
    with col_ui1:
        target_bonds = st.slider("Сложность графа (Количество тяжелых связей)", 1, max_bonds, 1, step=1)
    
    df_filtered = df_base[df_base['Graph_Complexity'] == target_bonds].copy()
    
    with col_ui2:
        st.info(f"Найдено молекул: {len(df_filtered)}")
    
    if st.button(f"🚀 Скомпилировать геометрию (N={target_bonds})"):
        if len(df_filtered) == 0:
            st.warning("В датасете нет молекул с такой сложностью.")
        else:
            with st.spinner(f"Рендеринг 3D-решеток и расчет объемов V_int для N={target_bonds}..."):
                df_result, calc_time = compile_unit_test(df_filtered)
                
            if len(df_result) == 0:
                st.error("Не удалось сгенерировать 3D-координаты для выбранной группы.")
            else:
                mae = df_result['Abs_Error'].mean()
                mape = df_result['Rel_Error_Pct'].mean()
                
                ss_res = np.sum((df_result['Actual_BDE_kJ'] - df_result['Grid_BDE_Final']) ** 2)
                ss_tot = np.sum((df_result['Actual_BDE_kJ'] - df_result['Actual_BDE_kJ'].mean()) ** 2)
                r2_score = (1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
                
                st.success(f"Анализ завершен за {calc_time:.2f} сек. Обраработано связей: {len(df_result)}")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("МАЕ", f"{mae:.2f} kJ/mol")
                col2.metric("MAPE", f"{mape:.2f}%")
                col3.metric("R² Score", f"{r2_score:.3f}")
                col4.metric("Средняя точность", f"{df_result['Accuracy'].mean():.2f}%")
                
                fig = px.scatter(df_result, x="Actual_BDE_kJ", y="Grid_BDE_Final", color="bond_clean", 
                                 hover_data=["d_actual", "v_int"],
                                 opacity=0.7, title=f"Grid BDE vs Факт (Графы сложности {target_bonds})")
                min_val = min(df_result['Actual_BDE_kJ'].min(), df_result['Grid_BDE_Final'].min())
                max_val = max(df_result['Actual_BDE_kJ'].max(), df_result['Grid_BDE_Final'].max())
                fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🔍 Журнал Транзакций (Геометрия)")
                display_cols = ['molecule', 'bond_clean', 'd_actual', 'v_int', 'Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error', 'Accuracy']
                st.dataframe(df_result.sort_values(by='Abs_Error', ascending=False)[display_cols].style.format({
                    "d_actual": "{:.3f} Å",
                    "v_int": "{:.2f} Å³",
                    "Actual_BDE_kJ": "{:.1f}", 
                    "Grid_BDE_Final": "{:.1f}", 
                    "Abs_Error": "{:.1f}",
                    "Accuracy": "{:.1f}%"
                }))
else:
    st.error("Файл датасета не найден. Убедитесь, что bde-db2.csv.gz в корневой папке.")
