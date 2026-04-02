import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V26.0 UNIVERSAL FORGE (SPACE, TIME & MOLECULES)
# Unified Synthesis Engine: From Stellar Cores to Organic Polymers
# =====================================================================

st.set_page_config(page_title="Universal Forge V26", layout="wide", page_icon="🌌")

# --- 1. STELLAR FORGE (ЗВЕЗДНЫЕ АЛГОРИТМЫ АРХИТЕКТОРА) ---
def generate_fcc_magic():
    base_shells = [int((n+1)*(n+2)*(n+3)/3) for n in range(6)] 
    twist_shifts = [28, 50, 82, 126] 
    return sorted(list(set(base_shells + twist_shifts)))

MAGIC_NODES = generate_fcc_magic()
E_ALPHA, E_MACRO, E_LINK, E_PAIR, J_TAX = 28.320, 2.425, 2.360, 1.180, 0.0131         

def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    base_ports = 10.0 * ((Z + N)**(2/3))
    return (base_ports + (15.0 * ((dist_Z + dist_N)**1.6))) * J_TAX

def get_dangling_port_tax(Z, N): return (E_LINK / 2.0) * ((Z % 2) + (N % 2))

def calculate_topological_profit(Z, N):
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_NODES]) + min([abs(N - m) for m in MAGIC_NODES])) * 0.4
    BE = (N_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO)
    halo_n = N - Z
    if halo_n > 0: 
        max_strong_links = int(Z * 0.4) 
        BE += min(halo_n, max_strong_links) * E_LINK + (halo_n - min(halo_n, max_strong_links)) * (E_PAIR / 2.0)
    return BE - get_jitter_tax(Z, N) - get_dangling_port_tax(Z, N)

def get_discrete_graph_diameter(A):
    if A <= 0: return 1
    diameter = 1
    for m in MAGIC_NODES:
        if A > m: diameter += 1
        else: break
    cb = MAGIC_NODES[diameter - 2] if diameter > 1 else 0
    nb = MAGIC_NODES[diameter - 1] if diameter <= len(MAGIC_NODES) else A
    return diameter + (A - cb) / max(1, (nb - cb))

def get_total_matrix_energy(Z, N):
    if Z <= 0 or N <= 0: return 0
    return calculate_topological_profit(Z, N) - ((E_LINK * np.sqrt(2)) * ((Z * (Z - 1)) / 2.0) / get_discrete_graph_diameter(Z + N))

def get_fusion_profit(Z1, N1, Z2, N2, confinement_tax_mev=0.0):
    return get_total_matrix_energy(Z1 + Z2, N1 + N2) - (get_total_matrix_energy(Z1, N1) + get_total_matrix_energy(Z2, N2) - confinement_tax_mev)

def simulate_gamow_peak(lattice_impedance, max_latch_speed):
    energies = np.linspace(1, 200, 400) 
    p_pen, p_latch = np.exp(-lattice_impedance / np.sqrt(energies)), np.exp(-energies / max_latch_speed)
    cross_section = (1.0 / energies) * p_pen * p_latch
    if np.max(cross_section) > 0: cross_section = (cross_section / np.max(cross_section)) * 100 
    return pd.DataFrame({"Kinetic Energy (keV)": energies, "Grid Yielding Prob": p_pen * 100, "Matrix Latch Prob": p_latch * 100, "Fusion Cross-Section": cross_section})

# --- 2. MOLECULAR FORGE (ОСЬ ХИМИИ - СБОРКА ИЗ V25) ---
GAMMA_SYS = 1.0418
RAW_CC = 327.51
RAW_CH = 398.11
RAW_CO = 330.91

def get_chem_energy(bonds_cc=0, bonds_ch=0, bonds_co=0, sp=0, sp2=0, token_ring=False, hw_lock=False):
    """Вычисляет АБСОЛЮТНУЮ вычислительную стабильность молекулы на ГЦК-решетке"""
    # 1. Base Deduplication (Слияние ядер)
    base = (bonds_cc * RAW_CC + bonds_ch * RAW_CH + bonds_co * RAW_CO) * GAMMA_SYS
    
    # 2. Hardware Tension (Штрафы за кривую маршрутизацию)
    tension = (sp * 140.0) + (sp2 * 45.0)
    
    # 3. Dynamic Cashback / Relief (Аппаратные бонусы)
    cashback = 0.0
    if token_ring:
        cashback += 150.0  # Возврат налогов за 2D гексагон (Резонанс)
        tension = 0        # Token ring обнуляет статический лаг изломов!
    if hw_lock:
        cashback += 150.0  # Бонус за идеальную прямую ось O=C=O
        tension = 0        # Замок не гнется, лага нет.
        
    return base - tension + cashback

