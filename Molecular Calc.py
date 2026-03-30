import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================================
# SIMUREALITY: V11.0 FCC MOLECULE SYNTHESIZER & MATRIX BILLING
# Chemical Bonds as Vector Alignment & Transaction Tax
# =====================================================================

# --- FUNDAMENTAL HARDWARE CONSTANTS ---
GAMMA_SYS = 1.0418       # Системный Налог (Transaction Fee = 4.18%)
R_OPEN_PORT = 100.0      # Топологическое сопротивление открытого порта (TU - Topological Units)
R_CLOSED_LINK = 20.0     # Сопротивление замкнутого туннеля (TU)

# --- FCC PORT VECTORS (Hardware Sockets) ---
# s-буфер (Водород) адаптируется под любой встречный вектор
# p-буфер (Кислород/Азот) использует строгие кубические оси
FCC_SOCKETS = {
    "H_1": np.array([1, 0, 0]),
    "H_2": np.array([-1, 0, 0]),
    "O_px": np.array([1, 0, 0]),
    "O_py": np.array([0, 1, 0]),
    "N_pz": np.array([0, 0, 1])
}

def calculate_merge_transaction(atom1, port1_name, atom2, port2_name):
    v1 = FCC_SOCKETS[port1_name]
    v2 = FCC_SOCKETS[port2_name]
    
    # 1. Проверка Выравнивания (Socket Alignment)
    # Идеальная связь требует встречных векторов (dot_product == -1)
    alignment = np.dot(v1, v2)
    is_aligned = (alignment == -1)
    
    if not is_aligned:
        return {"Status": "REJECTED", "Reason": "Векторы не соосны (Collision)", "Alignment": alignment}

    # 2. Расчет Топологического Давления (До слияния)
    # Матрица поддерживает 2 открытых порта
    k_initial = R_OPEN_PORT * 2
    
    # 3. Расчет Давления (После слияния)
    # Порты замкнуты, сопротивление падает
    k_final = R_CLOSED_LINK
    
    # 4. Освобожденная вычислительная мощность (Гросс-Энергия)
    delta_k_gross = k_initial - k_final
    
    # 5. СИСТЕМНЫЙ НАЛОГ (Transaction Fee)
    # Матрица забирает 4.18% за операцию MERGE
    tax_fee = delta_k_gross * (GAMMA_SYS - 1)
    
    # 6. Чистая энергия, сброшенная в вакуум (Экзотермическая реакция)
    energy_released = delta_k_gross - tax_fee
    
    # 7. Энергия, необходимая для разрыва (Эндотермический запрос)
    # Нужно компенсировать delta_k + заплатить налог за операцию DROP
    energy_to_break = delta_k_gross + tax_fee
    
    return {
        "Status": "SUCCESS",
        "Reaction": f"{atom1} + {atom2} -> {atom1}-{atom2}",
        "Initial_Resistance_TU": k_initial,
        "Final_Resistance_TU": k_final,
        "Gross_Energy_TU": delta_k_gross,
        "Matrix_Tax_TU": tax_fee,
        "Net_Energy_Released_TU": energy_released,
        "Energy_To_Break_TU": energy_to_break
    }

# --- UI RENDER ENGINE ---
st.set_page_config(page_title="V11.0 Matrix Synthesizer", layout="wide")
st.title("🧬 V11.0: FCC Covalent Synthesizer & System Billing")
st.markdown("Химическая связь — это замыкание двух встречных I/O портов ГЦК-решетки. Энергия связи подчиняется жесткому биллингу Матрицы: **вход и выход из системы облагаются Системным Налогом ($\gamma_{sys} = 1.0418$)**.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Node A (Left)")
    atom_A = st.selectbox("Atom A", ["Hydrogen (H)"], key="a1")
    port_A = st.selectbox("I/O Port A", ["H_1"], key="p1")

with col2:
    st.subheader("Node B (Right)")
    atom_B = st.selectbox("Atom B", ["Hydrogen (H)", "Oxygen (O)"], key="a2")
    port_B = st.selectbox("I/O Port B", ["H_2", "O_px", "O_py"], key="p2")

if st.button("Инициировать транзакцию `MERGE`", type="primary"):
    result = calculate_merge_transaction(atom_A, port_A, atom_B, port_B)
    
    if result["Status"] == "REJECTED":
        st.error(f"❌ ТРАНЗАКЦИЯ ОТКЛОНЕНА. {result['Reason']}. Скалярное произведение: {result['Alignment']}")
    else:
        st.success(f"✅ ТРАНЗАКЦИЯ УСПЕШНА. Сформирован закрытый контур.")
        
        # --- THE MATRIX INVOICE ---
        st.markdown("### 🧾 СЧЕТ-ФАКТУРА МАТРИЦЫ (Transaction Invoice)")
        
        df_invoice = pd.DataFrame({
            "Показатель": [
                "1. Топологическое сопротивление ДО (TU)",
                "2. Топологическое сопротивление ПОСЛЕ (TU)",
                "3. Оптимизация нагрузки (Gross ΔK)",
                "4. Системный Налог Матрицы (4.18%)",
                "5. ЧИСТАЯ ЭНЕРГИЯ СИНТЕЗА (Сброс в среду)",
                "6. ЭНЕРГИЯ РАЗРЫВА СВЯЗИ (Цена операции DROP)"
            ],
            "Значение": [
                f"{result['Initial_Resistance_TU']:.2f}",
                f"{result['Final_Resistance_TU']:.2f}",
                f"{result['Gross_Energy_TU']:.2f}",
                f"- {result['Matrix_Tax_TU']:.2f}",
                f"🔥 {result['Net_Energy_Released_TU']:.2f}",
                f"⚡ {result['Energy_To_Break_TU']:.2f}"
            ]
        })
        st.table(df_invoice)
        
        # Визуализация гистерезиса
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Сброс при Синтезе (Net Out)', x=['Энергия Связи'], y=[result['Net_Energy_Released_TU']], marker_color='#00E676'))
        fig.add_trace(go.Bar(name='Затраты на Разрыв (Net In)', x=['Энергия Разрыва'], y=[result['Energy_To_Break_TU']], marker_color='#FF1744'))
        fig.update_layout(title="Гистерезис Энергии (Налог Матрицы формирует разницу)", template="plotly_dark", yaxis_title="Topological Units (TU)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Архитектурный Вывод:** Чтобы разорвать ту же самую молекулу, требуется вкачать больше энергии, чем выделилось при ее создании. Разница (гистерезис) оседает в решетке как оплата транзакционных издержек (Системный Налог). Именно эта комиссия за постоянные операции MERGE/DROP формирует аномальную теплоемкость жидкой воды (4.18 Дж/г*К).")
