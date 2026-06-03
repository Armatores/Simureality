import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==============================================================================
# SIMUREALITY: THE UNIFIED ENGINE (V11 MASSES + CHRONOS GC)
# ==============================================================================

st.set_page_config(page_title="Simureality Unified Engine", layout="wide", page_icon="🌌")

st.title("🌌 Unified Grid Engine: Ab-Initio + Chronos")
st.markdown("Этот скрипт сшивает вашу новую идеальную геометрию (V11) с реальными данными периодов полураспада (NUBASE).")

# --- ИНТЕРФЕЙС ЗАГРУЗКИ (НИКАКИХ ОШИБОК ПУТЕЙ) ---
st.info("Пожалуйста, загрузите два файла из вашей локальной папки.")
colA, colB = st.columns(2)

with colA:
    masses_file = st.file_uploader("1. Загрузи новый дамп масс (Masses_5_export.csv)", type=["csv"])
with colB:
    chronos_file = st.file_uploader("2. Загрузи старый лог Хроноса (ради колонки Log10(T_1/2))", type=["csv"])

if masses_file is not None and chronos_file is not None:
    with st.spinner("Сшиваем метрики и компилируем Матрицу..."):
        # 1. Читаем файлы
        df_masses = pd.read_csv(masses_file)
        df_chronos = pd.read_csv(chronos_file)
        
        # 2. Ищем колонку нового долга (страховка от разных названий в дампе)
        debt_col = None
        for c in ['Grid Debt/Error (MeV)', 'Grid Debt', 'Error (MeV)']:
            if c in df_masses.columns:
                debt_col = c
                break
                
        if debt_col is None:
            st.error(f"❌ В файле масс не найдена колонка долга! Колонки: {list(df_masses.columns)}")
        else:
            # 3. ВЫТЯЖКА ДАННЫХ ИЗ СТАРОГО ФАЙЛА (Только база ЦЕРНа)
            base_cols = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)']
            existing_base_cols = [c for c in base_cols if c in df_chronos.columns]
            df_nubase = df_chronos[existing_base_cols].copy()
            
            # 4. СЛИЯНИЕ ПО Z И A
            df_merged = pd.merge(df_nubase, df_masses[['Z', 'A', debt_col]], on=['Z', 'A'], how='inner')
            
            # 5. ПЕРЕСЧЕТ CHRONOS (Новая геометрия -> Новое Время)
            df_merged['ΔK Debt (MeV)'] = df_merged[debt_col].abs()
            
            df_merged['3D_Jitter'] = (df_merged['ΔK Debt (MeV)'] / 110.0).clip(0, 0.4999)
            df_merged['Desync_Angle_Deg'] = df_merged['3D_Jitter'] * 360.0
            df_merged['Unpaired'] = ((df_merged['Z'] % 2 != 0) | ((df_merged['A'] - df_merged['Z']) % 2 != 0)).astype(int)
            
            T_base, Z_imp, E_pow, P_lock = 2.76, 0.04, -0.87, -0.13
            df_merged['Predicted_LogT'] = T_base + (Z_imp * df_merged['Z']) + (E_pow * np.sqrt(df_merged['ΔK Debt (MeV)'])) + (P_lock * df_merged['Unpaired'])
            
            df_merged['Error_Delta'] = abs(df_merged['Predicted_LogT'] - df_merged['Log10(T_1/2)'])
            df_merged = df_merged.sort_values('Desync_Angle_Deg')
            
            # --- ВЫВОД РЕЗУЛЬТАТОВ БЕНЧМАРКА ---
            df_unstable = df_merged[(df_merged['Status'] == 'Unstable') & (df_merged['Log10(T_1/2)'].notna())]
            mae_global = df_unstable['Error_Delta'].mean()
            accuracy_percent = max(0, 100 - (mae_global / 50.0 * 100))
            
            st.success("✅ Слияние успешно завершено!")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Сшито ядер (Nodes Compiled)", f"{len(df_merged)}")
            c2.metric("Новая средняя ошибка (MAE)", f"{mae_global:.3f} порядков")
            c3.metric("Точность Сборщика Мусора", f"{accuracy_percent:.2f}%")
            
            # --- ГРАФИК ---
            st.subheader("Global Phase Shift")
            fig = px.scatter(
                df_unstable, x="Desync_Angle_Deg", y="Log10(T_1/2)", color="Z", 
                hover_name="Isotope", hover_data=["ΔK Debt (MeV)", "Error_Delta"],
                color_continuous_scale="Turbo", template="plotly_dark",
                title="Global 3D-Time Degradation Map"
            )
            fig.add_vline(x=180, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
            
            # --- СКАЧИВАНИЕ ---
            st.divider()
            st.markdown("### 💾 Экспорт Мастер-Файла")
            cols_to_export = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)', 'ΔK Debt (MeV)', 'Desync_Angle_Deg', 'Unpaired', 'Predicted_LogT', 'Error_Delta']
            csv_data = df_merged[cols_to_export].to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Скачать готовый Chronos_V11_benchmark.csv",
                data=csv_data,
                file_name="Chronos_V11_benchmark.csv",
                mime="text/csv"
            )
            
            st.dataframe(df_merged[cols_to_export].head(15), use_container_width=True)
