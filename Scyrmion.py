import streamlit as st
import numpy as np
import math

# --- ВСТРОЕННАЯ МАТЕМАТИКА (NO SYMPY DEPENDENCY) ---
# Чтобы работало везде без настройки серверов
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

# --- БАЗА ДАННЫХ МАТЕРИАЛОВ ---
MATERIALS = {
    "FeGe (Helimagnet)":     {"A": 8.78, "D": 1.58, "a": 0.470, "desc": "Classic, Low Temp"},
    "MnSi (Classic Cryo)":   {"A": 4.40, "D": 0.72, "a": 0.456, "desc": "Unstable, Deep Freeze"},
    "Co8-Zn8-Mn4 (Room T)":  {"A": 6.20, "D": 2.10, "a": 0.640, "desc": "🔥 ROOM TEMP HERO"},
    "Cu2OSeO3 (Insulator)":  {"A": 5.00, "D": 1.00, "a": 0.890, "desc": "Fragile Insulator"},
    "Custom":                {"A": 10.0, "D": 1.5,  "a": 0.5,   "desc": "User Defined"}
}

st.set_page_config(page_title="Skyrmion Prime Scanner", layout="centered")

st.title("🌪️ Skyrmion Prime Scanner")
st.caption("Simureality Circuit 2: Topological Stability Analysis")

# --- ВВОД ДАННЫХ ---
selected_mat = st.selectbox("Выберите материал:", list(MATERIALS.keys()))

if selected_mat == "Custom":
    col1, col2, col3 = st.columns(3)
    A = col1.number_input("Stiffness A (pJ/m)", 0.1, 50.0, 10.0)
    D = col2.number_input("DMI D (mJ/m²)", 0.01, 10.0, 1.5)
    a = col3.number_input("Lattice a (nm)", 0.1, 2.0, 0.5)
    desc = "Custom"
else:
    params = MATERIALS[selected_mat]
    A = params["A"]
    D = params["D"]
    a = params["a"]
    desc = params["desc"]

st.info(f"**Параметры:** A={A}, D={D}, a={a} | **Тип:** {desc}")

# --- РАСЧЕТНАЯ ЧАСТЬ ---
# 1. Физика
pitch_nm = (4 * np.pi * A) / D
radius_nm = pitch_nm / 2

# 2. Геометрия
area_skyrmion = np.pi * (radius_nm ** 2)
area_node = a ** 2
num_nodes_raw = area_skyrmion / area_node
num_nodes = int(round(num_nodes_raw))

# 3. Анализ Чисел (Simureality)
is_prime = is_prime_manual(num_nodes)
divisors = get_divisors_manual(num_nodes)
num_divs = len(divisors)

# --- ВЫВОД РЕЗУЛЬТАТОВ ---
st.divider()
c1, c2 = st.columns(2)
c1.metric("Vortex Radius", f"{radius_nm:.2f} nm")
c2.metric("Grid Nodes (N)", f"{num_nodes}")

st.subheader("Simureality Verdict:")

if is_prime:
    st.success(f"💎 PRIME TOPOLOGY detected!")
    st.markdown(f"### {num_nodes} is a Prime Number.")
    st.write("Статус: **ABSOLUTE STABILITY**.")
    st.write("Геометрия неразрушима стандартными методами. Идеально для 'вечной' памяти.")
else:
    # Анализ делителей
    if num_divs <= 4:
        if num_nodes % 2 == 0:
            st.warning(f"💾 SEMI-PRIME (Hard Memory)")
            st.markdown(f"### {num_nodes} = 2 × {num_nodes//2}")
            st.write("Статус: **ROBUST / REWRITABLE**.")
            st.write("Идеальный баланс. Держит структуру, но поддается магнитной перезаписи (через шов '2').")
            if selected_mat.startswith("FeGe"):
                st.write("✅ Это объясняет успех FeGe!")
        else:
            st.warning(f"🔸 ALMOST PRIME ({num_divs} divisors)")
            st.write("Высокая стабильность.")
    else:
        st.error(f"⚠️ UNSTABLE / NOISY")
        st.markdown(f"### {num_nodes} is Composite ({num_divs} divisors)")
        st.write(f"Делители: {divisors[:10]}...")
        st.write("Статус: **DECAY**. Вихрь слишком 'рыхлый', решетка его порвет.")

st.divider()

# --- ВИЗУАЛИЗАЦИЯ (ЛАНДШАФТ) ---
st.write("⛰️ **Ландшафт Стабильности (Соседи)**")
range_vals = range(num_nodes - 10, num_nodes + 11)
stability = []
for x in range_vals:
    if is_prime_manual(x):
        stability.append(100) # Пик
    else:
        d = len(get_divisors_manual(x))
        stability.append(max(10, 80 - d*10)) # Яма

chart_data = {"Nodes": list(range_vals), "Stability": stability}
st.bar_chart(chart_data, x="Nodes", y="Stability")
