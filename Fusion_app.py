import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: STELLAR FORGE (SPACE & TIME UNIFIED ENGINE)
# =====================================================================

def generate_fcc_magic():
    base_shells = [int((n+1)*(n+2)*(n+3)/3) for n in range(6)] 
    twist_shifts = [28, 50, 82, 126] 
    return sorted(list(set(base_shells + twist_shifts)))

MAGIC_NODES = generate_fcc_magic()
E_ALPHA = 28.320       
E_MACRO = 2.425        
E_LINK = 2.360 
E_PAIR = 1.180      
J_TAX = 0.0131         

# --- ОСЬ ПРОСТРАНСТВА (НАША ТОПОЛОГИЯ) ---
def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    base_ports = 10.0 * ((Z + N)**(2/3))
    return (base_ports + (15.0 * ((dist_Z + dist_N)**1.6))) * J_TAX

def get_dangling_port_tax(Z, N):
    return (E_LINK / 2.0) * ((Z % 2) + (N % 2))

def calculate_topological_profit(Z, N):
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_NODES]) + min([abs(N - m) for m in MAGIC_NODES])) * 0.4
    
    BE = (N_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO)
    
    halo_n = N - Z
    if halo_n > 0: 
        max_strong_links = int(Z * 0.4) 
        strong_halo = min(halo_n, max_strong_links)
        weak_halo = halo_n - strong_halo
        BE += strong_halo * E_LINK
        BE += weak_halo * (E_PAIR / 2.0)
    
    BE -= get_jitter_tax(Z, N)
    BE -= get_dangling_port_tax(Z, N)
    return BE

def get_discrete_graph_diameter(A):
    if A <= 0: return 1
    diameter = 1
    for magic_size in MAGIC_NODES:
        if A > magic_size: diameter += 1
        else: break
    current_layer_base = MAGIC_NODES[diameter - 2] if diameter > 1 else 0
    next_layer_base = MAGIC_NODES[diameter - 1] if diameter <= len(MAGIC_NODES) else A
    layer_progress = (A - current_layer_base) / max(1, (next_layer_base - current_layer_base))
    return diameter + layer_progress

def get_total_matrix_energy(Z, N):
    """Полная энергия кристалла с учетом динамического Кулоновского налога"""
    if Z <= 0 or N <= 0: return 0
    base_profit = calculate_topological_profit(Z, N)
    A = Z + N
    C_TAX = E_LINK * np.sqrt(2) 
    coulomb_penalty = C_TAX * ((Z * (Z - 1)) / 2.0) / get_discrete_graph_diameter(A)
    return base_profit - coulomb_penalty

def get_fusion_profit(Z1, N1, Z2, N2, confinement_tax_mev=0.0):
    """
    Вычисляет профит слияния. 
    confinement_tax_mev - это Налог на Коллизию (Давление).
    Когда блоки разделены, но сдавлены гравитацией, они несут убыток маршрутизации.
    Слияние устраняет этот убыток.
    """
    E_parent = get_total_matrix_energy(Z1 + Z2, N1 + N2)
    E_frag1 = get_total_matrix_energy(Z1, N1)
    E_frag2 = get_total_matrix_energy(Z2, N2)
    
    # Энергия разделенного состояния: базовые энергии МИНУС налог на тесноту
    Initial_State = E_frag1 + E_frag2 - confinement_tax_mev
    Final_State = E_parent
    
    return Final_State - Initial_State

# --- ОСЬ ВРЕМЕНИ (ТАКТОВАЯ ЧАСТОТА ОТ "УМНИЦЫ") ---
def simulate_gamow_peak(lattice_impedance, max_latch_speed):
    energies = np.linspace(1, 200, 400) 
    p_penetration = np.exp(-lattice_impedance / np.sqrt(energies))
    p_latch = np.exp(-energies / max_latch_speed)
    cross_section = (1.0 / energies) * p_penetration * p_latch
    if np.max(cross_section) > 0:
        cross_section = (cross_section / np.max(cross_section)) * 100 
    
    df = pd.DataFrame({
        "Kinetic Energy (keV)": energies,
        "Grid Yielding Prob (Penetration)": p_penetration * 100,
        "Matrix Latch Prob (Commit Success)": p_latch * 100,
        "Fusion Cross-Section": cross_section
    })
    return df

# --- STREAMLIT UI ---
st.set_page_config(page_title="Stellar Forge: Unified Grid Engine", layout="wide")
st.title("🌟 Stellar Forge: Space-Time Fusion Engine")
st.markdown("Объединенный движок: Эмерджентная геометрия ГЦК-матрицы (Ось Пространства) + Декомпиляция тактовой частоты (Ось Времени).")

tab1, tab2, tab3 = st.tabs(["🪜 Alpha Ladder (Emergent Iron Wall)", "⚙️ Tokamak (Confinement Pressure)", "⏱️ Gamow Peak (Time Latch)"])

