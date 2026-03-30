import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V10 FCC BETA-DECAY ROUTER 
# Deterministic I/O Port Selection & The Illusion of Neutrinos
# =====================================================================

# --- HARDWARE CONSTANTS ---
ALPHA_INV = 137.036      # Импеданс Решетки
MAX_KE = 0.782           # Максимальная энергия бета-распада нейтрона (MeV)

# 12 Аппаратных портов ввода-вывода ГЦК-решетки (FCC Vectors)
FCC_PORTS = np.array([
    [1, 1, 0], [1, -1, 0], [-1, 1, 0], [-1, -1, 0],
    [1, 0, 1], [1, 0, -1], [-1, 0, 1], [-1, 0, -1],
    [0, 1, 1], [0, 1, -1], [0, -1, 1], [0, -1, -1]
])

def calculate_beta_routing(spin_vector, blocked_ports_indices):
    results = []
    
    # Нормализация вектора спина ядра (ось опроса Матрицы)
    S = np.array(spin_vector)
    S = S / np.linalg.norm(S)
    
    # Имитация Кулоновского градиента (выход из ядра направлен, например, по оси Z)
    grad_V = np.array([0, 0, 1]) 
    
    for i, port in enumerate(FCC_PORTS):
        # Вектор конкретного порта
        P = port / np.linalg.norm(port) 
        
        # 1. Collision Avoidance (Блокировка занятых портов макро-линками)
        B = 1 if i in blocked_ports_indices else 0
        
        # 2. Нарушение четности (Топологическое давление спина)
        # P dot S: отрицательное значение означает вылет против спина (разрежение)
        spin_alignment = np.dot(P, S)
        parity_factor = np.exp(-spin_alignment / (ALPHA_INV / 100)) # Нормировка для наглядности
        
        # 3. Кулоновский градиент
        coulomb_factor = max(0.1, np.dot(P, grad_V)) # Только порты, смотрящие наружу
        
        # Итоговый вес маршрута (Вероятность выстрела)
        W = (1 - B) * parity_factor * coulomb_factor
        
        # Расчет кинетической энергии электрона (Закон сжигания энергии на маршрутизацию)
        # Если порт оптимален (W максимально) -> KE стремится к MAX_KE
        # Если выстрел "за угол" -> Routing Lag съедает энергию (имитация нейтрино)
        routing_lag_penalty = (1 - np.dot(P, -S)) * 0.3 # Штраф за отклонение от идеального анти-спина
        kinetic_energy = MAX_KE - routing_lag_penalty if B == 0 else 0
        
        results.append({
            "Port_ID": f"P{i+1}",
            "Vector": f"({port[0]}, {port[1]}, {port[2]})",
            "Blocked": "YES" if B == 1 else "NO",
            "Spin_Dot": round(spin_alignment, 3),
            "Routing_Weight (W)": round(W, 4),
            "Electron_KE (MeV)": round(max(0, kinetic_energy), 3)
        })
        
    df = pd.DataFrame(results)
    # Сортировка по приоритету выстрела
    return df.sort_values(by="Routing_Weight (W)", ascending=False)

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="V10 Beta-Decay Router", layout="wide")
st.title("🔫 V10 I/O Router: The Geometric Origin of Beta Decay")
st.markdown("Этот алгоритм декомпилирует опыт Ву и доказывает **отсутствие нейтрино**. Электрон вылетает строго по одному из 12 ГЦК-портов. Диспетчер выбирает вектор наименьшего топологического сопротивления (против спина). Сплошной бета-спектр — это потеря энергии электрона на преодоление системного лага (Routing Lag) при стрельбе по неоптимальным портам.")

# Вводные данные от пользователя (моделируем состояние ядра)
st.sidebar.header("Параметры Макро-Ядра")
spin_z = st.sidebar.slider("Вектор Спина (Ось Z)", -1.0, 1.0, 1.0)
st.sidebar.markdown("Заблокированные порты (Имитация соседних нуклонов):")
blocked_str = st.sidebar.text_input("ID портов (через запятую, от 0 до 11)", "8, 9, 10")

try:
    blocked_idx = [int(x.strip()) for x in blocked_str.split(",") if x.strip()]
except:
    blocked_idx = []

df = calculate_beta_routing([0, 0, spin_z], blocked_idx)

# Визуализация приоритетов портов
fig1 = go.Figure()
fig1.add_trace(go.Bar(x=df["Port_ID"], y=df["Routing_Weight (W)"], marker_color='#00E676', name="Приоритет (W)"))
fig1.update_layout(title="Алгоритм Pathfinding: Выбор порта выстрела", yaxis_title="Routing Weight (Priority)", template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

# Визуализация "Иллюзии Нейтрино" (Бета-спектр)
fig2 = go.Figure()
df_active = df[df["Blocked"] == "NO"]
fig2.add_trace(go.Scatter(x=df_active["Port_ID"], y=df_active["Electron_KE (MeV)"], mode='lines+markers', line=dict(color='#FF1744', width=3), marker=dict(size=12)))
fig2.add_hline(y=MAX_KE, line_dash="dot", annotation_text="Max Energy (No Routing Lag)", annotation_position="bottom right")
fig2.update_layout(title="Сплошной Бета-Спектр (Кинетическая энергия зависит от выбранного порта)", yaxis_title="Kinetic Energy (MeV)", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# Таблица данных
st.subheader("Системный Журнал Ввода-Вывода (I/O Log)")
st.dataframe(df.style.background_gradient(subset=["Routing_Weight (W)"], cmap="Blues"), use_container_width=True)

st.success("🟢 ОПЕРАЦИЯ DROP() РАССЧИТАНА. Нейтрино официально переведено в статус Legacy Code. Энергия расходуется на системную маршрутизацию.")
