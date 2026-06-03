import streamlit as st
import pandas as pd
import numpy as np
import os

# ==============================================================================
# SIMUREALITY: CHRONOS V10 BULLETPROOF AUTO-COMPILER
# ==============================================================================

st.set_page_config(page_title="Chronos V10 Auto-Compiler", layout="wide", page_icon="⚡")

st.title("⚡ Chronos V10: Матричный Сборщик (V11 Core)")
st.markdown("**Grid Physics Framework:** Интеграция эталонных расчетов масс (Ab-Initio) и логов распада.")

# --- УМНЫЙ ПОИСК ФАЙЛОВ ---
old_files_targets = ["simureality_chronos_v8_benchmark.csv", "2026-05-30T23-26_export.csv"]
new_files_targets = ["Masses_5_export.csv"]

def get_file_path(filenames):
    # 1. Пробуем найти в текущей директории
    for f in filenames:
        if os.path.exists(f):
            return f
    # 2. Пробуем найти через абсолютный путь к папке скрипта (Лечит баг Streamlit Cloud)
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for f in filenames:
            full_path = os.path.join(base_dir, f)
            if os.path.exists(full_path):
                return full_path
    except:
        pass
    return None

old_file = get_file_path(old_files_targets)
new_file = get_file_path(new_files_targets)

# --- ИЗЯЩНАЯ ДЕГРАДАЦИЯ (FALLBACK) ---
# Если автоматика не нашла файлы (баг путей), показываем ручной загрузчик, вместо того чтобы ломаться
if not old_file or not new_file:
    st.warning("⚠️ **Автопоиск файлов на сервере не сработал** (конфликт рабочих директорий). Пожалуйста, выберите файлы вручную:")
    colA, colB = st.columns(2)
    with colA:
        old_file = st.file_uploader("1. Загрузите старый Chronos лог (с периодами полураспада)", type=["csv"])
    with colB:
        new_file = st.file_uploader("2. Загрузите свежий дамп масс (Masses_5_export.csv)", type=["csv"])

# --- ГЛАВНЫЙ АЛГОРИТМ (Срабатывает, если файлы найдены или загружены) ---
if old_file is not None and new_file is not None:
    st.success("✅ Источники данных успешно подключены. Выполняю компиляцию Матрицы...")
    
    try:
        # Чтение датасетов
        df_old = pd.read_csv(old_file)
        df_new = pd.read_csv(new_file)
        
        # Очистка старого файла (оставляем только базу NUBASE)
        base_cols = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)']
        existing_base_cols = [c for c in base_cols if c in df_old.columns]
        df_old_clean = df_old[existing_base_cols].copy()
        
        # Ищем колонку с новым топологическим долгом
        debt_col = None
        for c in ['Grid Debt/Error (MeV)', 'Grid Debt', 'Error (MeV)']:
            if c in df_new.columns:
                debt_col = c
                break
                
        if debt_col is None:
            st.error(f"❌ В новом файле масс не найдена колонка долга. Доступные колонки: {list(df_new.columns)}")
        else:
            # СЛИЯНИЕ ПО Z И A
            df_merged = pd.merge(df_old_clean, df_new[['Z', 'A', debt_col]], on=['Z', 'A'], how='inner')
            
            # Конвертация в абсолютный долг
            df_merged['ΔK Debt (MeV)'] = df_merged[debt_col].abs()
            df_merged = df_merged.drop(columns=[debt_col])
            
            # --- ХАРДКОРНЫЙ РАСЧЕТ CHRONOS V10 ---
            df_merged['3D_Jitter'] = (df_merged['ΔK Debt (MeV)'] / 110.0).clip(0, 0.4999)
            df_merged['Desync_Angle_Deg'] = df_merged['3D_Jitter'] * 360.0
            
            df_merged['Unpaired'] = ((df_merged['Z'] % 2 != 0) | ((df_merged['A'] - df_merged['Z']) % 2 != 0)).astype(int)
            
            T_base, Z_imp, E_pow, P_lock = 2.76, 0.04, -0.87, -0.13
            df_merged['Predicted_LogT'] = T_base + (Z_imp * df_merged['Z']) + (E_pow * np.sqrt(df_merged['ΔK Debt (MeV)'])) + (P_lock * df_merged['Unpaired'])
            
            df_merged['Error_Delta'] = abs(df_merged['Predicted_LogT'] - df_merged['Log10(T_1/2)'])
            df_merged = df_merged.sort_values('Desync_Angle_Deg')
            
            # --- РЕЗУЛЬТАТЫ ---
            df_unstable = df_merged[(df_merged['Status'] == 'Unstable') & (df_merged['Log10(T_1/2)'].notna())]
            mae_global = df_unstable['Error_Delta'].mean()
            accuracy_percent = max(0, 100 - (mae_global / 50.0 * 100))
            
            st.markdown("### 🎯 Результаты: Chronos V10 (Ab-Initio Integration)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Сшито ядер (Nodes Compiled)", f"{len(df_merged)}")
            c2.metric("Новая ошибка распада (MAE)", f"{mae_global:.3f} orders")
            c3.metric("Точность Сборщика Мусора", f"{accuracy_percent:.2f}%", delta="Grid Physics V11")
            
            st.divider()
            st.markdown("### 💾 Экспорт обновленного датасета")
            st.info("Отлично! Это финальный датасет. Скачайте его и загрузите в ваш основной визуализатор.")
            
            csv_data = df_merged.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Скачать Master Dataset (chronos_v10_master_debt.csv)",
                data=csv_data,
                file_name="chronos_v10_master_debt.csv",
                mime="text/csv"
            )
            
            st.dataframe(df_merged.head(15), use_container_width=True)

    except Exception as e:
        st.error(f"💥 Ошибка при обработке файлов: {str(e)}")
