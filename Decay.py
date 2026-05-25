import streamlit as st
import pandas as pd
import numpy as np

# --- SIMUREALITY ONTOLOGICAL CONSTANTS ---
GAMMA_SYS = 1.0418          # Системный налог на 3D-рендер (Плата за десинхронизацию)
JITTER_COST = 0.0131        # Энергия динамического шума на один открытый порт (МэВ)
MAGIC_NUMBERS = [2, 8, 20, 28, 50, 82, 126, 184] # Идеальные геометрические сборки ГЦК

st.set_page_config(page_title="Grid Physics: f_grid Topology Compiler", layout="wide")

def get_asymmetry(nucleons):
    """
    Вычисляет количество нескомпенсированных портов относительно 
    ближайшей идеальной геометрической сборки (Магического числа).
    """
    distances = [abs(nucleons - m) for m in MAGIC_NUMBERS]
    return min(distances)

def compile_f_grid(Z, N):
    """
    Дискретный аналог функции Бориса Кригера f_comp(G).
    Считает балансировку открытых портов ядра.
    """
    asym_Z = get_asymmetry(Z)
    asym_N = get_asymmetry(N)
    
    # Общая векторная асимметрия (открытые порты)
    total_asymmetry = asym_Z + asym_N
    
    # Grid Compensation Function
    # Если асимметрия = 0, f_grid = 1.0 (Идеальное Платоново/ГЦК тело)
    f_grid = 1.0 - (total_asymmetry * JITTER_COST * GAMMA_SYS)
    
    # Расчет вероятности распада (Топологического долга)
    # Чем больше асимметрия, тем быстрее переполняется буфер
    topological_debt = total_asymmetry * (GAMMA_SYS ** total_asymmetry)
    
    return f_grid, total_asymmetry, topological_debt, asym_Z, asym_N

# --- ИНТЕРФЕЙС ---
st.title("🌌 Grid Physics: Discrete Topology Compiler ($f_{grid}$)")
st.markdown("""
**Заменяет 928 страниц непрерывной топологии (модель Скирма) на алгоритм подсчета открытых ГЦК-портов.**
$f_{grid} = 1.0$ означает идеальную аппаратную сборку (нулевой дипольный/квадрупольный момент).
""")

col1, col2 = st.columns(2)

with col1:
    st.header("Ввод данных узла")
    Z = st.number_input("Протоны (Z)", min_value=1, max_value=120, value=82, step=1)
    N = st.number_input("Нейтроны (N)", min_value=1, max_value=184, value=126, step=1)
    
with col2:
    st.header("Системный Монитор Матрицы")
    f_grid, total_asym, debt, a_z, a_n = compile_f_grid(Z, N)
    
    # Визуализация статуса
    if total_asym == 0:
        st.success("✅ СТАТУС: PERFECT CLOSURE (Дважды Магическое Ядро)")
        st.info("Геометрия полностью сбалансирована. Аппаратные порты замкнуты. f_grid = 1.0")
    elif a_z == 0 or a_n == 0:
        st.warning("⚠️ СТАТУС: PARTIAL CLOSURE (Магическое Ядро)")
        st.write("Одна из подсетей сбалансирована, но есть общий джиттер.")
    else:
        st.error("🚨 СТАТУС: ASYMMETRY DETECTED (Нестабильное/Фонящее Ядро)")
        st.write("Накапливается топологический долг. Ожидается Exception (Распад).")

st.markdown("---")
st.subheader("📊 Логи Компилятора")

m1, m2, m3, m4 = st.columns(4)
m1.metric("f_grid (Compensation)", f"{f_grid:.4f}")
m2.metric("Нескомпенсированных вокселей", f"{total_asym}")
m3.metric("Топологический Долг (ΣK)", f"{debt:.2f}")
m4.metric("Jitter Penalty", f"-{(total_asym * JITTER_COST):.4f} MeV")

st.markdown("""
### Декомпиляция логики Бориса Кригера:
В классической теории Скирмионов для доказательства $f_{comp} = 1$ для Свинца-208 ($Z=82, N=126$) требуются сложные расчеты матриц вращения $SO(3)$, чтобы доказать обнуление мультипольных моментов.
**В Grid Physics:** Мы просто проверяем замыкание графа. $Z=82$ (идеальная оболочка), $N=126$ (идеальная оболочка). Нескомпенсированных векторов = 0. Система не излучает джиттер.
""")
