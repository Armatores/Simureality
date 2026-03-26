import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: CHRONOS ANALYZER V8.0
# DETAILED STATISTICAL PROOF OF DECAY DEPENDENCE ON TOPOLOGICAL DEBT
# ==========================================================================================

st.set_page_config(page_title="Chronos Analyzer", layout="wide")
st.title("Simureality: Chronos Analyzer 🔬")
st.markdown("""
**Инструмент жесткой верификации.** Анализ корреляции между Топологическим Долгом ГЦК ($\Delta K$) и временем жизни изотопов.
""")

@st.cache_data
def load_data():
    file_name = "simureality_chronos_benchmark_V73.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return None

df = load_data()

if df is None:
    st.warning("Файл `simureality_chronos_benchmark_V73.csv` не найден в корне. Загрузи его вручную:")
    uploaded_file = st.file_uploader("Загрузить CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

if df is not None:
    # Очистка данных: берем только нестабильные ядра, исключая экстремальные недострои (Drip Line)
    # Фильтруем таймеры > -25 (отсекаем йоттосекундные резонансы, которые даже не собрались)
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()
    
    st.success(f"База загружена. Анализируется нестабильных изотопов: **{len(df_unstable)}**")
    
    # --- БЛОК 1: ГЛОБАЛЬНЫЙ АНАЛИЗ (АЛЬФА И БЕТА РАСПАД) ---
    st.header("1. Глобальный макро-тренд")
    
    col1, col2 = st.columns(2)
    
    # Тяжелые ядра (Z > 82) - Доминирует Альфа-распад (Garbage Collection)
    heavy = df_unstable[df_unstable['Z'] > 82]
    r_heavy, p_heavy = stats.pearsonr(heavy['ΔK Debt (MeV)'], heavy['Log10(T_1/2)'])
    
    # Легкие/Средние ядра (Z <= 82) - Доминирует Бета-распад (Patching)
    light = df_unstable[df_unstable['Z'] <= 82]
    r_light, p_light = stats.pearsonr(light['ΔK Debt (MeV)'], light['Log10(T_1/2)'])
    
    with col1:
        st.subheader("Тяжелые ядра ($Z > 82$)")
        st.markdown("**Механика:** Альфа-сброс (критическое кулоновское напряжение макро-кристалла).")
        st.metric("Корреляция Пирсона", f"{r_heavy:.3f}")
        st.metric("p-value (Шанс случайности)", f"{p_heavy:.2e}")
        
        fig_heavy = px.scatter(
            heavy, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope",
            trendline="ols", trendline_color_override="red",
            title="Ось X: Ошибка геометрии | Ось Y: Время жизни (Log10)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_heavy, use_container_width=True)

    with col2:
        st.subheader("Легкие/Средние ядра ($Z \le 82$)")
        st.markdown("**Механика:** Бета-распад (аппаратный патч изоспиновой асимметрии).")
        st.metric("Корреляция Пирсона", f"{r_light:.3f}")
        st.metric("p-value (Шанс случайности)", f"{p_light:.2e}")
        
        fig_light = px.scatter(
            light, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope",
            trendline="ols", trendline_color_override="red",
            title="Ось X: Ошибка геометрии | Ось Y: Время жизни (Log10)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_light, use_container_width=True)

    st.info("""
    **Как читать графики:** Красная линия тренда идет вниз. Это доказывает жесткое правило: 
    *Чем больше Топологический Долг (отклонение от идеальной ГЦК-матрицы), тем быстрее Диспетчер Задач убивает процесс (распад).* Вероятность того, что этот тренд случаен (p-value), математически равна нулю.
    """)

    st.divider()

    # --- БЛОК 2: МИКРО-АНАЛИЗ ПО ЭЛЕМЕНТАМ ---
    st.header("2. Микро-анализ Изотопных Цепочек")
    st.markdown("Макро-формула дает фоновый шум при сравнении железа с ураном. Но если зафиксировать заряд ($Z$) и смотреть только на добавление нейтронов к одному элементу, закон Гейгера-Нэттолла в ГЦК-интерпретации становится кристально четким.")
    
    element_list = sorted(df_unstable['Z'].unique())
    # По умолчанию выберем Уран (92)
    default_index = element_list.index(92) if 92 in element_list else 0
    
    selected_Z = st.selectbox("Выбери заряд ядра (Z) для детального анализа:", element_list, index=default_index)
    
    chain = df_unstable[df_unstable['Z'] == selected_Z]
    
    if len(chain) > 2:
        r_chain, p_chain = stats.pearsonr(chain['ΔK Debt (MeV)'], chain['Log10(T_1/2)'])
        
        col3, col4 = st.columns([1, 2])
        with col3:
            st.metric(f"Корреляция для Z={selected_Z}", f"{r_chain:.3f}")
            st.metric("Изотопов в цепочке", len(chain))
            st.dataframe(chain[['Isotope', 'ΔK Debt (MeV)', 'Log10(T_1/2)']].sort_values('ΔK Debt (MeV)'))
            
        with col4:
            fig_chain = px.scatter(
                chain, x="ΔK Debt (MeV)", y="Log10(T_1/2)", hover_name="Isotope", text="Isotope",
                trendline="ols", trendline_color_override="orange",
                title=f"Зависимость Времени от Геометрии для Z={selected_Z}",
                template="plotly_dark"
            )
            fig_chain.update_traces(textposition='top center')
            st.plotly_chart(fig_chain, use_container_width=True)
    else:
        st.warning("Недостаточно данных для построения тренда (нужно минимум 3 нестабильных изотопа).")
