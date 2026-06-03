import streamlit as st
import pandas as pd
import numpy as np
import os

# ==============================================================================
# SIMUREALITY: CHRONOS V10 AUTO-COMPILER (ZERO-CLICK PIPELINE)
# ==============================================================================

st.set_page_config(page_title="Chronos V10 Auto-Compiler", layout="wide", page_icon="⚡")

st.title("⚡ Chronos V10: Автоматический Сборщик Матрицы")
st.markdown("**Grid Physics Framework:** Прямая интеграция Движка Геометрии (V11) и Движка Времени.")

# Автоматический поиск файлов в корневой директории
old_files_to_try = ["simureality_chronos_v8_benchmark.csv", "2026-05-30T23-26_export.csv"]
new_files_to_try = ["Masses_5_export.csv"]

def find_file(file_list):
    for f in file_list:
        if os.path.exists(f):
            return f
    return None

old_file_path = find_file(old_files_to_try)
new_file_path = find_file(new_files_to_try)

if not old_file_path or not new_file_path:
    st.error("❌ **Ошибка:** Не найдены базовые файлы в корне проекта!")
    st.info(f"Скрипт ищет старый лог ({old_files_to_try}) и новый дамп масс ({new_files_to_try}). Убедись, что они лежат в той же папке, что и этот скрипт.")
else:
    st.success(f"✅ Файлы найдены: `{old_file_path}` и `{new_file_path}`. Выполняю автоматическое слияние...")
    
    # 1. Загрузка данных
    df_old = pd.read_csv(old_file_path)
    df_new = pd.read_csv(new_file_path)
    
    # Очистка старого файла (оставляем только базу NUBASE)
    base_cols = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)']
    existing_base_cols = [c for c in base_cols if c in df_old.columns]
    df_old_clean = df_old[existing_base_cols].copy()
    
    # Поиск колонки с новым топологическим долгом
    debt_col = None
    for c in ['Grid Debt/Error (MeV)', 'Grid Debt', 'Error (MeV)']:
        if c in df_new.columns:
            debt_col = c
            break
            
    if debt_col is None:
        st.error(f"❌ Критическая ошибка: В файле {new_file_path} не найдена колонка долга. Есть только: {list(df_new.columns)}")
    else:
        # 2. Операция Слияния (Merge) по Z и A
        df_merged = pd.merge(df_old_clean, df_new[['Z', 'A', debt_col]], on=['Z', 'A'], how='inner')
        
        # 3. Конвертация ошибки в абсолютный Топологический Долг
        df_merged['ΔK Debt (MeV)'] = df_merged[debt_col].abs()
        df_merged = df_merged.drop(columns=[debt_col])
        
        # 4. Аппаратный пересчет Движка Времени
        df_merged['3D_Jitter'] = (df_merged['ΔK Debt (MeV)'] / 110.0).clip(0, 0.4999)
        df_merged['Desync_Angle_Deg'] = df_merged['3D_Jitter'] * 360.0
        
        # Hardware Lock (нечетные нуклоны)
        df_merged['Unpaired'] = ((df_merged['Z'] % 2 != 0) | ((df_merged['A'] - df_merged['Z']) % 2 != 0)).astype(int)
        
        # Уравнение Сборщика Мусора
        T_base, Z_imp, E_pow, P_lock = 2.76, 0.04, -0.87, -0.13
        df_merged['Predicted_LogT'] = T_base + (Z_imp * df_merged['Z']) + (E_pow * np.sqrt(df_merged['ΔK Debt (MeV)'])) + (P_lock * df_merged['Unpaired'])
        
        # Расчет дельты ошибки
        df_merged['Error_Delta'] = abs(df_merged['Predicted_LogT'] - df_merged['Log10(T_1/2)'])
        df_merged = df_merged.sort_values('Desync_Angle_Deg')
        
        # --- ВЫВОД РЕЗУЛЬТАТОВ ---
        df_unstable = df_merged[(df_merged['Status'] == 'Unstable') & (df_merged['Log10(T_1/2)'].notna())]
        mae_global = df_unstable['Error_Delta'].mean()
        accuracy_percent = max(0, 100 - (mae_global / 50.0 * 100))
        
        st.markdown("### 🎯 Результаты компиляции новой Матрицы (V10)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Сшито ядер (Nodes Compiled)", f"{len(df_merged)}")
        c2.metric("Новая ошибка распада (MAE)", f"{mae_global:.3f} orders")
        c3.metric("Точность Сборщика Мусора", f"{accuracy_percent:.2f}%", delta="Ab-Initio Core")
        
        st.divider()
        st.markdown("### 💾 Экспорт обновленного датасета")
        st.info("Это финальный, полностью согласованный датасет. Его нужно отдать Питеру и использовать в основном визуализаторе.")
        
        # Кнопка скачивания
        csv_data = df_merged.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать chronos_v10_master_debt.csv",
            data=csv_data,
            file_name="chronos_v10_master_debt.csv",
            mime="text/csv"
        )
        
        st.write("🔍 **Предпросмотр данных (Верхние строки):**")
        st.dataframe(df_merged.head(15), use_container_width=True)
