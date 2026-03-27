import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==========================================================================================
# SIMUREALITY: GC ROUTING EXTRACTOR V3.0 (3D VECTOR TIME EDITION)
# Декомпиляция Трехмерного Времени Вакуума (3D Time Matrix)
# ==========================================================================================

st.set_page_config(page_title="GC Vector Time 3D", layout="wide")
st.title("Simureality: 3D-Время Сборщика Мусора 🧊")
st.markdown("""
Доказательство векторной природы времени. Макро-время (скаляр) — это лишь длина 3D-вектора вычислений матрицы.
Здесь мы разбиваем время на оси: **X (Удаление Ошибки)**, **Y (Сетевой Лаг)** и **Z (Синхронизация Спина)**.
""")

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

# --- 1. ОЧИСТКА И РАСЧЕТ ВЕКТОРОВ ВРЕМЕНИ ---
df_unstable = df[(df['Status'] == 'Unstable') & (df['Log10(T_1/2)'] > -25)].copy()

# Базовые параметры
df_unstable['N'] = df_unstable['A'] - df_unstable['Z']
df_unstable['Unpaired_Ports'] = (df_unstable['Z'] % 2) + (df_unstable['N'] % 2)
df_unstable['sqrt_dK'] = np.sqrt(np.maximum(df_unstable['ΔK Debt (MeV)'], 0.1))

# Используем вытащенные нами константы (для Альфа-дампа тяжелых ядер Z>82, как пример жесткой физики)
# Если хочешь посмотреть всю базу, мы усредним веса для визуализации 3D-пространства
T_BASE = 11.225
Z_IMP = -0.066
E_POW = -0.783
P_LOCK = -0.080

# РАСЧЕТ 3D-ОСЕЙ ВРЕМЕНИ (КОМПОНЕНТЫ ВЕКТОРА)
# 1. Ось X: Вектор удаления Топологического Долга (Стремится вниз)
df_unstable['T_x (Error Vector)'] = E_POW * df_unstable['sqrt_dK']

# 2. Ось Y: Вектор Сетевого Импеданса / Лага (Стремится вверх)
df_unstable['T_y (Lag Vector)'] = Z_IMP * df_unstable['Z']

# 3. Ось Z: Вектор Синхронизации Спина (Динамический флаг)
df_unstable['T_z (Sync Vector)'] = P_LOCK * df_unstable['Unpaired_Ports']

# Макро-время (Длина вектора)
df_unstable['3D_Magnitude'] = np.sqrt(df_unstable['T_x (Error Vector)']**2 + 
                                      df_unstable['T_y (Lag Vector)']**2 + 
                                      df_unstable['T_z (Sync Vector)']**2)

st.header("1. Трехмерная маршрутизация распада")
st.markdown("Покрути этот 3D-график. Ты увидишь, что изотопы не раскиданы случайно. Они образуют жесткие геометрические плоскости в 3D-пространстве вычислений.")

# --- 2. 3D ВИЗУАЛИЗАЦИЯ ---
fig = px.scatter_3d(
    df_unstable, 
    x='T_x (Error Vector)', 
    y='T_y (Lag Vector)', 
    z='T_z (Sync Vector)',
    color='Log10(T_1/2)',
    hover_name='Isotope',
    hover_data=['Z', 'ΔK Debt (MeV)', 'Unpaired_Ports'],
    labels={
        "T_x (Error Vector)": "Ось X: Ошибка (ΔK)",
        "T_y (Lag Vector)": "Ось Y: Сетевой Лаг (Z)",
        "T_z (Sync Vector)": "Ось Z: Синхронизация (Spin)",
        "Log10(T_1/2)": "Макро-Время (Скаляр)"
    },
    title="3D-Вектор Времени Вакуума",
    template="plotly_dark",
    color_continuous_scale="Turbo",
    opacity=0.8
)

fig.update_traces(marker=dict(size=4))
fig.update_layout(scene=dict(
    xaxis_title='Ось X (Удаление Ошибки)',
    yaxis_title='Ось Y (Импеданс Сети)',
    zaxis_title='Ось Z (Синхронизация Портов)'
))

st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- 3. ВЫВОД АНАЛИТИКИ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Что мы сейчас видим?")
    st.info("""
    Вместо того чтобы сплющивать вычисления вакуума в 1D-линейку секунд, 
    мы развернули их в реальное 3D-пространство ГЦК-матрицы.
    * **Цвет точки** — это то 1D-время, которое видит детектор.
    * **Координаты точки** — это реальные такты процессора по трем осям.
    """)

with col2:
    st.subheader("Конец случайности")
    st.error("""
    Если покрутить график так, чтобы смотреть строго вдоль одной из осей (имитируя 1D-детектор), 
    точки сольются в хаотичное облако. Но в 3D — это детерминированные поверхности. 
    **Вакуум не играет в кости. Он вычисляет векторы.**
    """)
