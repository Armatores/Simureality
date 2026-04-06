import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# =====================================================================
# SIMUREALITY V34.0: SOLID-STATE GRID ENGINE (ENERGY STORAGE)
# Battery as an Asynchronous Data Migration Process
# =====================================================================

st.set_page_config(page_title="V34.0 Battery Engine", layout="wide", page_icon="🔋")

# --- БАЗА АППАРАТНЫХ КОМПОНЕНТОВ ---

# ПАКЕТЫ ДАННЫХ (Ионы)
# size_angstrom: размер пакета. valence: множитель профита (заряд). drag: сопротивление роутинга
CARRIERS = {
    "Li+ (Литий)": {"size_angstrom": 0.76, "valence": 1, "mass": 6.9, "drag": 1.0, "color": "#00d2ff"},
    "Na+ (Натрий)": {"size_angstrom": 1.02, "valence": 1, "mass": 23.0, "drag": 1.8, "color": "#f6d365"},
    "Mg2+ (Магний)": {"size_angstrom": 0.72, "valence": 2, "mass": 24.3, "drag": 3.5, "color": "#ff4444"},
    "K+ (Калий)": {"size_angstrom": 1.38, "valence": 1, "mass": 39.1, "drag": 2.5, "color": "#a18cd1"}
}

# RAM-БУФЕРЫ (Аноды)
# base_slots: Теоретическая емкость (mAh/g). voxel_expansion: % разбухания решетки при записи
# dendrite_risk: Вероятность утечки памяти (Memory Leak / КЗ)
ANODES = {
    "Графит (Graphite)": {"base_slots": 372, "voxel_expansion": 10.0, "dendrite_risk": 0.2, "debt_cost": 20},
    "Кремний (Silicon)": {"base_slots": 3579, "voxel_expansion": 300.0, "dendrite_risk": 0.1, "debt_cost": 85},
    "Чистый Металл (Lithium/Sodium)": {"base_slots": 3860, "voxel_expansion": 0.0, "dendrite_risk": 0.99, "debt_cost": 5},
    "Титанат (LTO)": {"base_slots": 175, "voxel_expansion": 0.2, "dendrite_risk": 0.01, "debt_cost": 150} # Сверхстабильный, но дорогой долг
}

# ROM-АРХИВЫ (Катоды)
# hardware_lock_profit: Насколько Матрице "нравится" укладывать сюда ион (определяет Вольтаж)
# slot_weight: Масса контроллера (снижает плотность энергии)
CATHODES = {
    "LCO (LiCoO2) - 2D Слои": {"lock_profit": 420, "slot_weight": 98, "life_cycles": 1000},
    "LFP (LiFePO4) - 1D Тоннели": {"lock_profit": 350, "slot_weight": 158, "life_cycles": 4000}, # Жесткая 3D решетка
    "NMC (Никель-Марганец-Кобальт)": {"lock_profit": 380, "slot_weight": 97, "life_cycles": 2000},
    "Сера (Sulfur S8) - Жидкий Кэш": {"lock_profit": 230, "slot_weight": 32, "life_cycles": 200} # Огромная емкость, но структура распадается
}

def compile_battery_grid(carrier, anode, cathode):
    c_data = CARRIERS[carrier]
    a_data = ANODES[anode]
    k_data = CATHODES[cathode]
    
    # 1. СОВМЕСТИМОСТЬ ПАКЕТА (Voxel Clipping)
    # Если пакет (Натрий/Калий) слишком большой для стандартных 2D-слоев графита - транзакция отменяется
    if c_data["size_angstrom"] > 0.9 and anode == "Графит (Graphite)":
        return None, "💥 FATAL ERROR: Размер пакета данных (Иона) превышает пропускную способность шины Графита. Требуется другой Анод (Hard Carbon)."
        
    # 2. РАСЧЕТ НАПРЯЖЕНИЯ (Difference in Computational Debt)
    # Вольтаж = Профит фиксации в Катоде МИНУС Вычислительный долг хранения в Аноде МИНУС Сетевое сопротивление иона
    raw_voltage = (k_data["lock_profit"] * c_data["valence"] - a_data["debt_cost"] - (c_data["drag"] * 15)) / 100.0
    voltage = max(0.5, round(raw_voltage, 2))
    
    # 3. ЕМКОСТЬ И ПЛОТНОСТЬ ЭНЕРГИИ (Wh/kg)
    # Адаптируем емкость под размер пакета (магний несет х2 профита, но тяжелый)
    cathode_capacity = (26800 * c_data["valence"]) / k_data["slot_weight"]
    cell_capacity = 1 / ((1 / a_data["base_slots"]) + (1 / cathode_capacity))
    energy_density = round(cell_capacity * voltage, 0)
    
    # 4. ДЕГРАДАЦИЯ (Bad Sectors Creation)
    # Зависит от разбухания Анода (Voxel Strain) и нестабильности Катода
    strain_factor = a_data["voxel_expansion"] / 100.0
    dendrite_penalty = a_data["dendrite_risk"] * 500
    real_life_cycles = int(k_data["life_cycles"] / (1 + strain_factor) - dendrite_penalty)
    if carrier == "Mg2+ (Магний)": real_life_cycles = int(real_life_cycles * 0.5) # Магний "застревает" в решетке
    
    real_life_cycles = max(50, real_life_cycles)
    
    # 5. БЕЗОПАСНОСТЬ (Memory Leak Risk)
    safety_score = 100 - (a_data["dendrite_risk"] * 100) - (strain_factor * 10)
    safety_score = max(0, min(100, safety_score))
    
    return {
        "Voltage (V)": voltage,
        "Energy Density (Wh/kg)": energy_density,
        "Cycle Life": real_life_cycles,
        "Safety Score": safety_score,
        "Expansion": a_data["voxel_expansion"]
    }, "✅ Успешная компиляция"

