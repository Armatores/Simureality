import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V14.0 ULTIMATE TOPO-BOND SCANNER
# 100+ Bonds Stress Test for 1D/3D Grid Quantization
# =====================================================================

GAMMA_SYS = 1.0418  # Системный Налог Матрицы

# Массив из 100+ экспериментальных энергий связей (кДж/моль)
BOND_DATA = {
    # 1. Base Organics & Hydrogen
    'H-H': 436, 'C-H': 413, 'N-H': 391, 'O-H': 463, 'F-H': 567,
    'Cl-H': 431, 'Br-H': 366, 'I-H': 299,
    # 2. Carbon Network
    'C-C': 348, 'C=C': 614, 'C#C': 839,
    'C-N': 293, 'C=N': 615, 'C#N': 891,
    'C-O': 358, 'C=O': 799, 'C#O': 1072,
    'C-F': 485, 'C-Cl': 328, 'C-Br': 276, 'C-I': 240,
    # 3. Nitrogen & Oxygen Network
    'N-N': 163, 'N=N': 418, 'N#N': 941,
    'N-O': 201, 'N=O': 607, 'N-F': 272, 'N-Cl': 200, 'N-Br': 243,
    'O-O': 146, 'O=O': 495, 'O-F': 190, 'O-Cl': 203, 'O-Br': 234,
    # 4. Halogens (Pure 1D Links)
    'F-F': 159, 'Cl-Cl': 242, 'Br-Br': 193, 'I-I': 151,
    # 5. Silicon Group
    'Si-H': 318, 'Si-C': 301, 'Si-Si': 226, 'Si-O': 452, 
    'Si-F': 590, 'Si-Cl': 400, 'Si-Br': 310, 'Si-I': 234,
    # 6. Phosphorus & Sulfur Group
    'P-H': 322, 'P-C': 264, 'P-P': 213, 'P-O': 335, 'P=O': 544, 
    'P-F': 490, 'P-Cl': 331, 'P-Br': 272, 'P-I': 184,
    'S-H': 339, 'S-C': 259, 'S=C': 477, 'S-S': 226, 'S=S': 425, 
    'S-O': 265, 'S=O': 523, 'S-F': 327, 'S-Cl': 253, 'S-Br': 218,
    # 7. Boron Group
    'B-H': 381, 'B-C': 372, 'B-O': 523, 'B-F': 613, 'B-Cl': 443, 'B-Br': 377,
    # 8. Heavy Metalloids & Chalcogens (Stress Test for Volumetric Tension)
    'Ge-Ge': 188, 'Ge-C': 255, 'Ge-H': 288, 'Ge-O': 360, 'Ge-Cl': 340, 'Ge-F': 470,
    'Sn-Sn': 150, 'Sn-C': 225, 'Sn-H': 251, 'Sn-O': 531, 'Sn-Cl': 320, 'Sn-F': 414,
    'Pb-Pb': 86, 'Pb-C': 130, 'Pb-H': 176, 'Pb-O': 382, 'Pb-Cl': 240, 'Pb-F': 310,
    'Se-Se': 209, 'Se-H': 276, 'Se-C': 243, 'Se-O': 343, 'Se-Cl': 245,
    'Te-Te': 138, 'Te-H': 238, 'Te-C': 200, 'Te-O': 268, 'Te-Cl': 240,
    'As-As': 180, 'As-H': 297, 'As-C': 200, 'As-O': 481, 'As-Cl': 290,
    'Sb-Sb': 142, 'Sb-H': 240, 'Sb-C': 215, 'Sb-O': 422, 'Sb-Cl': 310,
    # 9. Metals (Ionic & Crystal Interfaces)
    'Na-Cl': 411, 'K-Cl': 433, 'Li-F': 577, 'Al-O': 511, 'Be-O': 536, 
    'Mg-O': 394, 'Ca-O': 464, 'Ti-O': 672, 'Fe-O': 409, 'Cu-O': 269, 'Zn-O': 284, 'Ag-O': 222
}

def find_optimal_quantum(bonds, gamma):
    best_e_base = 0
    best_variance = float('inf')
    
    # Сканируем от 5 до 50, чтобы захватить и 1D квант (~12), и 3D квант (~36)
    test_bases = np.arange(5.0, 50.0, 0.05)
    energies = np.array(list(bonds.values()))
    taxed_energies = energies / gamma
    
    for e_base in test_bases:
        n_ports = taxed_energies / e_base
        variance = np.sum(np.abs(n_ports - np.round(n_ports)))
        
        if variance < best_variance:
            best_variance = variance
            best_e_base = e_base
            
    return best_e_base

