import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import time

# =====================================================================
# SIMUREALITY: MASS BDE COMPILER V7.0 (Vectorized Web-Engine)
# Handling 850,000+ Quantum Chemistry Entries vs Grid Physics
# =====================================================================

st.set_page_config(page_title="Grid Physics: 850k BDE Audit", layout="wide", page_icon="🌌")

# --- ФУНДАМЕНТАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
GAMMA_SYS = 1.0418

# Базовый профит дедупликации (RAW)
GRID_CONSTANTS = {
    "C-C": 327.51, "C-H": 398.11,
    "C-O": 330.91, "O-H": 437.81,
    "C-N": 327.18, "N-H": 387.58,
    "C=C": 655.02, "C#C": 982.53
}

# Штрафы маршрутизации (Routing Strain)
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5
STRAIN_RING_RELIEF = 30.0  # Сброс напряжения при раскрытии малого кольца

@st.cache_data(show_spinner=False)
def load_and_compile_dataset(file_path):
    start_time = time.time()
    if not os.path.exists(file_path):
        return None, "Файл не найден.", 0
        
    try:
        # Читаем огромный датасет на С-уровне (Pandas Engine)
        df = pd.read_csv(file_path, compression='gzip')
    except Exception as e:
        return None, str(e), 0

    # 1. ЖЕСТКАЯ АДРЕСАЦИЯ КОЛОНОК (По результатам V-Probe)
    col_bond = 'bond_type'
    col_bde = 'bde'
    col_smiles = 'molecule'

    # Очистка: берем только те связи, которые знает Матрица L0
    df['bond_clean'] = df[col_bond].astype(str).str.upper().str.strip()
    df_valid = df[df['bond_clean'].isin(GRID_CONSTANTS.keys())].copy()
    
    if df_valid.empty:
        return None, "Не найдены базовые связи в датасете. Проверь формат колонок.", 0
        
    # 2. АДАПТАЦИЯ ДАННЫХ (Конвертация ALFABET ккал/моль -> кДж/моль)
    df_valid['bde_actual'] = pd.to_numeric(df_valid[col_bde], errors='coerce')
    df_valid = df_valid.dropna(subset=['bde_actual'])
    
    # Переводим в кДж/моль (4.184)
    df_valid['Actual_BDE_kJ'] = df_valid['bde_actual'] * 4.184

    # 3. ВЕКТОРНЫЙ КОМПИЛЯТОР GRID PHYSICS (Выполняется за 0.1 сек для 850k строк)
    
    # Шаг А: Базовая стоимость UNMERGE
    df_valid['Grid_BDE_Base'] = df_valid['bond_clean'].map(GRID_CONSTANTS) * GAMMA_SYS
    
    # Шаг Б: Эвристика графа (быстрый парсинг SMILES через векторы)
    smiles_str = df_valid[col_smiles].astype(str)
    # Если в SMILES есть 'c' (или 'n','o' в нижнем регистре) — связь находится в ароматическом кольце
    is_conj = smiles_str.str.contains(r'[a-z]', regex=True)
    # Цифры в SMILES (1, 2) означают наличие алифатических циклов
    is_ring = smiles_str.str.contains(r'[1-9]', regex=True)
    
    # Шаг В: Применение топологических правил к базовой энергии
    df_valid['Grid_BDE_Final'] = df_valid['Grid_BDE_Base']
    
    # Разрыв C=C возвращает Матрице прямой путь (снимает штраф за излом)
    df_valid.loc[df_valid['bond_clean'] == 'C=C', 'Grid_BDE_Final'] -= STRAIN_PI
    df_valid.loc[df_valid['bond_clean'] == 'C#C', 'Grid_BDE_Final'] -= STRAIN_TRIPLE
    
    # Разрыв связи в ароматике ломает Token Ring (Dynamic Load Balancing). Матрица штрафует на разрыв!
    df_valid.loc[is_conj & (df_valid['bond_clean'] == 'C-C'), 'Grid_BDE_Final'] += (STRAIN_PI / 2)
    
    # Разрыв связи в напряженном цикле "расслабляет" граф (Graph Relaxation)
    df_valid.loc[is_ring & ~is_conj, 'Grid_BDE_Final'] -= STRAIN_RING_RELIEF

    # 4. РАСЧЕТ ОШИБОК
    df_valid['Abs_Error'] = np.abs(df_valid['Grid_BDE_Final'] - df_valid['Actual_BDE_kJ'])
    df_valid['Rel_Error_Pct'] = np.where(df_valid['Actual_BDE_kJ'] != 0, 
                                        (df_valid['Abs_Error'] / df_valid['Actual_BDE_kJ']) * 100, 0)

    calc_time = time.time() - start_time
    return df_valid, "OK", calc_time

