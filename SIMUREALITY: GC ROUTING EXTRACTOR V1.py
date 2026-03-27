import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: GC ROUTING EXTRACTOR V4.0 (UNIFIED CORE)
# Декомпиляция констант + 3D Векторное Время
# ==========================================================================================

st.set_page_config(page_title="GC Extractor V4", layout="wide")
st.title("Simureality: Архитектура Сборщика Мусора 🗑️ (V4.0)")

@st.cache_data
def load_data():
    file_name = "simureality_chronos_benchmark_V73.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return None

df = load_data()

if df is None:
    st.warning("Критическая ошибка: Файл базы данных не найден.")
    st.stop()

# --- 1. ОЧИСТКА И ПОДГОТОВКА ДАННЫХ ---
df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()
df_unstable['N'] = df_unstable['A'] - df_unstable['Z']
df_unstable['Unpaired_Ports'] = (df_unstable['Z'] % 2) + (df_unstable['N'] % 2)
df_unstable['sqrt_dK'] = np.sqrt(np.maximum(df_unstable['ΔK Debt (MeV)'], 0.1))

# МАРШРУТИЗАЦИЯ
heavy = df_unstable[df_unstable['Z'] > 82].copy()  # Hardware Dump
light = df_unstable[df_unstable['Z'] <= 82].copy() # Software Patch

# --- 2. ДЕКОМПИЛЯЦИЯ (РЕГРЕССИЯ) ---
def fit_gc_model(data):
    X = np.column_stack((data['Z'], data['sqrt_dK'], data['Unpaired_Ports']))
    y = data['Log10(T_1/2)'].values
    reg = LinearRegression().fit(X, y)
    r2 = reg.score(X, y)
    data['Predicted_Log10(T)'] = reg.predict(X)
    return reg, r2

reg_heavy, r2_heavy = fit_gc_model(heavy)
reg_light, r2_light = fit_gc_model(light)

st.header("1. Аппаратные константы вакуума")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Hardware Dump (Z > 82)")
    st.metric("Точность (R²)", f"{r2_heavy:.4f}")
    st.code(f"""
T_base: {reg_heavy.intercept_:.3f}
Z_imp : {reg_heavy.coef_[0]:.3f}
E_pow : {reg_heavy.coef_[1]:.3f}
P_lock: {reg_heavy.coef_[2]:.3f}
    """)

with col2:
    st.subheader("💻 Software Patch (Z <= 82)")
    st.metric("Точность (R²)", f"{r2_light:.4f}")
    st.code(f"""
T_base: {reg_light.intercept_:.3f}
Z_imp : {reg_light.coef_[0]:.3f}
E_pow : {reg_light.coef_[1]:.3f}
P_lock: {reg_light.coef_[2]:.3f}
    """)

st.divider()

# --- 3. 3D ВЕКТОРНОЕ ВРЕМЯ ---
st.header("2. Трехмерная проекция времени (3D Matrix Time)")
st.markdown("Здесь макро-время разбито на ортогональные векторы вычислений с использованием констант, полученных выше.")

# Считаем 3D-векторы для тяжелых ядер на основе их реальных констант
heavy['T_x (Error)'] = reg_heavy.coef_[1] * heavy['sqrt_dK']
heavy['T_y (Lag)'] = reg_heavy.coef_[0] * heavy['Z']
heavy['T_z (Sync)'] = reg_heavy.coef_[2] * heavy['Unpaired_Ports']

fig_3d = px.scatter_3d(
    heavy, 
    x='T_x (Error)', y='T_y (Lag)', z='T_z (Sync)',
    color='Log10(T_1/2)', hover_name='Isotope',
    labels={"T_x (Error)": "Ось X: Ошибка", "T_y (Lag)": "Ось Y: Сетевой Лаг", "T_z (Sync)": "Ось Z: Синхронизация Спина"},
    title="3D-Вектор Времени (Hardware Dump Z > 82)",
    template="plotly_dark", color_continuous_scale="Turbo"
)
fig_3d.update_traces(marker=dict(size=4))
st.plotly_chart(fig_3d, use_container_width=True)