def build_dataframe(bonds, e_base, gamma):
    results = []
    for bond, energy in bonds.items():
        taxed_energy = energy / gamma
        n_ports_raw = taxed_energy / e_base
        n_ports_int = int(np.round(n_ports_raw))
        
        predicted_energy = n_ports_int * e_base * gamma
        error = abs(predicted_energy - energy) / energy * 100
        
        results.append({
            "Связь": bond,
            "Энергия ЦЕРН (кДж/моль)": energy,
            "Расчетные 1D/3D Порты (N)": round(n_ports_raw, 2),
            "Lattice Links (Целые)": n_ports_int,
            "Предсказанная Энергия": round(predicted_energy, 1),
            "Ошибка (%)": round(error, 2)
        })
        
    df = pd.DataFrame(results)
    return df.sort_values(by="Ошибка (%)").reset_index(drop=True)

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="V14.0 Ultimate Topo-Bond Scanner", layout="wide")

st.title("🌌 V14.0: Ultimate Topo-Bond Scanner (100+ Dataset)")
st.markdown("""
Финальный стресс-тест гипотезы дискретности. В базу загружено **более 100** различных химических связей (включая тяжелые металлы, халькогены и металлоиды). 
Задача скрипта: подтвердить существование фундаментального 1D-кванта решетки (около 12 кДж/моль) или 3D-кванта (около 36.6 кДж/моль) в условиях экстремального топологического шума.
""")

st.sidebar.header("Параметры Матрицы")
gamma_input = st.sidebar.number_input("Системный Налог (Gamma)", value=GAMMA_SYS, format="%.4f")
st.sidebar.markdown(f"Загружено молекулярных связей: **{len(BOND_DATA)}**")

if st.button("Инициировать Брутфорс ГЦК-Кванта (100+)", type="primary"):
    with st.spinner("Декомпиляция 100+ энергетических уровней..."):
        optimal_e_base = find_optimal_quantum(BOND_DATA, gamma_input)
        df_results = build_dataframe(BOND_DATA, optimal_e_base, gamma_input)
        mean_error = df_results['Ошибка (%)'].mean()
        
    st.success("Декомпиляция завершена.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Оптимальный Квант ($E_{base}$)", f"{optimal_e_base:.2f} кДж/моль")
    col2.metric("Стоимость с Налогом (x Gamma)", f"{(optimal_e_base * gamma_input):.2f} кДж/моль")
    col3.metric("Средняя Погрешность", f"{mean_error:.2f}%")
    
    st.markdown("### Глобальная Матрица Дискретных Связей")
    
    def color_error(val):
        color = '#00E676' if val < 2.0 else '#FFD600' if val < 5.0 else '#FF1744'
        return f'color: {color}'
    
    st.dataframe(df_results.style.map(color_error, subset=['Ошибка (%)']), use_container_width=True, height=500)
    
    st.markdown("### Карта Топологического Шума")
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_results["Lattice Links (Целые)"], 
        y=df_results["Энергия ЦЕРН (кДж/моль)"],
        mode='markers', name='Химические связи',
        text=df_results["Связь"],
        hovertemplate="<b>%{text}</b><br>Энергия: %{y} кДж/моль<br>Линки: %{x}<extra></extra>",
        marker=dict(
            color=df_results["Ошибка (%)"],
            colorscale='Inferno',
            size=10,
            showscale=True,
            colorbar=dict(title="Ошибка (%)")
        )
    ))
    
    fig.update_layout(
        title="Стресс-Тест: 100+ связей на дискретной ГЦК-сетке",
        xaxis_title="Количество Замкнутых Линков (N)",
        yaxis_title="Энергия Связи (кДж/моль)",
        template="plotly_dark",
        hovermode="closest"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Аналитика для Архитектора:** Если оптимальный квант снова упадет в район ~12 кДж/моль (1D-вектор) или ~36 кДж/моль (3D-трилекс), а средняя ошибка останется в пределах 2-4% несмотря на добавление тяжелых узлов (Свинец, Олово, Теллур) — это абсолютная победа. Это докажет, что даже тяжелые элементы с гигантским топологическим рычагом подчиняются единой геометрии базового вектора Матрицы.")
