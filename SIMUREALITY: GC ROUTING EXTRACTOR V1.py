import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: GC ROUTING EXTRACTOR V1.0 (STREAMLIT EDITION)
# Декомпиляция аппаратных констант радиоактивного распада
# ==========================================================================================

st.set_page_config(page_title="GC Routing Extractor", layout="wide")
st.title("Simureality: Декомпилятор Сборщика Мусора 🗑️")
st.markdown("""
Этот модуль доказывает, что распад — это не "квантовая случайность", а строгий сетевой алгоритм очистки памяти. 
Мы извлекаем скрытые константы пропускной способности 3D-матрицы напрямую из базы AME2020/NUBASE.
""")

@st.cache_data
def load_data():
    file_name = "simureality_chronos_benchmark_V73.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return None

df = load_data()

if df is None:
    st.warning("Критическая ошибка: Файл `simureality_chronos_benchmark_V73.csv` не найден в корне. Загрузите его:")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

if df is not None:
    # --- 1. ОЧИСТКА И ПОДГОТОВКА ДАННЫХ ---
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()
    
    # Считаем открытые порты (Parity Lock)
    df_unstable['N'] = df_unstable['A'] - df_unstable['Z']
    df_unstable['Unpaired_Ports'] = (df_unstable['Z'] % 2) + (df_unstable['N'] % 2)
    
    # Считаем мощность ошибки (корень из долга)
    df_unstable['sqrt_dK'] = np.sqrt(np.maximum(df_unstable['ΔK Debt (MeV)'], 0.1))
    
    st.success(f"База данных подключена. Анализируется {len(df_unstable)} нестабильных изотопов.")
    
    # --- 2. МАШИННОЕ ОБУЧЕНИЕ (REVERSE ENGINEERING) ---
    X = np.column_stack((df_unstable['Z'], df_unstable['sqrt_dK'], df_unstable['Unpaired_Ports']))
    y = df_unstable['Log10(T_1/2)'].values
    
    reg = LinearRegression().fit(X, y)
    r_squared = reg.score(X, y)
    
    # Получаем коэффициенты
    t_base = reg.intercept_
    z_imp = reg.coef_[0]
    e_pow = reg.coef_[1]
    p_lock = reg.coef_[2]
    
    # Добавляем предсказанное время в датафрейм для графика
    df_unstable['Predicted_Log10(T)'] = reg.predict(X)
    
    st.header("1. Аппаратные константы Сборщика Мусора (GC Constants)")
    st.markdown(f"**Точность декомпиляции (R²):** `{r_squared:.4f}`")
    st.latex(r"\log_{10}(T_{1/2}) = T_{base} + Z_{imp} \cdot Z + E_{pow} \cdot \sqrt{\Delta K} + P_{lock} \cdot Unpaired")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T_base (Базовый такт)", f"{t_base:+.3f}", "Базовый лимит сброса")
    c2.metric("Z_imp (Сопротивление Z)", f"{z_imp:+.3f}", "Тормозит удаление (Packet Loss)")
    c3.metric("E_pow (Тяжесть Ошибки)", f"{e_pow:+.3f}", "Ускоряет удаление", delta_color="inverse")
    c4.metric("P_lock (Штраф Порта)", f"{p_lock:+.3f}", "Ускоряет удаление", delta_color="inverse")
    
    st.divider()

    # --- 3. ГРАФИК ПРЕДСКАЗАНИЙ ---
    st.header("2. Визуализация Уравнения Маршрутизации")
    st.markdown("Сравнение реального времени жизни из базы NUBASE с расчетным временем по нашей выведенной аппаратной формуле.")
    
    fig = px.scatter(
        df_unstable, 
        x="Predicted_Log10(T)", 
        y="Log10(T_1/2)", 
        color="Unpaired_Ports",
        hover_name="Isotope",
        hover_data=["Z", "A", "ΔK Debt (MeV)"],
        labels={
            "Predicted_Log10(T)": "Расчетное время (Simureality GC Equation)", 
            "Log10(T_1/2)": "Реальное время распада (AME2020)"
        },
        title="Корреляция: Аппаратный Алгоритм vs Реальность",
        template="plotly_dark",
        color_continuous_scale="Viridis"
    )
    # Добавляем идеальную диагональ
    fig.add_shape(type="line", line=dict(dash='dash', color='white'), x0=-25, y0=-25, x1=30, y1=30)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 4. РАЗРЕШЕНИЕ ПАРАДОКСА 5 MeV ---
    st.header("3. Декомпиляция Парадокса: Одинаковый Долг, Разная Судьба")
    st.markdown("Почему легкое и тяжелое ядро с одинаковым дефицитом в ~5 МэВ живут с разницей в миллиарды раз? **Ответ: Импеданс $Z$ (Забитая шина данных).**")
    
    col_light, col_heavy = st.columns(2)
    
    light = df_unstable[(df_unstable['Z'] < 20) & (df_unstable['ΔK Debt (MeV)'].between(5.0, 5.6))].head(1)
    heavy = df_unstable[(df_unstable['Z'] > 80) & (df_unstable['ΔK Debt (MeV)'].between(5.0, 5.6))].head(1)
    
    with col_light:
        if not light.empty:
            row = light.iloc[0]
            st.subheader("Свободный Канал (Легкое ядро)")
            st.info(f"**Изотоп:** {row['Isotope']}\n\n**Протонов (Z):** {row['Z']}\n\n**Топологический Долг:** {row['ΔK Debt (MeV)']:.2f} MeV\n\n**Время распада:** $10^{{{row['Log10(T_1/2)']:.2f}}}$ секунд")
            st.markdown("*Сборщику мусора ничто не мешает. Ошибка в 5 МэВ удаляется мгновенно через пустую сеть.*")
            
    with col_heavy:
        if not heavy.empty:
            row = heavy.iloc[0]
            st.subheader("Забитый Канал (Тяжелое ядро)")
            st.error(f"**Изотоп:** {row['Isotope']}\n\n**Протонов (Z):** {row['Z']}\n\n**Топологический Долг:** {row['ΔK Debt (MeV)']:.2f} MeV\n\n**Время распада:** $10^{{{row['Log10(T_1/2)']:.2f}}}$ секунд")
            st.markdown("*Плотная решетка из 80+ протонов создает колоссальный кулоновский импеданс. Удаление ошибки в 5 МэВ требует миллионов тактов ожидания.*")
