import streamlit as st
import math
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Simureality Nuclear Calculator", layout="wide", page_icon="⚛️")

# --- БАЗА ДАННЫХ (ИЗ ТВОЕГО СКРИПТА EN 249) ---
# Мы используем это как "Справочник официальной науки" для сравнения
DATASET = [
    ("H-2", 1, 2, 2.22), ("H-3", 1, 3, 8.48), ("He-3", 2, 3, 7.72), ("He-4", 2, 4, 28.30),
    ("Li-6", 3, 6, 32.00), ("Li-7", 3, 7, 39.24), ("Be-9", 4, 9, 58.16), ("B-10", 5, 10, 64.75),
    ("B-11", 5, 11, 76.20), ("C-12", 6, 12, 92.16), ("C-13", 6, 13, 97.11), ("N-14", 7, 14, 104.66),
    ("O-16", 8, 16, 127.62), ("O-17", 8, 17, 131.76), ("O-18", 8, 18, 139.81), ("F-19", 9, 19, 147.80),
    ("Ne-20", 10, 20, 160.64), ("Na-23", 11, 23, 186.56), ("Mg-24", 12, 24, 198.26), ("Al-27", 13, 27, 224.95),
    ("Si-28", 14, 28, 236.54), ("P-31", 15, 31, 262.92), ("S-32", 16, 32, 271.78), ("Cl-35", 17, 35, 298.21),
    ("Ar-40", 18, 40, 343.81), ("K-39", 19, 39, 333.72), ("Ca-40", 20, 40, 342.05), ("Sc-45", 21, 45, 387.85),
    ("Ti-48", 22, 48, 418.70), ("V-51", 23, 51, 445.84), ("Cr-52", 24, 52, 456.35), ("Mn-55", 25, 55, 482.59),
    ("Fe-56", 26, 56, 492.26), ("Co-59", 27, 59, 517.31), ("Ni-58", 28, 58, 506.46), ("Cu-63", 29, 63, 551.38),
    ("Zn-64", 30, 64, 559.10), ("Ga-69", 31, 69, 602.01), ("Ge-74", 32, 74, 645.69), ("As-75", 33, 75, 652.57),
    ("Se-80", 34, 80, 695.88), ("Br-79", 35, 79, 686.22), ("Kr-84", 36, 84, 732.25), ("Rb-85", 37, 85, 739.75),
    ("Sr-88", 38, 88, 768.47), ("Y-89", 39, 89, 775.58), ("Zr-90", 40, 90, 783.91), ("Nb-93", 41, 93, 808.50),
    ("Mo-98", 42, 98, 846.10), ("Tc-99", 43, 99, 852.74), ("Ru-102", 44, 102, 878.85), ("Rh-103", 45, 103, 884.58),
    ("Pd-106", 46, 106, 906.51), ("Ag-107", 47, 107, 915.22), ("Cd-114", 48, 114, 975.33), ("In-115", 49, 115, 980.71),
    ("Sn-120", 50, 120, 1029.20), ("Sb-121", 51, 121, 1030.80), ("Te-130", 52, 130, 1093.00), ("I-127", 53, 127, 1072.58),
    ("Xe-132", 54, 132, 1102.93), ("Cs-133", 55, 133, 1110.49), ("Ba-138", 56, 138, 1158.29), ("La-139", 57, 139, 1163.74),
    ("Ce-140", 58, 140, 1172.69), ("Pr-141", 59, 141, 1179.80), ("Nd-142", 60, 142, 1185.12), ("Sm-152", 62, 152, 1243.14),
    ("Eu-153", 63, 153, 1248.60), ("Gd-158", 64, 158, 1282.74), ("Tb-159", 65, 159, 1288.74), ("Dy-164", 66, 164, 1319.45),
    ("Ho-165", 67, 165, 1326.63), ("Er-166", 68, 166, 1337.81), ("Tm-169", 69, 169, 1354.34), ("Yb-174", 70, 174, 1386.43),
    ("Lu-175", 71, 175, 1393.91), ("Hf-180", 72, 180, 1428.14), ("Ta-181", 73, 181, 1433.80), ("W-184", 74, 184, 1459.20),
    ("Re-187", 75, 187, 1476.01), ("Os-192", 76, 192, 1515.00), ("Ir-193", 77, 193, 1520.13), ("Pt-195", 78, 195, 1533.12),
    ("Au-197", 79, 197, 1545.60), ("Hg-202", 80, 202, 1581.63), ("Tl-205", 81, 205, 1603.20), ("Pb-208", 82, 208, 1636.45),
    ("Bi-209", 83, 209, 1640.24), ("Th-232", 90, 232, 1766.68), ("U-238", 92, 238, 1801.71)
]