# --- UI ---
st.title("🔋 V34.0: Grid Energy Compiler")
st.markdown("Здесь батарея — это **Асинхронный Процесс Миграции Данных**. Напряжение (V) — это Вычислительный Долг, а деградация — появление `Bad Sectors` из-за растяжения 3D-решетки.")

col1, col2, col3 = st.columns(3)
with col1:
    sel_carrier = st.selectbox("📦 Пакет Данных (Carrier Ion):", list(CARRIERS.keys()))
with col2:
    sel_anode = st.selectbox("📝 RAM-Буфер (Anode):", list(ANODES.keys()))
with col3:
    sel_cathode = st.selectbox("🗄️ ROM-Архив (Cathode):", list(CATHODES.keys()))

st.divider()

metrics, status = compile_battery_grid(sel_carrier, sel_anode, sel_cathode)

if not metrics:
    st.error(status)
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ Вычислительный Долг (Напряжение)", f"{metrics['Voltage (V)']} V", help="Разница профита между Катодом и Анодом.")
    c2.metric("🔋 Плотность данных (Energy Density)", f"{metrics['Energy Density (Wh/kg)']} Wh/kg", help="Сколько профита помещается в 1 кг аппаратной массы.")
    c3.metric("🔄 Срок службы (До Bad Sectors)", f"{metrics['Cycle Life']} циклов", help="Разрушение решетки из-за Voxel Strain (расширения).")
    
    safety_color = "normal" if metrics['Safety Score'] > 80 else ("inverse" if metrics['Safety Score'] < 40 else "off")
    c4.metric("🛡️ Защита от утечек (Безопасность)", f"{metrics['Safety Score']}%", delta="Риск Дендритов" if metrics['Safety Score'] < 40 else "Стабильно", delta_color=safety_color)
    
    # Визуализация Деградации
    st.markdown("### 📉 График появления Bad Sectors (Деградация Решетки)")
    cycles = np.linspace(0, metrics['Cycle Life'] * 1.5, 100)
    # Нелинейное падение емкости (ускоряется к концу из-за накопления микротрещин)
    capacity_drop = 100 - (100 * (cycles / metrics['Cycle Life']) ** (1.5 + (metrics['Expansion']/100)))
    capacity_drop = np.clip(capacity_drop, 0, 100)
    
    df_plot = pd.DataFrame({"Циклы (I/O Operations)": cycles, "Состояние Здоровья (SOH %)": capacity_drop})
    
    fig = px.line(df_plot, x="Циклы (I/O Operations)", y="Состояние Здоровья (SOH %)", 
                  color_discrete_sequence=[CARRIERS[sel_carrier]["color"]])
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="EoL (Замена Батареи)")
    fig.update_layout(template="plotly_dark", yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)
    
    # Системный лог
    st.markdown("### 🧠 Лог Архитектора:")
    if "Кремний" in sel_anode:
        st.warning("⚠️ **КРИТИЧЕСКИЙ VOXEL STRAIN:** Вы выбрали Кремний. Емкость колоссальная, но при загрузке Лития решетка разбухает на 300%. Voxel-сетка трескается, вызывая лавинообразное появление битых секторов. Срок службы критически низок.")
    if "Чистый Металл" in sel_anode:
        st.error("🔥 **КРИТИЧЕСКАЯ УТЕЧКА ПАМЯТИ (ДЕНДРИТЫ):** Чистый металл идеален по объему (0% расширения), но Garbage Collector Матрицы не успевает ровно укладывать ионы. Образуются `висячие указатели` (дендриты). Риск КЗ (kernel panic) максимален!")
    if "Титанат" in sel_anode:
        st.success("🛡️ **НУЛЕВОЙ STRAIN:** Титанат (LTO) вообще не меняет объем при записи (Zero-Strain). Батарея почти бессмертна, но тяжелая матрица забирает часть профита (Напряжение ниже).")
    if "Mg2+" in sel_carrier:
        st.warning("⚠️ **CPU LAG (Высокая поляризация):** Ион Магния несет заряд 2+ (Двойной профит!). Но он настолько плотный, что 'цепляется' за электроны решетки Катода, вызывая жесточайший лаг (drag). Он физически застревает в ROM-архиве, убивая циклы.")