with tab1:
    st.subheader("Симуляция звездного нуклеосинтеза (Alpha-процесс)")
    st.markdown("Алгоритм холодного синтеза. Железная стена возникает эмерджентно: Кулоновский налог на диагонали превышает профит от сборки новых тетраэдров.")
    
    if st.button("Запустить цепочку альфа-захвата", type="primary", key="btn_ladder"):
        ladder_results = []
        current_Z, current_N = 2, 2 
        elements = ["He", "Be", "C", "O", "Ne", "Mg", "Si", "S", "Ar", "Ca", "Ti", "Cr", "Fe", "Ni", "Zn", "Ge", "Se", "Kr"]
        
        for idx in range(1, 15):
            target_Z, target_N = current_Z + 2, current_N + 2
            elem_name = elements[idx] if idx < len(elements) else f"Z={target_Z}"
            step_profit = get_fusion_profit(current_Z, current_N, 2, 2)
            
            ladder_results.append({
                "Reaction": f"Z={current_Z} + He-4 ➔ {elem_name}-{target_Z+target_N}",
                "Product Z": target_Z,
                "Fusion Profit (MeV)": step_profit,
                "Verdict": "✅ Одобрено (Star Burns)" if step_profit > 0 else "🚨 Заблокировано (Endothermic)"
            })
            current_Z, current_N = target_Z, target_N
            
        df_ladder = pd.DataFrame(ladder_results)
        
        fig1 = px.bar(df_ladder, x="Product Z", y="Fusion Profit (MeV)", 
                     color="Verdict", text_auto='.2f',
                     color_discrete_map={"✅ Одобрено (Star Burns)": "#00FF7F", "🚨 Заблокировано (Endothermic)": "#FF4500"})
        fig1.update_layout(xaxis_title="Protons (Z) of Product", yaxis_title="Marginal Fusion Profit (MeV)", template="plotly_dark")
        fig1.add_hline(y=0, line_width=2, line_color="white")
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(df_ladder, use_container_width=True)

with tab2:
    st.subheader("Влияние Гравитации: Налог на пространственную коллизию")
    st.markdown("В вакууме симметричные блоки Углерода/Кислорода не сливаются (убыток). Но если гравитация сжимает их, порты начинают конфликтовать. Матрица одобряет синтез, чтобы сбросить налог на коллизию кэша.")
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        z1 = st.number_input("Fragment 1 (Z)", min_value=1, value=6, step=1)
        n1 = st.number_input("Fragment 1 (N)", min_value=0, value=6, step=1)
        z2 = st.number_input("Fragment 2 (Z)", min_value=1, value=6, step=1)
        n2 = st.number_input("Fragment 2 (N)", min_value=0, value=6, step=1)
        
    with col_c2:
        pressure = st.slider("Гравитационное Давление (Collision Tax, MeV)", min_value=0.0, max_value=25.0, value=0.0, step=0.5, help="Штраф Матрицы за то, что два независимых блока удерживаются в одной ячейке.")
        
        profit = get_fusion_profit(z1, n1, z2, n2, confinement_tax_mev=pressure)
        
        st.divider()
        if profit > 0:
            st.success(f"🔥 УСПЕХ: Термоядерное Зажигание! Матрица спаяла блоки. Выход энергии: +{profit:.2f} МэВ")
        else:
            st.error(f"❄️ ОТКАЗ: Давления недостаточно. Слияние заблокировано: {profit:.2f} МэВ")
            
        st.info(f"Собранный макро-кристалл: Z={z1+z2}, N={n1+n2} (Масса {z1+z2+n1+n2})")

with tab3:
    st.subheader("Декомпиляция Пика Гамова (Аппаратный Latch Timeout)")
    st.markdown("Температура — это Jitter-частота. Если ядро летит слишком быстро, Диспетчер Матрицы не успевает записать транзакцию (Пропуск Кадра / Latch Timeout).")
    
    col1, col2 = st.columns(2)
    imp = col1.slider("Lattice Impedance (Сопротивление Сетки Кулоном)", 10.0, 150.0, 80.0, 10.0)
    latch = col2.slider("Matrix Latch Timeout Speed (Тактовая частота)", 50.0, 300.0, 120.0, 10.0, help="Энергия, при которой скорость пролета превышает скорость коммита Матрицы.")
    
    df_gamow = simulate_gamow_peak(lattice_impedance=imp, max_latch_speed=latch)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Grid Yielding Prob (Penetration)"], name="Успех Прогиба Сетки", line=dict(dash='dash', color='#00BFFF')))
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Matrix Latch Prob (Commit Success)"], name="Успех Коммита (До тайм-аута)", line=dict(dash='dash', color='#FF4500')))
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Fusion Cross-Section"], name="Итоговое Сечение (Пик Гамова)", line=dict(color='#32CD32', width=4), fill='tozeroy'))
    
    fig2.update_layout(title="Hardware Simulation of Thermonuclear Fusion Rates", xaxis_title="Kinetic Energy / Temperature (keV)", yaxis_title="Probability (Normalized)", template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)