# Исходные мономеры
E_ETHYLENE = get_chem_energy(bonds_cc=2, bonds_ch=4, sp2=2)
E_ACETYLENE = get_chem_energy(bonds_cc=3, bonds_ch=2, sp=2)
E_O_ATOM = 0 # Baseline
E_C_ATOM = 0 # Baseline

# --- STREAMLIT UI ---
st.title("🌌 V26.0 Universal Forge: Forward Synthesis")
st.markdown("Мы больше не разрушаем системы. Мы рассчитываем **Маржинальный Вычислительный Профит Слияния** (MERGE Profit). Диспетчер Матрицы принимает решения одинаково: будь то слияние ядер в звезде или сборка органики.")

tab1, tab2, tab3 = st.tabs(["🧬 Химическая Сборка (Molecular Forge)", "🌟 Звездная Сборка (Alpha Ladder)", "⚙️ Давление и Время (Gravity & Gamow)"])

with tab1:
    st.subheader("Поэтапная молекулярная сборка (Алгоритм Созидания)")
    st.markdown("Смотрим, как система осознает выгоду *в процессе*. Полимеры собираются легко, Бензол — с сопротивлением (пока не сорвет Джекпот), а CO2 формирует железный замок.")
    
    pathways = {
        "1. Синтез Пластика (Полиэтилен) - Снятие Штрафа Маршрутизации": [
            {"step": "C2H4 + C2H4 ➔ 1-Butene", "val": get_chem_energy(bonds_cc=4, bonds_ch=8, sp2=2) - (2 * E_ETHYLENE), "desc": "Две двойные связи сливаются. Одна из них распрямляется в одинарную. Матрица рада снять штраф SP2! Профит: ~90 кДж."},
            {"step": "Butene + C2H4 ➔ 1-Hexene", "val": get_chem_energy(bonds_cc=6, bonds_ch=12, sp2=2) - get_chem_energy(bonds_cc=4, bonds_ch=8, sp2=2) - E_ETHYLENE, "desc": "Еще одна двойная связь распрямилась. Стабильный маржинальный профит."},
            {"step": "Hexene + C2H4 ➔ 1-Octene", "val": get_chem_energy(bonds_cc=8, bonds_ch=16, sp2=2) - get_chem_energy(bonds_cc=6, bonds_ch=12, sp2=2) - E_ETHYLENE, "desc": "Матрице выгодно строить пластик до бесконечности. Это автоматический BugFix изломов."}
        ],
        "2. Токенизация Ароматики (Тримеризация Бензола)": [
            {"step": "C2H2 + C2H2 ➔ Vinylacetylene", "val": get_chem_energy(bonds_cc=6, bonds_ch=4, sp=2, sp2=2) - (2 * E_ACETYLENE), "desc": "Слияние двух ацетиленов. Матрица сильно сопротивляется: в молекуле адское натяжение (два SP и два SP2 узла). Профит скромный."},
            {"step": "Vinylacetylene + C2H2 ➔ BENZENE", "val": get_chem_energy(bonds_cc=9, bonds_ch=6, sp2=6, token_ring=True) - get_chem_energy(bonds_cc=6, bonds_ch=4, sp=2, sp2=2) - E_ACETYLENE, "desc": "💎 ДЖЕКПОТ! Замыкается 6-е звено. Матрица опознает 2D-гексагон, стирает ВСЕ штрафы за натяжение и включает Token Ring. Энергия обрушивается вниз водопадом!"}
        ],
        "3. Углеродное Горение (Железный Пик Химии: CO2)": [
            {"step": "C + O ➔ C=O (Carbon Monoxide)", "val": get_chem_energy(bonds_co=2, sp=1) - 0, "desc": "Базовая дедупликация портов C и O. Выделение первой порции тепла."},
            {"step": "C=O + O ➔ O=C=O (Hardware Lock)", "val": get_chem_energy(bonds_co=4, hw_lock=True) - get_chem_energy(bonds_co=2, sp=1), "desc": "🔥 АКТИВАЦИЯ ЗАМКА! Матрице алгоритмически настолько выгодно залочить эти три узла в прямую линию, что она выдает гигантский экстра-бонус. CO2 — это 'Железо-56' органической химии!"}
        ]
    }
    
    selected_path = st.selectbox("Выберите путь молекулярной сборки:", list(pathways.keys()))
    steps = pathways[selected_path]
    
    fig3 = go.Figure(go.Waterfall(
        name="Энергия Синтеза", orientation="v",
        measure=["relative"] * len(steps) + ["total"],
        x=[s["step"] for s in steps] + ["ИТОГОВЫЙ ПРОФИТ СБОРКИ"],
        textposition="outside",
        text=[f"+{s['val']:.1f}" for s in steps] + [f"<b>{sum([s['val'] for s in steps]):.1f} kJ/mol</b>"],
        y=[s["val"] for s in steps] + [sum([s['val'] for s in steps])],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
        decreasing={"marker":{"color":"#FF4500"}}, increasing={"marker":{"color":"#00E676"}}, totals={"marker":{"color":"#1E90FF"}}
    ))
    fig3.update_layout(title="Водопад Вычислительного Профита (Выделение Тепла шаг за шагом)", template="plotly_dark", yaxis_title="Marginal Profit (kJ/mol)")
    st.plotly_chart(fig3, use_container_width=True)
    
    for i, s in enumerate(steps):
        st.info(f"**Шаг {i+1}:** {s['desc']} (Профит: **+{s['val']:.1f} kJ/mol**)")

