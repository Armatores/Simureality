import streamlit as st
import numpy as np
import pandas as pd
import math

# --- 1. МАТЕМАТИЧЕСКОЕ ЯДРО ---
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
        df = pd.read_csv("scyrmions_db.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ Файл scyrmions_db.csv не найден!")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. БОКОВАЯ ПАНЕЛЬ ---
    st.sidebar.header("🎛️ Control Panel")
    
    material_names = df["Material"].tolist()
    selected_name = st.sidebar.selectbox("Load Preset", material_names, key="material_selector")
    
    row = df[df["Material"] == selected_name].iloc[0]
    
    # ЛОГИКА ОБНОВЛЕНИЯ (SESSION STATE)
    if "last_selected_mat" not in st.session_state:
        st.session_state.last_selected_mat = None

    if st.session_state.last_selected_mat != selected_name:
        st.session_state.last_selected_mat = selected_name
        st.session_state.A_input = float(row["A_stiffness"])
        st.session_state.D_input = float(row["D_dmi"])
        st.session_state.a_input = float(row["a_lattice"])
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write("⚙️ **Fine-Tuning (High Precision)**")
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ: format="%.4f" и step=0.001 ---
    # Теперь он показывает 4 знака и позволяет менять тысячные доли
    A_val = st.sidebar.number_input("Stiffness A (pJ/m)", step=0.001, format="%.4f", key="A_input")
    D_val = st.sidebar.number_input("DMI D (mJ/m²)", step=0.001, format="%.4f", key="D_input")
    a_val = st.sidebar.number_input("Lattice a (nm)", step=0.0001, format="%.4f", key="a_input")
    # -----------------------------------------------------

    mat_type = str(row['Type'])
    mat_desc = str(row['Description'])
    st.sidebar.info(f"**Type:** {mat_type}\n\n{mat_desc}")

    # --- 5. РАСЧЕТ ---
    if D_val == 0: D_val = 0.0001
    pitch_nm = (4 * np.pi * A_val) / D_val
    radius_nm = pitch_nm / 2

    area_skyrmion = np.pi * (radius_nm ** 2)
    area_node = a_val ** 2
    num_nodes_raw = area_skyrmion / area_node
    num_nodes = int(round(num_nodes_raw))

    is_prime = is_prime_manual(num_nodes)
    divisors = get_divisors_manual(num_nodes)
    num_divs = len(divisors)

    # --- 6. ВЫВОД ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vortex Radius (R)", f"{radius_nm:.2f} nm")
    with col2:
        preset_pitch = (4 * np.pi * row["A_stiffness"]) / row["D_dmi"]
        preset_nodes = int(round((np.pi * (preset_pitch/2)**2) / row["a_lattice"]**2))
        diff_nodes = num_nodes - preset_nodes
        
        # Красивый вывод дельты
        if diff_nodes > 0:
            delta_str = f"+{diff_nodes} vs Preset"
            delta_color = "normal" # Зеленый (обычно)
        elif diff_nodes < 0:
            delta_str = f"{diff_nodes} vs Preset"
            delta_color = "off" # Красный/Серый
        else:
            delta_str = "Exact Preset"
            delta_color = "off"
        
        st.metric("Grid Nodes (N)", f"{num_nodes}", delta=delta_str, delta_color=delta_color)
        
    with col3:
        if is_prime:
            st.success("💎 PRIME FOUND")
        elif num_divs <= 4:
            st.warning("💾 ROBUST")
        else:
            st.error("⚠️ UNSTABLE")

    st.divider()

    st.subheader("Simureality Verdict")
    
    if is_prime:
        st.success(f"### 💎 PRIME TOPOLOGY DETECTED: {num_nodes}")
        st.markdown(f"**Status: ABSOLUTE STABILITY.**\n\nГеометрия {selected_name} (с текущими настройками) образует неразрушимый узел.")
    else:
        lower_prime = num_nodes - 1
        while not is_prime_manual(lower_prime): lower_prime -= 1
        upper_prime = num_nodes + 1
        while not is_prime_manual(upper_prime): upper_prime += 1
        
        dist_down = num_nodes - lower_prime
        dist_up = upper_prime - num_nodes
        target = lower_prime if dist_down < dist_up else upper_prime
        diff = target - num_nodes
        
        if num_divs <= 4 and num_nodes % 2 == 0:
             st.info(f"### 💾 SEMI-PRIME: {num_nodes} = 2 × {num_nodes//2}")
             st.write("Статус: **Rewritable Memory**.")
        else:
             st.error(f"### ⚠️ COMPOSITE: {num_nodes} ({num_divs} divisors)")
             st.write("Статус: **Instability / Decay**.")

        # Подсказка
        approx_dA = (diff / num_nodes) * A_val * 0.5
        new_A_target = A_val + approx_dA
        st.caption(f"👉 Target Prime: **{target}**. Try setting Stiffness A ≈ **{new_A_target:.4f}**")

    # --- 7. ЛАНДШАФТ ---
    st.write("---")
    st.write("⛰️ **Stability Landscape**")
    
    range_width = 15
    start_x = max(1, num_nodes - range_width)
    end_x = num_nodes + range_width
    
    x_vals = list(range(start_x, end_x + 1))
    y_vals = []
    
    for x in x_vals:
        if x == num_nodes:
            val = 50 
        elif is_prime_manual(x):
            val = 100
        else:
            d = len(get_divisors_manual(x))
            val = max(5, 85 - d*8)
        y_vals.append(val)

    chart_data = pd.DataFrame({"Nodes": x_vals, "Stability Index": y_vals})
    st.bar_chart(chart_data.set_index("Nodes"))

else:
    st.warning("⚠️ База данных не загружена.")
