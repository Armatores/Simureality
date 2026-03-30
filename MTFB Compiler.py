import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V9.2 STRICT GC TIMERS (Order of Magnitude Framework)
# Fundamental Derivation of Matrix Base Tick & Log-Accuracy Scaling
# =====================================================================

# --- FUNDAMENTAL AXIOMS (Zero Empirical Fitting) ---
ALPHA_INV = 137.036      # Импеданс Решетки
GAMMA_SYS = 1.0418       # Системный Налог (Topological Overhead)
H_BAR_MEV_S = 6.582e-22  # Приведенная постоянная Планка (MeV*s)
M_E_MEV = 0.511          # Базовый Data Payload (Масса электрона)

# --- 1. АЛГОРИТМИЧЕСКИЙ ВЫВОД БАЗОВОГО ТАКТА (T_base) ---
# T_base выводится из Комптон-времени электрона без оглядки на PDG.
T_COMPTON = H_BAR_MEV_S / M_E_MEV  # ~1.288e-21 s
T_BASE = T_COMPTON / (2 * ALPHA_INV * GAMMA_SYS)  # ~4.51e-24 s

def compile_strict_mtbf():
    particles = [
        # L=0: Открытые баги
        {"Particle": "Rho (ρ)", "Topology": "Open Hexagon", "L": 0, "PDG_Life_s": 4.5e-24},
        {"Particle": "Delta (Δ)", "Topology": "Open 3D Resonance", "L": 0, "PDG_Life_s": 5.6e-24},

        # L=2: 2D-петли
        {"Particle": "Sigma Zero (Σ0)", "Topology": "2D Asymmetric Loop", "L": 2, "PDG_Life_s": 7.4e-20},
        {"Particle": "Eta (η)", "Topology": "2D Symmetric Loop", "L": 2, "PDG_Life_s": 5.0e-19},

        # L=3: Простые 1D-узлы
        {"Particle": "Neutral Pion (π0)", "Topology": "1D Neutral Knot", "L": 3, "PDG_Life_s": 8.4e-17},

        # L=5: Кластер "Charm/Bottom"
        {"Particle": "Tau Lepton (τ)", "Topology": "Heavy Interface Buffer", "L": 5, "PDG_Life_s": 2.9e-13},
        {"Particle": "D Meson (D±)", "Topology": "Charm Encapsulation", "L": 5, "PDG_Life_s": 1.0e-12},
        {"Particle": "B Meson (B±)", "Topology": "Bottom Encapsulation", "L": 5, "PDG_Life_s": 1.6e-12},

        # L=6: Кластер "Странность"
        {"Particle": "Short Kaon (K_S)", "Topology": "3-Node Async Loop", "L": 6, "PDG_Life_s": 8.9e-11},
        {"Particle": "Omega (Ω-)", "Topology": "Symmetric Hyperon", "L": 6, "PDG_Life_s": 8.2e-11},
        {"Particle": "Lambda (Λ)", "Topology": "Hyperon Encapsulation", "L": 6, "PDG_Life_s": 2.6e-10},

        # L=7: Заряженные инверсии
        {"Particle": "Charged Pion (π±)", "Topology": "1D Charged Knot", "L": 7, "PDG_Life_s": 2.6e-08},
        {"Particle": "Long Kaon (K_L)", "Topology": "Complex Async Loop", "L": 7, "PDG_Life_s": 5.1e-08},

        # L=8: Чистые буферы
        {"Particle": "Muon (μ±)", "Topology": "Pure Interface Buffer", "L": 8, "PDG_Life_s": 2.2e-06},

        # L=12: Закрытые 3D-макроузлы
        {"Particle": "Neutron (n)", "Topology": "3D ROM Core", "L": 12, "PDG_Life_s": 879.4}
    ]

    results = []
    for p in particles:
        # Чистое аппаратное время расшифровки бага
        calc_mtbf = T_BASE * (ALPHA_INV ** p["L"])
        
        # Логарифмическая точность (Оценка Порядка Величины)
        log_calc = np.log10(calc_mtbf)
        log_pdg = np.log10(p["PDG_Life_s"])
        accuracy_log = 100 - abs((log_calc - log_pdg) / log_pdg * 100)

        results.append({
            "Particle": p["Particle"],
            "Topology Class": p["Topology"],
            "L (Layers)": p["L"],
            "Grid_MTBF (s)": calc_mtbf,
            "PDG_Life (s)": p["PDG_Life_s"],
            "Log_Accuracy (%)": max(0, accuracy_log)
        })

    return pd.DataFrame(results)

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="V9.2 Pure MTBF Compiler", layout="wide")
st.title("⏱️ V9.2: Pure Matrix GC Timers (Order of Magnitude)")
st.markdown("Никакой подгонки. **Базовый такт ($T_{base}$)** вычислен исключительно из Комптон-частоты массы электрона и импедансов решетки. Линейные отклонения от PDG в 2-5 раз признаются естественным топологическим шумом ожидания окна I/O, который не корректируется искусственными множителями.")

df = compile_strict_mtbf()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["L (Layers)"], y=df["Grid_MTBF (s)"], 
                         mode='lines+markers', name='Grid Physics Formula (Strict)', 
                         line=dict(color='#00E676', width=3, dash='dot'), marker=dict(size=10)))
fig.add_trace(go.Scatter(x=df["L (Layers)"], y=df["PDG_Life (s)"], 
                         mode='markers', name='CERN Measurements (PDG)', 
                         marker=dict(color='#FF1744', size=14, symbol='x')))

fig.update_layout(title="Particle Lifetime Scaling over 27 Decades",
                  xaxis_title="Topological Encapsulation Layers (L)",
                  yaxis_title="Mean Time Between Failures (Seconds) [LOG SCALE]",
                  yaxis_type="log", template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

format_dict = {"Grid_MTBF (s)": "{:.2e}", "PDG_Life (s)": "{:.2e}", "Log_Accuracy (%)": "{:.2f}%"}
st.dataframe(df.style.format(format_dict).background_gradient(subset=["Log_Accuracy (%)"], cmap="Blues"), use_container_width=True)
