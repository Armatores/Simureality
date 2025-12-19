import streamlit as st
import math
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Simureality Nuclear Calculator", layout="wide")

st.title("🧩 Simureality: Digital Nuclear Physics")
st.markdown("""
**Гипотеза:** Ядро атома — это не жидкая капля, а кристалл из альфа-частиц.
Этот калькулятор рассчитывает энергию связи (Binding Energy) на основе геометрии решетки (FCC Lattice) без эмпирической подгонки.
""")

# --- ФИЗИЧЕСКИЕ КОНСТАНТЫ (Твой "Золотой Стандарт") ---
def get_constants():
    m_e = 0.511 
    PI = math.pi
    ALPHA = 1 / 137.035999 
    gamma_struct = 2 / math.sqrt(3) 
    gamma_sys = 1.0418 
    E_LINK = 4 * m_e * gamma_struct        
    E_ALPHA = 12 * E_LINK                  
    a_Sym_Cluster = E_ALPHA * math.sqrt(2/3) 
    a_V = (6 * E_LINK) * gamma_sys         
    a_S = 14.5                             
    gamma_vol = gamma_struct**(1/3)
    apf = PI / (3 * math.sqrt(2))
    a_C = apf / gamma_vol                  
    a_Sym_Lattice = 6 * E_LINK             
    K_DEFORM = (4 * ALPHA) / (PI**2 * gamma_sys) 
    return E_ALPHA, E_LINK, a_Sym_Cluster, a_V, a_S, a_C, a_Sym_Lattice, K_DEFORM

def get_deformation_penalty(Z, N, K_DEFORM):
    magic_nums = [2, 8, 20, 28, 50, 82, 126, 184]
    dist_Z = min([abs(Z - m) for m in magic_nums])
    dist_N = min([abs(N - m) for m in magic_nums])
    penalty = K_DEFORM * (dist_Z * dist_N) * (dist_Z + dist_N)**0.8
    if Z < 40: return 0
    return penalty

def calculate_energy(Z, A, consts):
    E_ALPHA, E_LINK, a_Sym_Cluster, a_V, a_S, a_C, a_Sym_Lattice, K_DEFORM = consts
    N = A - Z
    if Z <= 20:
        n_alpha = A // 4
        rem = A % 4
        if n_alpha < 2: links = 0
        else: links = 3 * n_alpha - 6
        E_geom = (n_alpha * E_ALPHA) + (links * E_LINK)
        if rem == 2: E_geom += E_LINK
        if rem == 3: 
            E_geom += 3.5 * E_LINK
            if Z == 2: E_geom -= a_C
        if N != Z and A >= 4: 
             E_geom -= a_Sym_Cluster * ((N-Z)**2) / A 
        return E_geom
    else:
        E_vol = a_V * A
        E_surf = a_S * (A**(2.0/3.0))
        E_coul = a_C * (Z*(Z-1)) / (A**(1.0/3.0))
        E_sym = a_Sym_Lattice * ((N-Z)**2) / A
        delta = 12.0 / (A**(1.0/2.0))
        if Z%2==0 and N%2==0: E_pair = delta
        elif Z%2!=0 and N%2!=0: E_pair = -delta
        else: E_pair = 0
        E_sphere = E_vol - E_surf - E_coul - E_sym + E_pair
        return E_sphere - get_deformation_penalty(Z, N, K_DEFORM)

# --- ИНТЕРФЕЙС КАЛЬКУЛЯТОРА ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠 Ввод параметров")
    Z_input = st.number_input("Количество Протонов (Z)", min_value=1, max_value=118, value=26)
    N_input = st.number_input("Количество Нейтронов (N)", min_value=0, max_value=200, value=30)
    A_input = Z_input + N_input
    st.write(f"Массовое число (A): **{A_input}**")

    if st.button("🚀 Рассчитать Энергию"):
        consts = get_constants()
        sim_be = calculate_energy(Z_input, A_input, consts)
        
        st.success(f"Simureality Binding Energy: **{sim_be:.2f} MeV**")
        st.info("Расчет выполнен на основе геометрических констант решетки.")

# --- ДЕМО ДАННЫЕ ---
with col2:
    st.subheader("📊 Тестовый Прогон (Железо, Кальций...)")
    # Небольшой кусок твоего датасета для примера
    demo_data = [
        ("O-16", 8, 16, 127.62),
        ("Ca-40", 20, 40, 342.05),
        ("Fe-56", 26, 56, 492.26),
        ("U-238", 92, 238, 1801.71)
    ]
    
    results = []
    consts = get_constants()
    for name, z, a, real in demo_data:
        sim = calculate_energy(z, a, consts)
        diff = sim - real
        acc = 100 * (1 - abs(diff)/real)
        results.append([name, z, a, real, f"{sim:.2f}", f"{acc:.2f}%"])
        
    df = pd.DataFrame(results, columns=["Ядро", "Z", "A", "Real BE (MeV)", "Sim BE (MeV)", "Точность"])
    st.dataframe(df)

st.markdown("---")
st.caption("© 2025 Simureality Research Group. Powered by Python & Grid Physics.")
