import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# SIMUREALITY: CHRONOS V10 DATA PIPELINE COMPILER (AB-INITIO CORE INTEGRATION)
# ==============================================================================

st.set_page_config(page_title="Chronos V10 Pipeline Compiler", layout="wide", page_icon="🧬")

st.title("🧬 Chronos V10: Pipeline Compiler & Data Fusion Engine")
st.markdown(r"**Discrete Lattice Infrastructure:** Утилита для сквозного бесшовного слияния Движка Геометрии (V11) и Движка Времени.")
st.info("🎯 **Принцип Оптимизации ($\Sigma K \to \min$):** Инструмент исключает ручной парсинг. Загрузите старый лог и новый дамп масс для пересчета матрицы.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Legacy Timeline Log")
    old_file = st.file_uploader("Загрузите старый файл Chronos (например, simureality_chronos_v8_benchmark.csv или экспорт из Streamlit)", type=["csv"])

with col2:
    st.subheader("2. New Ab-Initio Mass Dump")
    new_file = st.file_uploader("Загрузите свежий дамп масс от Движка Геометрии V11 (Masses_5_export.csv)", type=["csv"])

if old_file is not None and new_file is not None:
    st.divider()
    st.success("⚙️ Оба потока данных успешно инициализированы в оперативной памяти. Начинаю компиляцию матрицы...")
    
    try:
        # 1. Загрузка данных
        df_old = pd.read_csv(old_file)
        df_new = pd.read_csv(new_file)
        
        # Оставляем из старого файла только фундаментальные экспериментальные метрики NUBASE
        base_cols = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)']
        existing_base_cols = [c for c in base_cols if c in df_old.columns]
        df_old_clean = df_old[existing_base_cols].copy()
        
        # Находим нужную колонку долга в новом дампе масс
        debt_col = None
        for c in ['Grid Debt/Error (MeV)', 'Grid Debt', 'Error (MeV)']:
            if c in df_new.columns:
                debt_col = c
                break
        
        if debt_col is None:
            st.error(f"❌ Критическая ошибка структуры: В файле масс не найдена колонка топологического долга. Доступные колонки: {list(df_new.columns)}")
        else:
            # 2. Операция Слияния (Handshake) узлов по координатам Z и A
            df_merged = pd.merge(df_old_clean, df_new[['Z', 'A', debt_col]], on=['Z', 'A'], how='inner')
            
            # 3. Конвертация ошибки в абсолютный Топологический Долг
            df_merged['ΔK Debt (MeV)'] = df_merged[debt_col].abs()
            df_merged = df_merged.drop(columns=[debt_col])
            
            # 4. Аппаратный пересчет Движка Времени (Chronos V10 Core)
            df_merged['3D_Jitter'] = (df_merged['ΔK Debt (MeV)'] / 110.0).clip(0, 0.4999)
            df_merged['Desync_Angle_Deg'] = df_merged['3D_Jitter'] * 360.0
            
            # Определение неспаренных портов (Hardware Lock)
            df_merged['Unpaired'] = ((df_merged['Z'] % 2 != 0) | ((df_merged['A'] - df_merged['Z']) % 2 != 0)).astype(int)
            
            # Вычисление детерминированного таймаута Сборщика Мусора (GC Equation)
            T_base, Z_imp, E_pow, P_lock = 2.76, 0.04, -0.87, -0.13
            df_merged['Predicted_LogT'] = T_base + (Z_imp * df_merged['Z']) + (E_pow * np.sqrt(df_merged['ΔK Debt (MeV)'])) + (P_lock * df_merged['Unpaired'])
            
            # Расчет дельты ошибки
            df_merged['Error_Delta'] = abs(df_merged['Predicted_LogT'] - df_merged['Log10(T_1/2)'])
            
            # Сортировка по углу деградации
            df_merged = df_merged.sort_values('Desync_Angle_Deg')
            
            # --- ВЫВОД РЕЗУЛЬТАТОВ БЕНЧМАРКА ---
            df_unstable = df_merged[(df_merged['Status'] == 'Unstable') & (df_merged['Log10(T_1/2)'].notna())]
            mae_global = df_unstable['Error_Delta'].mean()
            accuracy_percent = max(0, 100 - (mae_global / 50.0 * 100))
            
            st.markdown("### 🎯 Live Benchmark: Результаты валидации новой матрицы")
            c1, c2, c3 = st.columns(3)
            c1.metric("Сшито ядер (Nodes Compiled)", f"{len(df_merged)}")
            c2.metric("Новая средняя ошибка (MAE)", f"{mae_global:.3f} orders")
            c3.metric("Точность Сборщика Мусора", f"{accuracy_percent:.2f}%", delta="Grid Physics V10")
            
            # Секция скачивания готового CSV
            st.divider()
            st.markdown("### 💾 Экспорт мастер-файла")
            
            # Переводим датафрейм в байты для безопасной передачи в кнопку
            csv_data = df_merged.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Скачать Мастер-Датасет (chronos_v10_master_debt.csv)",
                data=csv_data,
                file_name="chronos_v10_master_debt.csv",
                mime="text/csv",
                help="Нажмите для выгрузки полностью согласованной таблицы с новыми долгами масс V11 для Питера."
            )
            
            # Предпросмотр таблицы
            st.write("🔍 **Предпросмотр скомпилированных логов памяти (Топ-20 стабильных/оптимальных конфигураций):**")
            st.dataframe(df_merged.head(20), use_container_width=True)
            
    except Exception as e:
        st.error(f"💥 Системный сбой при парсинге структур: {str(e)}")
        st.info("Проверьте, что в загружаемых CSV файлах разделителем является запятая и присутствуют базовые колонки Z и A.")