# Создаем удобный справочник для поиска
reference_dict = {}
for name, z, a, be in DATASET:
    element_symbol = name.split('-')[0]
    reference_dict[(z, a)] = {"name": name, "real_be": be}
    
# Таблица для сайдбара
df_ref = pd.DataFrame(DATASET, columns=["Изотоп", "Z (Протоны)", "A (Масса)", "Real BE"])
df_ref["N (Нейтроны)"] = df_ref["A (Масса)"] - df_ref["Z (Протоны)"] # Добавим колонку N

# --- ФИЗИЧЕСКОЕ ЯДРО (SIMUREALITY) ---
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

# --- БОКОВАЯ ПАНЕЛЬ (ШПАРГАЛКА) ---
with st.sidebar:
    st.header("📚 Справочник Изотопов")
    st.write("Не знаешь сколько нейтронов? Посмотри здесь:")
    st.dataframe(df_ref[["Изотоп", "Z (Протоны)", "N (Нейтроны)"]], height=600)

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("🧩 Simureality: Digital Nuclear Physics")
st.markdown("""
**Калькулятор Энергии Связи Ядра**
*Введите количество протонов и нейтронов, чтобы рассчитать энергию связи (Binding Energy) по геометрическому алгоритму Simureality.*
""")

# Контейнер для ввода
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        Z_input = st.number_input("Количество Протонов (Z)", min_value=1, max_value=118, value=26)
    with col2:
        N_input = st.number_input("Количество Нейтронов (N)", min_value=0, max_value=200, value=30) # Default для Fe-56
    
    A_input = Z_input + N_input
    
    # Кнопка расчета
    if st.button("🚀 Рассчитать Энергию", type="primary", use_container_width=True):
        consts = get_constants()
        sim_be = calculate_energy(Z_input, A_input, consts)
        
        # Поиск в базе данных
        ref_data = reference_dict.get((Z_input, A_input))
        
        st.divider()
        st.subheader("📊 Результаты Анализа")
        
        # Блок 1: Идентификация
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Массовое число (A)", value=f"{A_input}")
        with col_res2:
            if ref_data:
                element_name = ref_data['name']
                st.success(f"🔍 Элемент определен: **{element_name}**")
            else:
                st.warning(f"⚠️ Неизвестный изотоп (Z={Z_input}, N={N_input})")

        # Блок 2: Энергия и Сравнение
        st.markdown("### ⚡ Энергия Связи (Binding Energy)")
        
        if ref_data:
            real_be = ref_data['real_be']
            diff = sim_be - real_be
            accuracy = 100 * (1 - abs(diff)/real_be)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Simureality (Наш расчет)", f"{sim_be:.2f} MeV")
            c2.metric("Официальная Наука", f"{real_be:.2f} MeV")
            c3.metric("Точность", f"{accuracy:.3f}%", delta=f"{diff:+.2f} MeV")
            
            if accuracy > 99.0:
                st.balloons()
                st.success("🎯 **Фантастическая точность!** Геометрия работает.")
        else:
            st.metric("Simureality Prediction", f"{sim_be:.2f} MeV")
            st.info("Для этого редкого изотопа у нас нет официальных данных в справочнике для сравнения, но расчет выполнен корректно.")

st.markdown("---")
st.caption("© 2025 Simureality Research Group. Данные основаны на алгоритме 'Grid Physics'.")
