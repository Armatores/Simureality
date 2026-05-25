import streamlit as st
import numpy as np

# --- SIMUREALITY CONSTANTS ---
BASE_RYDBERG_THZ = 3289.84196  # Идеальный базовый такт вакуума (ТГц)
NODE_IMPEDANCE = 0.0005446     # Системная задержка на один узел (эквивалент m_e/m_p)

st.set_page_config(page_title="Simureality: Binary Core Parser", layout="wide")

# Бинарный словарь легких изотопов
# 1 = Протон (Активный I/O порт)
# 0 = Нейтрон (Пассивный буфер)
CORE_ALPHABET = {
    "Hydrogen-1 (Protium)": [1],
    "Hydrogen-2 (Deuterium)": [1, 0],
    "Hydrogen-3 (Tritium)": [1, 0, 0],
    "Helium-3": [1, 0, 1],
    "Helium-4": [1, 0, 1, 0],
    "Lithium-6": [1, 0, 1, 0, 1, 0],
    "Lithium-7": [1, 0, 1, 0, 1, 0, 0]
}

st.title("🔢 Бинарный Парсер Спектра (Unit-тесты)")
st.markdown("""
**От кода к свету:** Атомное ядро — это исполняемый бинарный массив в ГЦК-матрице. 
Единицы `1` генерируют сигнал, нули `0` работают как буферы, поглощающие аппаратный джиттер. 
Чем лучше буферизация, тем ближе частота сброса фотона к идеальному вакуумному такту.
""")

selected_isotope = st.selectbox("Выберите исполняемый массив (Изотоп):", list(CORE_ALPHABET.keys()))
binary_code = CORE_ALPHABET[selected_isotope]

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Анализ Исходного Кода")
    st.code(f"ARRAY = {binary_code}", language="python")
    
    active_ports = binary_code.count(1)
    buffers = binary_code.count(0)
    total_nodes = len(binary_code)
    
    st.write(f"🟢 **Активные порты (1):** {active_ports}")
    st.write(f"⚪ **Буферы (0):** {buffers}")
    st.write(f"🔗 **Длина массива (Total Nodes):** {total_nodes}")
    
    # Расчет плотности буферизации
    if active_ports > 0:
        buffer_ratio = buffers / active_ports
    else:
        buffer_ratio = 0
        
    st.metric("Коэффициент Буферизации", f"{buffer_ratio:.2f} буферов/порт")

with col2:
    st.header("Компиляция Спектрального Хэша")
    
    # Физика Grid: Смещение частоты из-за задержки узлов (Изотопический сдвиг)
    # Матрица тратит такты (NODE_IMPEDANCE) на обработку массива. 
    # Больше узлов = больше масса = меньше "джиттера" излучающего порта.
    
    # Базовый заряд ядра для серии Бальмера (в квадрате)
    charge_multiplier = active_ports ** 2
    
    # Вычисление "Импеданса Массива" (аналог приведенной массы)
    array_impedance_factor = 1 / (1 + (NODE_IMPEDANCE / total_nodes))
    
    # Симулируем переход 3 -> 2 (Линия альфа в серии Бальмера/Пикеринга)
    transition_multiplier = (1/(2**2)) - (1/(3**2))
    
    # Итоговая частота хэш-суммы (фотона)
    output_freq = BASE_RYDBERG_THZ * charge_multiplier * transition_multiplier * array_impedance_factor
    output_wave = 299792.458 / output_freq
    
    st.success("ПАКЕТ ДАННЫХ (ФОТОН) СКОМПИЛИРОВАН")
    st.metric("Частота сигнала", f"{output_freq:.5f} ТГц")
    st.metric("Длина волны", f"{output_wave:.5f} нм")
    
    st.markdown("""
    *Классическая физика называет изменение этой частоты «Изотопическим сдвигом». 
    В Grid Physics это просто изменение времени обработки прерывания в зависимости от длины бинарного массива.*
    """)

st.markdown("---")
st.subheader("💡 Логика реверс-инжиниринга")
st.write("""
Если мы переключимся с **Hydrogen-1 `[1]`** на **Hydrogen-2 `[1, 0]`**, длина массива увеличится. 
Аппаратный импеданс на узел падает (так как база тяжелее и стабильнее), и частота ответа Матрицы смещается ровно на ту величину, которую телескопы фиксируют в космосе. 
Когда мы наберем базу таких "спектральных отпечатков" для разных паттернов `1` и `0`, мы сможем написать алгоритм-дешифратор, который будет читать спектры звезд и выдавать нам чистый бинарный код их состава!
""")
