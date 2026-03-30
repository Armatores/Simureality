import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V10.1 STRICT GEOMETRIC ROUTER
# Deterministic Beta-Decay I/O without Empirical Fitting
# =====================================================================

# --- FUNDAMENTAL HARDWARE CONSTANTS ---
ALPHA_INV = 137.036      # Импеданс Решетки
GAMMA_SYS = 1.0418       # Системный Налог
MAX_KE = 0.782           # Максимальная кинетическая энергия (MeV)

# 12 Аппаратных портов ввода-вывода ГЦК-решетки (FCC Vectors)
FCC_PORTS = np.array([
    [1, 1, 0], [1, -1, 0], [-1, 1, 0], [-1, -1, 0],
    [1, 0, 1], [1, 0, -1], [-1, 0, 1], [-1, 0, -1],
    [0, 1, 1], [0, 1, -1], [0, -1, 1], [0, -1, -1]
])

def calculate_strict_routing(spin_vector, blocked_ports_indices, neutron_pos):
    results = []
    
    # Нормализация векторов
    S = np.array(spin_vector)
    S = S / np.linalg.norm(S)
    
    # Динамический кулоновский градиент (зависит от позиции нейтрона в ядре)
    pos = np.array(neutron_pos)
    grad_V = pos / np.linalg.norm(pos) if np.linalg.norm(pos) > 0 else np.array([0, 0, 1])
    
    for i, port in enumerate(FCC_PORTS):
        P = port / np.linalg.norm(port) 
        
        # 1. Collision Avoidance (Булева блокировка)
        B = 1 if i in blocked_ports_indices else 0
        
        # 2. Строгий Топологический Импеданс (Экспоненциальное затухание)
        # Оптимальный вылет - строго против спина (-S)
        cos_theta_spin = np.dot(P, -S) 
        parity_factor = np.exp(cos_theta_spin * GAMMA_SYS)
        
        # 3. Строгий Кулоновский Импеданс
        cos_theta_coulomb = np.dot(P, grad_V)
        coulomb_factor = np.exp(cos_theta_coulomb)
        
        # Итоговый приоритет порта
        W = (1 - B) * parity_factor * coulomb_factor
        
        # 4. Геометрическая потеря энергии (Routing Lag)
        # Энергия сжигается пропорционально углу изгиба маршрута (1 - cos_theta)
        # Если вылет по идеальному анти-спину (cos_theta = 1), лаг = 0.
        routing_lag_penalty = MAX_KE * (1 - cos_theta_spin) * (GAMMA_SYS - 1)
        kinetic_energy = MAX_KE - routing_lag_penalty if B == 0 else 0
        
        results.append({
            "Port_ID": f"P{i}",
            "Vector": f"({port[0]}, {port[1]}, {port[2]})",
            "Blocked": "YES" if B == 1 else "NO",
            "Angle_to_AntiSpin": round(np.arccos(cos_theta_spin) * (180/np.pi), 1),
            "Routing_Weight (W)": round(W, 4),
            "Electron_KE (MeV)": round(max(0, kinetic_energy), 3)
        })
        
    df = pd.DataFrame(results)
    return df.sort_values(by="Routing_Weight (W)", ascending=False)

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="V10.1 Strict Geometric Beta-Decay", layout="wide")
st.title("🔫 V10.1: Pure FCC Geometric Router (Zero Fitting)")

st.sidebar.header("Параметры Макро-Ядра")
spin_z = st.sidebar.slider("Ось Спина Z", -1.0, 1.0, 1.0)
pos_z = st.sidebar.slider("Позиция нейтрона (Ось Z)", -1.0, 1.0, 1.0)
blocked_str = st.sidebar.text_input("Заблокированные порты (0-11)", "8, 9, 10")

try:
    blocked_idx = [int(x.strip()) for x in blocked_str.split(",") if x.strip()]
except:
    blocked_idx = []

df = calculate_strict_routing([0, 0, spin_z], blocked_idx, [0, 0, pos_z])

fig2 = go.Figure()
df_active = df[df["Blocked"] == "NO"]
fig2.add_trace(go.Scatter(x=df_active["Port_ID"], y=df_active["Electron_KE (MeV)"], mode='lines+markers', line=dict(color='#00E676', width=3), marker=dict(size=12)))
fig2.add_hline(y=MAX_KE, line_dash="dot", annotation_text="Max Energy (Ideal Path)")
fig2.update_layout(title="Дискретный Бета-Спектр (Геометрическая потеря энергии)", yaxis_title="Kinetic Energy (MeV)", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(df.style.background_gradient(subset=["Routing_Weight (W)"], cmap="Blues"), use_container_width=True)