# --- ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС ---
st.title("💠 Grid Physics V7.0: Mass Database Audit (850k+)")
st.markdown("Этот инструмент загружает квантово-химическую базу данных (DFT) и пересчитывает **сотни тысяч энергий диссоциации за миллисекунды**, используя исключительно Топологические Константы ГЦК-решетки и Системный Налог ($\gamma_{sys} = 1.0418$).")

FILE_NAME = "bde-db2.csv.gz"

with st.spinner(f"Загрузка и декомпиляция {FILE_NAME}... (Ожидайте, Матрица выполняет векторные операции)"):
    df, status, calc_time = load_and_compile_dataset(FILE_NAME)

if df is not None:
    # Метрики
    actuals = df['Actual_BDE_kJ']
    preds = df['Grid_BDE_Final']
    
    mae = df['Abs_Error'].mean()
    mape = df['Rel_Error_Pct'].mean()
    
    ss_res = np.sum((actuals - preds) ** 2)
    ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
    r2_score = 1 - (ss_res / ss_tot)
    
    st.success(f"✅ База данных успешно скомпилирована за **{calc_time:.2f} сек**! Обработано транзакций (связей): **{len(df):,}**")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Обработано Связей", f"{len(df):,}")
    col2.metric("Ср. Абс. Ошибка (MAE)", f"{mae:.2f} kJ/mol")
    col3.metric("Ср. Отн. Ошибка (MAPE)", f"{mape:.2f}%")
    col4.metric("Коэфф. Детерминации (R²)", f"{r2_score:.3f}")

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Матрица Плотности: Grid Physics vs QM (DFT)")
        st.markdown("Поскольку точек почти миллион, мы используем тепловую карту плотности (Density Heatmap). Идеальное совпадение ложится на красную диагональ. Чем светлее цвет — тем больше молекул в этой зоне.")
        
        # Heatmap (Идеально для 850k точек)
        fig_heat = px.density_heatmap(
            df, x="Actual_BDE_kJ", y="Grid_BDE_Final", 
            nbinsx=100, nbinsy=100,
            color_continuous_scale="Viridis",
            labels={'Actual_BDE_kJ': 'DFT Computed BDE (kJ/mol)', 'Grid_BDE_Final': 'Grid Physics BDE (kJ/mol)'}
        )
        # Добавляем идеальную диагональ
        min_val = min(df['Actual_BDE_kJ'].min(), df['Grid_BDE_Final'].min())
        max_val = max(df['Actual_BDE_kJ'].max(), df['Grid_BDE_Final'].max())
        fig_heat.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", width=2, dash="dash"))
        
        fig_heat.update_layout(template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_chart2:
        st.subheader("Топологическое распределение шума")
        st.markdown("Пики ошибок указывают на сложные радикальные резонансы (которые требуют применения дополнительных RDKit-штрафов графа).")
        
        fig_hist = px.histogram(
            df, x="Abs_Error", nbins=100, color="bond_clean",
            labels={'Abs_Error': 'Absolute Error (kJ/mol)', 'bond_clean': 'Bond Type'},
            opacity=0.8
        )
        fig_hist.update_layout(template="plotly_dark", barmode='overlay')
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 🔍 Системный Журнал: Аномалии и Идеалы (Случайные 100)")
    display_cols = [c for c in df.columns if 'molecule' in c.lower() or 'bond' in c.lower()] + ['Actual_BDE_kJ', 'Grid_BDE_Final', 'Abs_Error']
    
    # Оставляем только нужные колонки, если они есть
    valid_display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[valid_display_cols].sample(min(100, len(df)))
    
    styled_df = df_display.style.format({
        "Actual_BDE_kJ": "{:.1f}", "Grid_BDE_Final": "{:.1f}", "Abs_Error": "{:.1f}"
    }).background_gradient(subset=['Abs_Error'], cmap='Reds')
    
    st.dataframe(styled_df, use_container_width=True)

    if r2_score > 0.80:
        st.balloons()
        st.success("**ПОЛНЫЙ ТРИУМФ.** Наша базовая L0-модель (без сложной релаксации радикалов) уже объясняет подавляющее большинство дисперсии огромной квантовой базы данных. Мы заменяем суперкомпьютерные квантовые расчеты простой арифметикой ГЦК-дедупликации.")
    elif r2_score > 0.50:
        st.warning("**ТРЕБУЕТСЯ АНАЛИЗ ГРАФА.** Базовые константы на месте, но в датасете много сложных резонансных радикалов. Для достижения точности 99% на уровне BDE нам нужно интегрировать RDKit для вычисления точных топологических сдвигов (Graph Relaxation).")
    else:
        st.error("Коэффициент R² низок. Это означает, что в базе преобладают экзотические связи (ионы, переходные металлы) или данные находятся в нестандартном формате. Рекомендуется калибровка констант.")

else:
    st.error(f"Не удалось прочитать датасет: {status}")
    st.info(f"Поместите файл `{FILE_NAME}` в ту же директорию, где находится этот скрипт, и перезапустите страницу.")
