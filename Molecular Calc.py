import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================================
# SIMUREALITY: V15.0 BIG DATA GRID SCANNER (500K+ BONDS)
# Hexa-Quantum (6.20 kJ/mol) Validation on ALFABET Dataset
# =====================================================================

GAMMA_SYS = 1.0418
HEXA_QUANTUM = 6.20
KCAL_TO_KJ = 4.184

st.set_page_config(page_title="V15.0 Big Data Grid Scanner", layout="wide")
st.title("🌌 V15.0: Big Data Matrix Decompiler")
st.markdown("Парсинг 531,000+ связей из датасета `bde-db2.csv.gz`. Цель: поиск кластеризации энергий вокруг дискретных гекса-линков Матрицы (6.20 кДж/моль).")

@st.cache_data(show_spinner=False)
def load_and_process_data():
    try:
        # Чтение gzip архива напрямую
        df = pd.read_csv("bde-db2.csv.gz", compression='gzip')
        
        # Поиск колонки с энергией (bde или BDE)
        bde_col = 'bde' if 'bde' in df.columns else 'BDE' if 'BDE' in df.columns else None
        
        if not bde_col:
            return None, "Не найдена колонка 'bde' в файле."
            
        # 1. Берем сырые калории
        raw_kcal = df[bde_col].dropna().values
        
        # 2. Конвертация в кДж/моль
        energy_kj = raw_kcal * KCAL_TO_KJ
        
        # 3. Снятие Системного Налога Матрицы
        taxed_energy = energy_kj / GAMMA_SYS
        
        # 4. Расчет количества Гекса-Линков (N_ports)
        n_ports = taxed_energy / HEXA_QUANTUM
        
        return n_ports, len(n_ports)
    except Exception as e:
        return None, str(e)

with st.spinner("Загрузка и декомпиляция полумиллиона связей..."):
    n_ports_array, status = load_and_process_data()

if n_ports_array is None:
    st.error(f"❌ Ошибка парсинга: {status}. Проверь, лежит ли bde-db2.csv.gz в корне.")
else:
    st.success(f"✅ База загружена. Обработано связей: {status:,}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Тестируемый Квант", f"{HEXA_QUANTUM} кДж/моль")
    col2.metric("Конверсия (ккал -> кДж)", f"x {KCAL_TO_KJ}")
    col3.metric("Системный Налог", f"/ {GAMMA_SYS}")
    
    # --- ВИЗУАЛИЗАЦИЯ (ОПТИМИЗИРОВАННАЯ ДЛЯ ПЛАНШЕТОВ) ---
    st.markdown("### Спектр Топологического Резонанса")
    st.markdown("Если теория верна, на графике плотности должны появиться выраженные пики (резонансы) вблизи целых чисел по оси X.")
    
    # Используем агрегированную гистограмму, чтобы не рендерить 500k точек
    fig = px.histogram(
        x=n_ports_array, 
        nbins=500, 
        title="Распределение Гекса-Линков (Density Plot)",
        labels={'x': 'Количество Гекса-Линков (N)', 'y': 'Количество связей (Плотность)'},
        color_discrete_sequence=['#00E676']
    )
    
    # Добавляем вертикальные линии для идеальных целых чисел (от 10 до 150)
    for i in range(10, 150, 5):
        fig.add_vline(x=i, line_width=0.5, line_dash="dot", line_color="rgba(255,255,255,0.2)")
        
    fig.update_layout(template="plotly_dark", bargap=0)
    st.plotly_chart(fig, use_container_width=True)
    
    # Расчет глобальной погрешности
    variance = np.abs(n_ports_array - np.round(n_ports_array))
    mean_error_percent = np.mean(variance / np.round(n_ports_array)) * 100
    
    st.info(f"💡 **Аналитика:** Глобальная средняя погрешность отклонения от целых Гекса-Линков по всей базе: **{mean_error_percent:.2f}%**. Обрати внимание на 'гребенку' гистограммы. Широкие пики обусловлены геометрическим шумом (влиянием соседних узлов в сложных макромолекулах), но центры масс должны тяготеть к шагу сетки.")
