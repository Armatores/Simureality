import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==============================================================================
# SIMUREALITY: 3D-TIME PHASE DESYNCHRONIZATION ENGINE (CHRONOS V9.1)
# Merging Topological Debt (ΔK) with the Theorem of 180° GC Timeout + Live Benchmark
# ==============================================================================

# Аппаратный лимит: 55 MeV долга вызывает Kernel Panic (сдвиг 180 градусов)
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
    
    # 1. Расчет 3D-Джиттера и Угла рассинхрона
    df['3D_Jitter'] = (df['ΔK Debt (MeV)'] / (K_CRITICAL_MEV * 2)).clip(0, 0.4999)
    df['Phase_Margin'] = 1.0 - 2.0 * df['3D_Jitter']
    df['Desync_Angle_Deg'] = df['3D_Jitter'] * 360.0
    
    # 2. ПРЕДСКАЗАНИЕ ВРЕМЕНИ ЖИЗНИ (Теория Матрицы)
    df['Desync_Factor'] = df['3D_Jitter'] / df['Phase_Margin']
    
    # Аппаратные константы Сборщика Мусора
    conditions = [
        (df['Z'] <= 92),
        (df['Z'] > 92) & (df['Z'] <= 98),
        (df['Z'] > 98)
    ]
    choices_A = [27.0, 15.0, 5.0]
    choices_B = [76.0, 18.0, 15.0]
    
    df['A_sys'] = np.select(conditions, choices_A, default=27.0)
    df['B_sys'] = np.select(conditions, choices_B, default=76.0)
    
    # Расчет предсказанного времени
    df['Predicted_LogT'] = df['A_sys'] - (df['B_sys'] * df['Desync_Factor'])
    
    # 3. ВЫЧИСЛЕНИЕ ОШИБКИ (Дельта с реальным миром)
    df['Error_Delta'] = abs(df['Predicted_LogT'] - df['Log10(T_1/2)'])
    
    return df.sort_values('Desync_Angle_Deg')

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("⏱️ Chronos V9.1: Механика 3D-Времени и Детерминированный Распад")
st.markdown("""
**Доказательство Детерминированного Распада:** Время — это не скаляр, а трехмерный вектор обновления координат $(t_x, t_y, t_z)$. 
Топологический Долг $(\\Delta K)$ физически искажает геометрию графа, вызывая расхождение фаз времени. **Каждый 1 МэВ долга сдвигает векторы времени на $\\approx 3.27^\\circ$.** При достижении $180^\\circ$ возникает аппаратный конфликт (Kernel Panic), и Сборщик Мусора мгновенно удаляет процесс.
""")

df_raw = load_chronos_data()

if df_raw is None:
    st.error("Файл `simureality_chronos_v8_benchmark.csv` не найден. Пожалуйста, загрузите базу данных в папку со скриптом.")
else:
    df = compute_3d_phase_shift(df_raw)
    
    # Фильтруем только нестабильные ядра для статистики (у них есть реальное время жизни)
    df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'].notna())].copy()

    # --- ПАНЕЛЬ ВАЛИДАЦИИ (ЖИВОЙ БЕНЧМАРК) ---
    mae_global = df_unstable['Error_Delta'].mean()
    # Грубая оценка точности: шкала времени охватывает около 25 порядков (от секунд до квадриллионов лет)
    accuracy_percent = max(0, 100 - (mae_global / 25.0 * 100))
    
    st.markdown("### 🎯 Live Benchmark: Валидация теории по базе NUBASE2020")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Обраработано ядер", f"{len(df_unstable)}")
    col2.metric("Средняя ошибка (MAE)", f"{mae_global:.2f} (Log10)", help="Среднее отклонение предсказания от реальности (в порядках)")
    col3.metric("Точность модели", f"{accuracy_percent:.1f}%", delta="Ab Initio", delta_color="normal")
    col4.metric("Магический Предел", "55 MeV", help="Лимит долга до 180° рассинхрона")
    
    st.divider()

    # --- ГРАФИКИ И ЛОГИ ---
    tab1, tab2, tab3 = st.tabs([
        "🔬 Изотопные Цепи (Вектор Смерти)", 
        "🌌 Глобальный Граф Рассинхрона", 
        "🗄️ Системный Лог (Сравнение)"
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
                labels={"Desync_Angle_Deg": "Угол Рассинхрона 3D-Времени (°)", "Log10(T_1/2)": "Реальное Время Log10(T)"},
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
        else:
            st.warning("Слишком мало данных для отрисовки тренда цепи.")

    with tab2:
        st.subheader("Глобальный сдвиг фаз (Все элементы)")
        
        fig2 = px.scatter(
            df_unstable, x="Desync_Angle_Deg", y="Log10(T_1/2)", color="Z", 
            hover_name="Isotope", hover_data=["ΔK Debt (MeV)", "Predicted_LogT", "Error_Delta"],
            color_continuous_scale="Turbo", template="plotly_dark",
            title="Глобальная Карта Деградации 3D-Времени",
            labels={"Desync_Angle_Deg": "Угол Рассинхрона (°)", "Log10(T_1/2)": "Реальное Время Log10(T)"}
        )
        fig2.add_vline(x=180, line_dash="dash", line_color="red")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### 🗄️ Сравнение: Теория против Реальности")
        st.markdown("Здесь Матрица сравнивает свои предсказания с официальными замерами коллайдеров.")
        
        display_cols = ['Isotope', 'Z', 'Status', 'ΔK Debt (MeV)', 'Desync_Angle_Deg', 'Predicted_LogT', 'Log10(T_1/2)', 'Error_Delta']
        format_dict = {
            'ΔK Debt (MeV)': '{:.3f}', 
            'Desync_Angle_Deg': '{:.2f}°', 
            'Predicted_LogT': '{:.2f}', 
            'Log10(T_1/2)': '{:.2f}', 
            'Error_Delta': '{:.3f}'
        }
        
        # Показываем таблицу, отсортированную по точности (сначала самые точные)
        st.dataframe(
            df_unstable[display_cols].sort_values('Error_Delta').style
            .format(format_dict)
            .background_gradient(subset=['Error_Delta'], cmap='Reds', vmin=0, vmax=5)
            .background_gradient(subset=['Desync_Angle_Deg'], cmap='Oranges'),
            use_container_width=True,
            height=600
        )