with tab2:
    st.subheader("Симуляция звездного нуклеосинтеза (Alpha-процесс)")
    st.markdown("Тот же алгоритм `MERGE`, но для атомных ядер. Железная стена возникает эмерджентно: Кулоновский налог на маршрутизацию превышает профит сборки нового тетраэдра.")
    if st.button("Запустить цепочку альфа-захвата", type="primary", key="btn_ladder"):
        ladder_results = []
        current_Z, current_N = 2, 2 
        elements = ["He", "Be", "C", "O", "Ne", "Mg", "Si", "S", "Ar", "Ca", "Ti", "Cr", "Fe", "Ni", "Zn"]
        for idx in range(1, 14):
            target_Z, target_N = current_Z + 2, current_N + 2
            step_profit = get_fusion_profit(current_Z, current_N, 2, 2)
            ladder_results.append({
                "Reaction": f"Z={current_Z} + He-4 ➔ {elements[idx]}-{target_Z+target_N}",
                "Product Z": target_Z, "Marginal Profit (MeV)": step_profit,
                "Verdict": "✅ Одобрено (Star Burns)" if step_profit > 0 else "🚨 Заблокировано (Endothermic)"
            })
            current_Z, current_N = target_Z, target_N
            
        df_ladder = pd.DataFrame(ladder_results)
        fig1 = px.bar(df_ladder, x="Product Z", y="Marginal Profit (MeV)", color="Verdict", text_auto='.2f', color_discrete_map={"✅ Одобрено (Star Burns)": "#00FF7F", "🚨 Заблокировано (Endothermic)": "#FF4500"})
        fig1.update_layout(template="plotly_dark")
        fig1.add_hline(y=0, line_width=2, line_color="white")
        st.plotly_chart(fig1, use_container_width=True)

with tab3:
    st.subheader("Налог на коллизию и Аппаратный Latch Timeout")
    st.markdown("Внешнее давление (Гравитация) заставляет Матрицу одобрять убыточные транзакции, чтобы избавиться от коллизии.")
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        z1, n1 = st.number_input("Fragment 1 (Z)", 1, 6), st.number_input("Fragment 1 (N)", 0, 6)
        z2, n2 = st.number_input("Fragment 2 (Z)", 1, 6), st.number_input("Fragment 2 (N)", 0, 6)
    with col_c2:
        pressure = st.slider("Гравитационное Давление (Collision Tax, MeV)", 0.0, 25.0, 0.0, 0.5)
        profit = get_fusion_profit(z1, n1, z2, n2, confinement_tax_mev=pressure)
        st.divider()
        if profit > 0: st.success(f"🔥 УСПЕХ: Зажигание! Матрица спаяла блоки. Выход энергии: +{profit:.2f} МэВ")
        else: st.error(f"❄️ ОТКАЗ: Давления недостаточно. Слияние заблокировано: {profit:.2f} МэВ")

    st.divider()
    imp = st.slider("Lattice Impedance (Сопротивление Кулоном)", 10.0, 150.0, 80.0, 10.0)
    latch = st.slider("Matrix Latch Timeout Speed (Тактовая частота)", 50.0, 300.0, 120.0, 10.0)
    df_gamow = simulate_gamow_peak(imp, latch)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Grid Yielding Prob"], name="Успех Прогиба Сетки", line=dict(dash='dash', color='#00BFFF')))
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Matrix Latch Prob"], name="Успех Коммита", line=dict(dash='dash', color='#FF4500')))
    fig2.add_trace(go.Scatter(x=df_gamow["Kinetic Energy (keV)"], y=df_gamow["Fusion Cross-Section"], name="Пик Гамова", line=dict(color='#32CD32', width=4), fill='tozeroy'))
    fig2.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)
