import streamlit as st
import numpy as np
import pandas as pd
import math

# --- МАТЕМАТИЧЕСКОЕ ЯДРО (Без внешних зависимостей) ---
def is_prime_manual(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_divisors_manual(n):
    divs = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i*i != n:
                divs.append(n // i)
    return sorted(divs)

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Skyrmion Pro Lab", layout="wide")

st.title("🌪️ Skyrmion Pro: Topological Engineering")
st.markdown("**Simureality Circuit 2:** Select a material from the DB, then fine-tune parameters to find the Prime Resonance.")

# --- ЗАГРУЗКА БАЗЫ ДАННЫХ ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("scyrmions_db.csv")
        return df
    except FileNotFoundError:
        st.error("Файл scyrmions_db.csv не найден! Создайте его в репозитории.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- БОКОВАЯ ПАНЕЛЬ: ВЫБОР И ПОДСТРОЙКА ---
    st.sidebar.header("🎛️ Control Panel")
    
    # 1. Выбор материала
    material_names = df["Material"].tolist()
    selected_name = st.sidebar.selectbox("Load Preset", material_names)
    
    # Получаем данные из базы
    row = df[df["Material"] == selected_name].iloc[0]
    
    # --- ЛОГИКА СОСТОЯНИЯ (SESSION STATE) ---
    # Чтобы параметры обновлялись при смене материала, но не сбрасывались при ручном вводе
    if "last_selected" not in st.session_state or st.session_state.last_selected != selected_name:
        st.session_state.last_selected = selected_name
        st.session_state.A = float(row["A_stiffness"])
        st.session_state.D = float(row["D_dmi"])
        st.session_state.a = float(row["a_lattice"])

    st.sidebar.markdown("---")
    st.sidebar.write("⚙️ **Fine-Tuning (Live)**")
    
    # 2. Ручки управления (связаны с session_state)
    A_val = st.sidebar.number_input("Stiffness A (pJ/m)", value=st.session_state.A, step=0.01, format="%.2f", key="A_input")
    D_val = st.sidebar.number_input("DMI D (mJ/m²)", value=st.session_state.D, step=0.01, format="%.2f", key="D_input")
    a_val = st.sidebar.number_input("Lattice a (nm)", value=st.session_state.a, step=0.001, format="%.3f", key="a_input")

    # Обновляем описание
    st.sidebar.info(f"**Type:** {row['Type']}\n\n{row['Description']}")

    # --- РАСЧЕТ ---
    # 1. Физика
    pitch_nm = (4 * np.pi * A_val) / D_val
    radius_nm = pitch_nm / 2

    # 2. Геометрия Simureality
    area_skyrmion = np.pi * (radius_nm ** 2)
    area_node = a_val ** 2
    num_nodes_raw = area_skyrmion / area_node
    num_nodes = int(round(num_nodes_raw))

    # 3. Анализ Чисел
    is_prime = is_prime_manual(num_nodes)
    divisors = get_divisors_manual(num_nodes)
    num_divs = len(divisors)

    # --- ВЫВОД РЕЗУЛЬТАТОВ (ГЛАВНЫЙ ЭКРАН) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vortex Radius (R)", f"{radius_nm:.2f} nm", delta=None)
    with col2:
        # Показываем отклонение от "заводских" настроек базы
        diff_nodes = num_nodes - int(round((np.pi * ((4*np.pi*row["A_stiffness"]/row["D_dmi"])/2)**2) / row["a_lattice"]**2))
        st.metric("Grid Nodes (N)", f"{num_nodes}", delta=f"{diff_nodes} vs Preset" if diff_nodes != 0 else None)
    with col3:
        if is_prime:
            st.success("💎 PRIME")
        elif num_divs <= 4:
            st.warning("💾 ROBUST")
        else:
            st.error("⚠️ UNSTABLE")

    st.divider()

    # --- ВЕРДИКТ ---
    st.subheader("Simureality Verdict")
    
    if is_prime:
        st.success(f"### 💎 PRIME TOPOLOGY DETECTED: {num_nodes}")
        st.markdown(f"**Status: ABSOLUTE STABILITY.**\n\nГеометрия {selected_name} (с текущими настройками) образует неразрушимый узел.")
    else:
        # Поиск ближайшего простого числа
        lower_prime = num_nodes - 1
        while not is_prime_manual(lower_prime): lower_prime -= 1
        
        upper_prime = num_nodes + 1
        while not is_prime_manual(upper_prime): upper_prime += 1
        
        dist_down = num_nodes - lower_prime
        dist_up = upper_prime - num_nodes
        
        target = lower_prime if dist_down < dist_up else upper_prime
        diff = target - num_nodes
        action = "Expand (+)" if diff > 0 else "Shrink (-)"
        
        if num_divs <= 4 and num_nodes % 2 == 0:
             st.info(f"### 💾 SEMI-PRIME: {num_nodes} = 2 × {num_nodes//2}")
             st.write("Идеально для памяти (FeGe style).")
        else:
             st.error(f"### ⚠️ COMPOSITE: {num_nodes} ({num_divs} divisors)")
             st.write("Структура нестабильна.")

        st.markdown(f"""
        **Optimization Strategy:**
        Чтобы попасть в **Prime Resonance ({target})**, нужно изменить геометрию на **{abs(diff)} узлов**.
        👉 Попробуйте изменить **A** на `{A_val + (diff * 0.001):.3f}` или **a** (нагрев).
        """)

    # --- ЛАНДШАФТ ---
    st.write("---")
    st.write("⛰️ **Stability Landscape**")
    
    range_width = 15
    start_x = max(1, num_nodes - range_width)
    end_x = num_nodes + range_width
    
    x_vals = list(range(start_x, end_x + 1))
    y_vals = []
    colors = []
    
    for x in x_vals:
        if x == num_nodes:
            colors.append("#FF4B4B") # Красный (Мы здесь)
            val = 50 # Маркер
        elif is_prime_manual(x):
            colors.append("#00CC96") # Зеленый (Prime)
            val = 100
        else:
            colors.append("#636EFA") # Синий (Обычный)
            d = len(get_divisors_manual(x))
            val = max(10, 80 - d*8)
        y_vals.append(val)

    chart_data = pd.DataFrame({"Nodes": x_vals, "Stability": y_vals, "Color": colors})
    
    # Используем Altair или простой bar_chart (здесь простой, но цвета через Streamlit сложно передать в нативном bar_chart, 
    # поэтому просто покажем пики)
    st.bar_chart(chart_data.set_index("Nodes")["Stability"])
    st.caption("Пики = Простые Числа. Текущее положение в центре.")

else:
    st.warning("Загрузите базу данных scyrmions_db.csv")
