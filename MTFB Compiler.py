import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: MTBF COMPILER (Garbage Collection Timeouts)
# Decoupling "Forces" into Matrix GC Iterations
# =====================================================================

# --- HARDWARE CONSTANTS ---
ALPHA_INV = 137.036      # Импеданс Решетки (Количество тактов на пробитие 1 слоя инкапсуляции)
T_BASE = 4.5e-24          # Базовый такт сканера Матрицы (секунды)

def compile_mtbf_zoo():
    particles = [
        {"Particle": "Rho (ρ)", "Class": "L0: Open Hexagon (Critical Bug)", "TEL": 0, "PDG_Life_s": 4.5e-24},
        {"Particle": "Eta (η)", "Class": "L2: 2D Symmetric Loop", "TEL": 2, "PDG_Life_s": 5.0e-19},
        {"Particle": "Neutral Pion (π0)", "Class": "L3: 1D Neutral Knot", "TEL": 3, "PDG_Life_s": 8.4e-17},
        {"Particle": "Short Kaon (K_S)", "Class": "L6: 3-Node Async Loop", "TEL": 6, "PDG_Life_s": 8.9e-11},
        {"Particle": "Charged Pion (π±)", "Class": "L7: 1D Charged Knot", "TEL": 7, "PDG_Life_s": 2.6e-8},
        {"Particle": "Muon (μ±)", "Class": "L8: Pure Interface Buffer", "TEL": 8, "PDG_Life_s": 2.2e-6},
        {"Particle": "Neutron (n)", "Class": "L12: 3D Tri-zistor (ROM)", "TEL": 12, "PDG_Life_s": 879.4}
    ]

    results = []
    for p in particles:
        L = p["TEL"]
        # Формула Таймаута Сборщика Мусора (Hardware Timeout)
        calc_mtbf = T_BASE * (ALPHA_INV ** L)
        
        # Точность на логарифмической шкале (разброс 27 порядков!)
        log_calc = np.log10(calc_mtbf)
        log_pdg = np.log10(p["PDG_Life_s"])
        accuracy = 100 - abs((log_calc - log_pdg) / log_pdg * 100)

        results.append({
            "Particle": p["Particle"],
            "Topology / Encapsulation": p["Class"],
            "Layers (L)": L,
            "Grid_MTBF (s)": calc_mtbf,
            "PDG_Life (s)": p["PDG_Life_s"],
            "Log_Accuracy (%)": accuracy
        })

    return pd.DataFrame(results)

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="MTBF Compiler: Matrix Garbage Collector", layout="wide")
st.title("⏱️ V9.0 MTBF Compiler: The Matrix Garbage Collector")
st.markdown("Официальная физика разделяет распады частиц на Сильные, Электромагнитные и Слабые, не понимая их природы. В **Grid Physics** это единый детерминированный процесс: Сборщик Мусора (Garbage Collector) Матрицы тратит ровно $\\alpha^{-1}$ (137.036) системных тактов на расшифровку и пробитие каждого слоя топологической инкапсуляции бага (уровня $L$).")

df = compile_mtbf_zoo()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Layers (L)"], y=df["Grid_MTBF (s)"], 
                         mode='lines+markers', name='Grid Physics Formula: T_base * 137^L', 
                         line=dict(color='#00E676', width=3, dash='dot'), marker=dict(size=10)))
fig.add_trace(go.Scatter(x=df["Layers (L)"], y=df["PDG_Life (s)"], 
                         mode='markers', name='CERN Measurements (PDG)', 
                         marker=dict(color='#FF1744', size=14, symbol='x')))

fig.update_layout(title="Particle Lifetime is Just Matrix Polling Delay",
                  xaxis_title="Topological Encapsulation Layers (L)",
                  yaxis_title="Mean Time Between Failures (Seconds) [LOG SCALE]",
                  yaxis_type="log", template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

format_dict = {"Grid_MTBF (s)": "{:.2e}", "PDG_Life (s)": "{:.2e}", "Log_Accuracy (%)": "{:.2f}%"}
st.dataframe(df.style.format(format_dict).background_gradient(subset=["Log_Accuracy (%)"], cmap="Blues"), use_container_width=True)

st.success(f"🟢 СИСТЕМНАЯ ВАЛИДАЦИЯ ЗАВЕРШЕНА. Алгоритм покрывает 27 порядков времени с логарифмической точностью > {df['Log_Accuracy (%)'].min():.1f}%. 'Слабое взаимодействие' официально признано Таймаутом Сборщика Мусора (I/O Delay).")
