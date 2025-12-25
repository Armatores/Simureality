import streamlit as st
import numpy as np
import pandas as pd
import math

# --- 1. МАТЕМАТИЧЕСКОЕ ЯДРО (Без внешних зависимостей) ---
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

# --- 2. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Skyrmion Pro Lab", layout="wide")

st.title("🌪️ Skyrmion Pro: Topological Engineering")
st.markdown("**Simureality Circuit 2:** Select a material from the DB, then fine-tune parameters to find the Prime Resonance.")

# --- 3. ЗАГРУЗКА БАЗЫ ДАННЫХ ---
@st.cache_data
def load_data():
    try:
        # Пытаемся загрузить CSV
        df = pd.read_csv("scyrmions_db.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ Файл scyrmions_db.csv не найден! Создайте его в корне репозитория.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. БОКОВАЯ ПАНЕЛЬ (CONTROL PANEL) ---
    st.sidebar.header("🎛️ Control Panel")
    
    # Список материалов
    material_names = df["Material"].tolist()
    
    # Виджет выбора (ключ важен!)
    selected_name = st.sidebar.selectbox("Load Preset", material_names, key="material_selector")
    
    # Получаем данные из базы для текущего выбора
    row = df[df["Material"] == selected_name].iloc[0]
    
    # === ЛОГИКА ОБНОВЛЕНИЯ ПАРАМЕТРОВ (SESSION STATE MAGIC) ===
    # Если мы только что сменили материал в списке, нам нужно ПРИНУДИТЕЛЬНО
    # обновить значения в полях ввода (Input Fields).
    
    if "last_selected_mat" not in st.session_state:
        st.session_state.last_selected_mat = None # Инициализация

    if st.session_state.last_selected_mat != selected_name:
        # Материал изменился! Обновляем состояние.
        st.session_state.last_selected_mat = selected_name
        st.session_state.A_input = float(row["A_stiffness"])
        st.session_state.D_input = float(row["D_dmi"])
        st.session_state.a_input = float(row["a_lattice"])
        st.rerun() # Перезагружаем страницу, чтобы показать новые цифры

    st.sidebar.markdown("---")
    st.sidebar.write("⚙️ **Fine-Tuning (Live)**")
    
    # Поля ввода. Обрати внимание: value здесь не нужно, так как есть key!
    # Значения берутся напрямую из st.session_state[key]
    A_val = st.sidebar.number_input("Stiffness A (pJ/m)", step=0.01, format="%.2f", key="A_input")
    D_val = st.sidebar.number_input("DMI D (mJ/m²)", step=0.01, format="%.2f", key="D_input")
    a_val = st.sidebar.number_input("Lattice a (nm)", step=0.001, format="%.3f", key="a_input")

    # Информация о типе
    st.sidebar.info(f"**Type:** {row['Type']}\n\n{row['Description']}")

    # --- 5. РАСЧЕТНАЯ ЧАСТЬ ---
    # Физика (Magnetic Spiral)
    # L = 4 * pi * A / D
    if D_val == 0: D_val = 0.0001 # Защита от деления на ноль
    pitch_nm = (4 * np.pi * A_val) / D_val
    radius_nm = pitch_nm / 2

    # Геометрия Simureality (Nodes Count)
    area_skyrmion = np.pi * (radius_nm ** 2)
    area_node = a_val ** 2
    num_nodes_raw = area_skyrmion / area_node
    num_nodes = int(round(num_nodes_raw))

    # Анализ Чисел (Number Theory)
    is_prime = is_prime_manual(num_nodes)
    divisors = get_divisors_manual(num_nodes)
    num_divs = len(divisors)

    # --- 6. ВЫВОД РЕЗУЛЬТАТОВ (ГЛАВНЫЙ ЭКРАН) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vortex Radius (R)", f"{radius_nm:.2f} nm")
    with col2:
        # Считаем "эталонное" число для этого материала (из базы), чтобы показать разницу
        preset_pitch = (4 * np.pi * row["A_stiffness"]) / row["D_dmi"]
        preset_nodes = int(round((np.pi * (preset_pitch/2)**2) / row["a_lattice"]**2))
        diff_nodes = num_nodes - preset_nodes
        
        delta_str = f"{diff_nodes:+d} vs Preset" if diff_nodes != 0 else "Exact Preset"
        delta_color = "off" if diff_nodes == 0 else "normal"
        
        st.metric("Grid Nodes (N)", f"{num_nodes}", delta=delta_str, delta_color=delta_color)
        
    with col3:
        if is_prime:
            st.success("💎 PRIME FOUND")
        elif num_divs <= 4:
            st.warning("💾 ROBUST")
        else:
            st.error("⚠️ UNSTABLE")

    st.divider()

    # --- 7. ВЕРДИКТ И РЕКОМЕНДАЦИИ ---
    st.subheader("Simureality Verdict")
    
    if is_prime:
        st.success(f"### 💎 PRIME TOPOLOGY DETECTED: {num_nodes}")
        st.markdown(f"**Status: ABSOLUTE STABILITY.**\n\nГеометрия {selected_name} (с текущими настройками) образует неразрушимый узел.")
    else:
        # Поиск ближайшего простого
        lower_prime = num_nodes - 1
        while not is_prime_manual(lower_prime): lower_prime -= 1
        
        upper_prime = num_nodes + 1
        while not is_prime_manual(upper_prime): upper_prime += 1
        
        dist_down = num_nodes - lower_prime
        dist_up = upper_prime - num_nodes
        
        target = lower_prime if dist_down < dist_up else upper_prime
        diff = target - num_nodes
        
        # Анализ текущего состояния
        if num_divs <= 4 and num_nodes % 2 == 0:
             st.info(f"### 💾 SEMI-PRIME: {num_nodes} = 2 × {num_nodes//2}")
             st.write("Статус: **Rewritable Memory** (Как FeGe). Идеальный баланс.")
        else:
             st.error(f"### ⚠️ COMPOSITE: {num_nodes} ({num_divs} divisors)")
             st.write("Статус: **Instability / Decay**. Вихрь слишком рыхлый.")

        # Стратегия оптимизации
        st.markdown(f"""
        ---
        **🎯 Optimization Strategy:**
        Nearest Prime Attractor: **{target} nodes** (Difference: **{abs(diff)}**).
        """)
        
        # Расчет подсказки
        # Если нужно увеличить N, нужно увеличить A или уменьшить D, или уменьшить a
        # Примерная дельта для A:
        # N ~ A^2 -> dN/dA ~ 2A. dA ~ dN / 2A (грубо, но для подсказки пойдет)
        approx_dA = (diff / num_nodes) * A_val * 0.5
        new_A_target = A_val + approx_dA
        
        st.caption(f"👉 Try setting Stiffness **A** to **{new_A_target:.3f}** to hit the target.")

    # --- 8. ЛАНДШАФТ СТАБИЛЬНОСТИ ---
    st.write("---")
    st.write("⛰️ **Stability Landscape (Neighborhood)**")
    
    range_width = 15
    start_x = max(1, num_nodes - range_width)
    end_x = num_nodes + range_width
    
    x_vals = list(range(start_x, end_x + 1))
    y_vals = []
    
    for x in x_vals:
        if x == num_nodes:
            val = 50 # Текущая позиция
        elif is_prime_manual(x):
            val = 100 # Пик (Prime)
        else:
            d = len(get_divisors_manual(x))
            val = max(5, 85 - d*8) # Яма
        y_vals.append(val)

    chart_data = pd.DataFrame({"Nodes": x_vals, "Stability Index": y_vals})
    st.bar_chart(chart_data.set_index("Nodes"))
    st.caption("Высокие столбцы = Простые Числа. Низкие = Составные. Ваша цель — высокий столбец.")

else:
    st.warning("⚠️ База данных пуста или не загружена. Проверьте файл scyrmions_db.csv")
