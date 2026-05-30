import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==============================================================================
# SIMUREALITY: 3D-TIME PHASE DESYNCHRONIZATION ENGINE (CHRONOS V9)
# Merging Topological Debt (ΔK) with the Theorem of 180° GC Timeout
# ==============================================================================

# Аппаратный лимит: 55 MeV долга вызывает Kernel Panic (сдвиг 180 градусов и Jitter = 0.5)
K_CRITICAL_MEV = 55.0  

st.set_page_config(page_title="Chronos V9: 3D-Time Engine", layout="wide", page_icon="⏱️")

@st.cache_data
def load_chronos_data():
    file_name = "simureality_chronos_v8_benchmark.csv"
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        # Фильтруем пустые значения
        df = df.dropna(subset=['ΔK Debt (MeV)', 'Log10(T_1/2)'])
        return df
    return None

def compute_3d_phase_shift(df):
    if df is None or df.empty:
        return df
    
    # 1. Расчет истинного 3D-Джиттера через Топологический Долг
    # Jitter = 0.5 - это 180 градусов (предел системы)
    df['3D_Jitter'] = (df['ΔK Debt (MeV)'] / (K_CRITICAL_MEV * 2)).clip(0, 0.4999)
    
    # 2. Фазовый Ресурс (Phase Margin)
    df['Phase_Margin'] = 1.0 - 2.0 * df['3D_Jitter']
    
    # 3. Угол Рассинхрона векторов Времени (tx, ty, tz)
    df['Desync_Angle_Deg'] = df['3D_Jitter'] * 360.0
    
    # Сортировка для красоты
    return df.sort_values('Desync_Angle_Deg')

# --- ИНТЕРФЕЙС ---
st.title("⏱️ Chronos V9: Механика 3D-Времени и Kernel Panic")
st.markdown("""
**Доказательство Детерминированного Распада:** Время — это не скаляр, а трехмерный вектор обновления координат $(t_x, t_y, t_z)$. 
Топологический Долг $(\\Delta K)$ физически искажает геометрию графа, вызывая расхождение фаз времени. **Каждый 1 МэВ долга сдвигает векторы времени на $\\approx 3.27^\\circ$.** При достижении $180^\\circ$ возникает аппаратный конфликт (Kernel Panic), и Сборщик Мусора мгновенно удаляет процесс.
""")

df_raw = load_chronos_data()

if df_raw is None:
    st.error("Файл `simureality_chronos_v8_benchmark.csv` не найден. Пожалуйста, загрузите базу данных.")
else:
    df = compute_3d_phase_shift(df_raw)
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()

    tab1, tab2, tab3 = st.tabs([
        "🔬 Изотопные Цепи (Вектор Смерти)", 
        "🌌 Глобальный Граф Рассинхрона", 
        "🗄️ Лог Сборщика Мусора"
    ])

    with tab1:
        st.subheader("Фазовый распад элемента (Микро-анализ)")
        st.markdown("Выберите элемент, чтобы увидеть идеальную зависимость: как рост Угла Рассинхрона обрушивает таймер жизни.")
        
        elements = sorted(df_unstable['Z'].unique())
        default_index = elements.index(6) if 6 in elements else 0
        selected_Z = st.selectbox("Выберите заряд ядра (Z):", elements, index=default_index)
        
        chain = df_unstable[df_unstable['Z'] == selected_Z]
        
        if len(chain) > 2:
            fig1 = px.scatter(
                chain, x="Desync_Angle_Deg", y="Log10(T_1/2)", 
                hover_name="Isotope", text="Isotope",
                title=f"Траектория Kernel Panic для Z={selected_Z}",
                labels={"Desync_Angle_Deg": "Угол Рассинхрона 3D-Времени (°)", "Log10(T_1/2)": "Log10(T) в секундах"},
                trendline="ols", trendline_color_override="#FF1744", template="plotly_dark"
            )
            fig1.update_traces(textposition='top right', marker=dict(size=14, color='#00E676', line=dict(width=2, color='white')))
            fig1.add_vline(x=180, line_dash="dash", line_color="red", annotation_text="Kernel Panic (180°)")
            
            # Добавляем "безопасную зону" для стабильных (если есть)
            stable_chain = df[(df['Z'] == selected_Z) & (df['Status'] == 'Stable')]
            if not stable_chain.empty:
                fig1.add_trace(px.scatter(stable_chain, x="Desync_Angle_Deg", y=[30]*len(stable_chain), text="Isotope").data[0])
                fig1.data[-1].marker.color = 'yellow'
                fig1.data[-1].marker.symbol = 'star'
                fig1.data[-1].name = 'Stable (∞)'

            st.plotly_chart(fig1, use_container_width=True)
            st.info(f"**Вывод:** Изотопы Z={selected_Z} выстраиваются в жесткую фазовую траекторию. Чем шире угол между осями 3D-времени, тем быстрее Матрица отзывает процесс.")
        else:
            st.warning("Слишком мало данных для отрисовки тренда цепи.")

    with tab2:
        st.subheader("Глобальный сдвиг фаз (Все элементы)")
        st.markdown("Здесь собрана вся таблица Менделеева. Видно, как легкие и тяжелые ядра стремятся к единому горизонту событий ($180^\\circ$).")
        
        fig2 = px.scatter(
            df_unstable, x="Desync_Angle_Deg", y="Log10(T_1/2)", color="Z", 
            hover_name="Isotope", hover_data=["ΔK Debt (MeV)"],
            color_continuous_scale="Turbo", template="plotly_dark",
            title="Глобальная Карта Деградации 3D-Времени",
            labels={"Desync_Angle_Deg": "Угол Рассинхрона (°)", "Log10(T_1/2)": "Время жизни Log10(T)"}
        )
        fig2.add_vline(x=180, line_dash="dash", line_color="red")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### Системный лог 3D-Времени")
        display_cols = ['Isotope', 'Z', 'A', 'Status', 'ΔK Debt (MeV)', '3D_Jitter', 'Phase_Margin', 'Desync_Angle_Deg', 'Log10(T_1/2)']
        format_dict = {'ΔK Debt (MeV)': '{:.3f}', '3D_Jitter': '{:.4f}', 'Phase_Margin': '{:.4f}', 'Desync_Angle_Deg': '{:.2f}°', 'Log10(T_1/2)': '{:.2f}'}
        
        st.dataframe(
            df[display_cols].style
            .format(format_dict)
            .background_gradient(subset=['Desync_Angle_Deg'], cmap='Reds')
            .background_gradient(subset=['ΔK Debt (MeV)'], cmap='Oranges'),
            use_container_width=True
        )
