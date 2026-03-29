import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================================
# SIMUREALITY: STELLAR NUCLEOSYNTHESIS & FUSION ENGINE
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

def get_jitter_tax(Z, N):
    if Z <= 0 or N <= 0: return 0
    dist_Z, dist_N = min([abs(Z - m) for m in MAGIC_NODES]), min([abs(N - m) for m in MAGIC_NODES])
    base_ports = 10.0 * ((Z + N)**(2/3))
    return (base_ports + (15.0 * ((dist_Z + dist_N)**1.2))) * J_TAX

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

def get_fusion_profit(Z1, N1, Z2, N2):
    """Вычисляет профит от геометрического слияния двух блоков"""
    E_parent = get_total_matrix_energy(Z1 + Z2, N1 + N2)
    E_frag1 = get_total_matrix_energy(Z1, N1)
    E_frag2 = get_total_matrix_energy(Z2, N2)
    return E_parent - (E_frag1 + E_frag2)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Fusion Matrix Assembly", layout="wide")
st.title("☀️ Stellar Nucleosynthesis: Grid Assembly")

tab1, tab2 = st.tabs(["🪜 Alpha Ladder (Stellar Core)", "⚡ Custom Fusion (Tokamak)"])

with tab1:
    st.markdown("Симуляция звездного нуклеосинтеза: последовательное присоединение тетраэдров Гелия-4 к растущему макро-кристаллу.")
    
    if st.button("Запустить цепочку альфа-захвата", type="primary"):
        ladder_results = []
        current_Z, current_N = 2, 2 # Стартуем с Гелия-4
        
        # Симулируем сборку вплоть до Цинка
        for _ in range(14):
            target_Z, target_N = current_Z + 2, current_N + 2
            step_profit = get_fusion_profit(current_Z, current_N, 2, 2)
            
            ladder_results.append({
                "Reaction": f"Z={current_Z} + He-4 ➔ Z={target_Z}",
                "Product Z": target_Z,
                "Product Mass (A)": target_Z + target_N,
                "Fusion Profit (MeV)": step_profit,
                "Verdict": "✅ Одобрено (Экзотермическая)" if step_profit > 0 else "🚨 Заблокировано (Эндотермическая)"
            })
            current_Z, current_N = target_Z, target_N
            
        df_ladder = pd.DataFrame(ladder_results)
        
        st.subheader("Лог сборки решетки")
        
        fig = px.bar(df_ladder, x="Product Z", y="Fusion Profit (MeV)", 
                     color="Verdict", text_auto='.2f',
                     color_discrete_map={"✅ Одобрено (Экзотермическая)": "#00BFFF", "🚨 Заблокировано (Эндотермическая)": "#FF4B4B"})
        fig.update_layout(xaxis_title="Protons (Z) of Product", yaxis_title="Energy Released per Alpha Block (MeV)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_ladder, use_container_width=True)

with tab2:
    st.markdown("Свободный конструктор: проверка слияния любых двух легких блоков.")
    c1, c2, c3, c4 = st.columns(4)
    z1 = c1.number_input("Fragment 1 (Z)", min_value=1, value=1, step=1)
    n1 = c2.number_input("Fragment 1 (N)", min_value=0, value=1, step=1) # D
    z2 = c3.number_input("Fragment 2 (Z)", min_value=1, value=1, step=1)
    n2 = c4.number_input("Fragment 2 (N)", min_value=0, value=2, step=1) # T
    
    if st.button("Выполнить слияние"):
        profit = get_fusion_profit(z1, n1, z2, n2)
        total_Z, total_N = z1 + z2, n1 + n2
        
        st.divider()
        if profit > 0:
            st.success(f"🔥 УСПЕХ: Вакуум одобрил слияние. Выход энергии: {profit:.2f} МэВ")
        else:
            st.error(f"❄️ ОТКАЗ: Сборка невыгодна. Энергия поглощается: {profit:.2f} МэВ")
            
        m1, m2 = st.columns(2)
        m1.metric("Собранный кристалл (Z)", total_Z)
        m2.metric("Собранный кристалл (Mass)", total_Z + total_N)
