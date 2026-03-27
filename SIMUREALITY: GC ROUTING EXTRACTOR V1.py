import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: GC ROUTING EXTRACTOR V2.0 (DUAL PROTOCOL)
# Декомпиляция аппаратных констант с разделением на Software Patch и Hardware Dump
# ==========================================================================================

st.set_page_config(page_title="GC Routing Extractor V2", layout="wide")
st.title("Simureality: Декомпилятор Сборщика Мусора 🗑️ (Dual Protocol)")
st.markdown("""
Доказательство двухуровневой обработки исключений в 3D-матрице.
Мы разделяем потоки: **Аппаратный сброс (Альфа-распад, $Z > 82$)** и **Программный патч (Бета-распад, $Z \le 82$)**.
""")

@st.cache_data
def load_data():
    file_name = "simureality_chronos_benchmark_V73.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return None

df = load_data()

if df is None:
    st.warning("Критическая ошибка: Файл `simureality_chronos_benchmark_V73.csv` не найден в корне.")
    st.stop()

# --- 1. ОЧИСТКА И ПОДГОТОВКА ДАННЫХ ---
df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()

# Считаем открытые порты (Parity Lock) и мощность ошибки
df_unstable['N'] = df_unstable['A'] - df_unstable['Z']
df_unstable['Unpaired_Ports'] = (df_unstable['Z'] % 2) + (df_unstable['N'] % 2)
df_unstable['sqrt_dK'] = np.sqrt(np.maximum(df_unstable['ΔK Debt (MeV)'], 0.1))

# РАЗДЕЛЕНИЕ ПОТОКОВ (МАРШРУТИЗАЦИЯ)
heavy = df_unstable[df_unstable['Z'] > 82].copy()  # Hardware Dump (Alpha)
light = df_unstable[df_unstable['Z'] <= 82].copy() # Software Patch (Beta)

# --- 2. ОБУЧЕНИЕ МОДЕЛЕЙ (scikit-learn) ---
def fit_gc_model(data):
    X = np.column_stack((data['Z'], data['sqrt_dK'], data['Unpaired_Ports']))
    y = data['Log10(T_1/2)'].values
    reg = LinearRegression().fit(X, y)
    r2 = reg.score(X, y)
    data['Predicted_Log10(T)'] = reg.predict(X)
    return reg, r2

reg_heavy, r2_heavy = fit_gc_model(heavy)
reg_light, r2_light = fit_gc_model(light)

# --- 3. ИНТЕРФЕЙС АНАЛИЗА ---
st.header("1. Декомпиляция констант по протоколам")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Hardware Dump (Альфа-распад)")
    st.markdown("Тяжелые ядра ($Z > 82$). Отрыв целого Альфа-тетраэдра. Критически важен Импеданс Сети ($Z$).")
    st.metric("Точность (R²)", f"{r2_heavy:.4f}")
    
    st.code(f"""
T_base (Базовый такт) : {reg_heavy.intercept_:.3f}
Z_imp  (Сопротивление): {reg_heavy.coef_[0]:.3f}  <-- ПРОБКА
E_pow  (Сила сброса)  : {reg_heavy.coef_[1]:.3f}
P_lock (Штраф порта)  : {reg_heavy.coef_[2]:.3f}
    """)

with col2:
    st.subheader("💻 Software Patch (Бета-распад)")
    st.markdown("Легкие/Средние ($Z \le 82$). Локальная перепрошивка узла (n ↔ p). Импеданс сети не мешает.")
    st.metric("Точность (R²)", f"{r2_light:.4f}")
    
    st.code(f"""
T_base (Базовый такт) : {reg_light.intercept_:.3f}
Z_imp  (Сопротивление): {reg_light.coef_[0]:.3f}  <-- ПОЧТИ НЕТ ПРОБКИ
E_pow  (Сила сброса)  : {reg_light.coef_[1]:.3f}
P_lock (Штраф порта)  : {reg_light.coef_[2]:.3f}
    """)

st.divider()

# --- 4. ВИЗУАЛИЗАЦИЯ ДВУХ ПОТОКОВ ---
st.header("2. Визуализация очищенных потоков маршрутизации")
st.markdown("Теперь, когда мы не заставляем вакуум считать программные патчи по формулам аппаратного сброса, облако точек вытягивается в предсказуемые диагонали.")

tab1, tab2 = st.tabs(["Аппаратный Сброс (Тяжелые)", "Программный Патч (Легкие/Средние)"])

with tab1:
    fig_h = px.scatter(
        heavy, x="Predicted_Log10(T)", y="Log10(T_1/2)", color="Unpaired_Ports",
        hover_name="Isotope", hover_data=["Z", "A", "ΔK Debt (MeV)"],
        labels={"Predicted_Log10(T)": "Расчет (Hardware Dump)", "Log10(T_1/2)": "AME2020"},
        title="Hardware Dump: Удаление Альфа-ошибок через забитую шину Z",
        template="plotly_dark", color_continuous_scale="Reds"
    )
    fig_h.add_shape(type="line", line=dict(dash='dash', color='white'), x0=-15, y0=-15, x1=25, y1=25)
    st.plotly_chart(fig_h, use_container_width=True)

with tab2:
    fig_l = px.scatter(
        light, x="Predicted_Log10(T)", y="Log10(T_1/2)", color="Unpaired_Ports",
        hover_name="Isotope", hover_data=["Z", "A", "ΔK Debt (MeV)"],
        labels={"Predicted_Log10(T)": "Расчет (Software Patch)", "Log10(T_1/2)": "AME2020"},
        title="Software Patch: Перепрошивка изоспина без сильного влияния Z",
        template="plotly_dark", color_continuous_scale="Blues"
    )
    fig_l.add_shape(type="line", line=dict(dash='dash', color='white'), x0=-25, y0=-25, x1=25, y1=25)
    st.plotly_chart(fig_l, use_container_width=True)
