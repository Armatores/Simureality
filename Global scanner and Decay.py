import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==============================================================================
# SIMUREALITY: 3D-TIME DESYNCHRONIZATION ENGINE (GLOBAL SCANNER)
# The Theorem of 180 Degrees & Garbage Collector Timeout
# ==============================================================================

LAMBDA_P = 1.3214  # L1-Cache Step (Proton Compton Wavelength in fm)

st.set_page_config(page_title="3D-Time GC Scanner", layout="wide", page_icon="⏱️")

# --- 1. ПАРСИНГ БАЗ ДАННЫХ (CR2013 + FRDM95 + NUBASE2020) ---
@st.cache_data
def load_global_matrix():
    # Радиусы (CR2013)
    if not os.path.exists("charge_radii.csv"): return pd.DataFrame()
    df_radii = pd.read_csv("charge_radii.csv").rename(columns={'z': 'Z', 'a': 'A', 'radius_val': 'Rc_fm', 'symbol': 'Isotope_Sym'}).dropna(subset=['Rc_fm'])
    df_radii['Isotope'] = df_radii['Isotope_Sym'] + "-" + df_radii['A'].astype(str)
    
    # Деформации (FRDM-95)
    frdm_data = []
    if os.path.exists("mass-frdm95.txt"):
        with open("mass-frdm95.txt", 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or len(line) < 63: continue
                try:
                    Z, A = int(line[0:4].strip()), int(line[4:8].strip())
                    b2 = line[55:63].strip()
                    if b2: frdm_data.append({'Z': Z, 'A': A, 'Beta2': float(b2)})
                except ValueError: continue
    df_frdm = pd.DataFrame(frdm_data).drop_duplicates(subset=['Z', 'A'])
    df_geo = pd.merge(df_radii, df_frdm, on=['Z', 'A'], how='inner') if not df_frdm.empty else df_radii.copy()
    if 'Beta2' not in df_geo.columns: df_geo['Beta2'] = 0.0

    # Время жизни (NUBASE2020)
    nubase_data = []
    if os.path.exists("Nubase2020.txt"):
        with open("Nubase2020.txt", 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or len(line) < 80: continue
                try:
                    A_str, Z_str = line[0:3].strip(), line[4:7].strip()
                    if not A_str.isdigit() or not Z_str.isdigit() or line[7:8].strip() != '0': continue
                    A, Z = int(A_str), int(Z_str)
                    hl_str = line[69:78].strip().replace('#', '').replace('>', '').replace('<', '').replace('~', '')
                    unit = line[78:80].strip().lower()
                    
                    if 'stbl' in hl_str.lower() or 'stable' in hl_str.lower():
                        sec = np.inf
                    elif 'p-unst' in hl_str.lower():
                        sec = 1e-21
                    else:
                        mults = {'s':1, 'm':60, 'h':3600, 'd':86400, 'y':31536000, 'ms':1e-3, 'us':1e-6, 'ns':1e-9, 'ps':1e-12, 'fs':1e-15, 'as':1e-18, 'zs':1e-21, 'ys':1e-24}
                        sec = float(hl_str) * mults.get(unit, 1)
                    nubase_data.append({'Z': Z, 'A': A, 'Half_Life_Sec': sec, 'HL_Raw': f"{hl_str} {unit}"})
                except Exception: continue
    df_nu = pd.DataFrame(nubase_data).drop_duplicates(subset=['Z', 'A'])
    df_final = pd.merge(df_geo, df_nu, on=['Z', 'A'], how='left') if not df_nu.empty else df_geo.copy()
    
    return df_final[df_final['A'] > 20].copy()

# --- 2. ДВИЖОК 3D-ВРЕМЕНИ (ФАЗОВЫЙ СДВИГ) ---
def compute_3d_time_physics(df):
    if df.empty: return df
    
    # Геометрия
    df['Length_fm'] = df['Rc_fm'] * (1 + 0.63078 * df['Beta2']) * 2.0
    df['Grid_Layers'] = df['Length_fm'] / LAMBDA_P
    
    # Вычисление Джиттера
    df['Jitter'] = abs(df['Grid_Layers'] - df['Grid_Layers'].round())
    df['Jitter_Safe'] = np.clip(df['Jitter'], 0.0, 0.499)
    
    # ФИЗИКА 3D-ВРЕМЕНИ:
    df['Phase_Margin'] = 1.0 - 2.0 * df['Jitter_Safe']  # Остаточный ресурс до Kernel Panic
    df['Desync_Angle_Deg'] = df['Jitter_Safe'] * 360.0  # Угол расхождения векторов (t_x, t_y, t_z)
    
    # Логарифм реального времени для графиков
    with np.errstate(divide='ignore'):
        df['Real_Log10_T'] = np.where(df['Half_Life_Sec'] != np.inf, np.log10(df['Half_Life_Sec'].astype(float)), np.nan)
        
    df['Stability'] = np.where(df['Half_Life_Sec'] == np.inf, "Stable (Jitter 0°)", "Unstable (Desync)")
    return df

# --- 3. ИНТЕРФЕЙС STREAMLIT ---
st.title("⏱️ 3D-Time Desynchronization Engine")
st.markdown("""
**Механика Сборщика Мусора (GC):** Время — это не скаляр, а трехмерный вектор обновления координат $(\\tau_x, \\tau_y, \\tau_z)$. 
Когда ядро деформируется (Jitter), эти векторы расходятся. При достижении **Угла рассинхрона в 180°** ($Jitter = 0.5$) возникает *Kernel Panic* (полная противофаза данных), и Матрица мгновенно удаляет ядро.
""")

with st.spinner("Компиляция фазовых сдвигов Матрицы..."):
    raw_df = load_global_matrix()
    df = compute_3d_time_physics(raw_df)

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["🔬 Микро-Анализ цепей (Чистый тренд)", "🌌 Макро-Облако Рассинхрона", "🗄️ База Данных Времени"])
    
    with tab1:
        st.subheader("Фазовый распад конкретного элемента")
        st.markdown("Выберите элемент, чтобы увидеть, как рост угла рассинхрона 3D-времени экспоненциально убивает время его жизни.")
        
        elements = sorted(df['Z'].unique())
        selected_z = st.selectbox("Выберите заряд ядра (Z):", elements, index=elements.index(92) if 92 in elements else 0)
        
        chain_df = df[(df['Z'] == selected_z) & (df['Half_Life_Sec'] != np.inf)].dropna(subset=['Real_Log10_T'])
        
        if len(chain_df) > 2:
            fig1 = px.scatter(chain_df, x="Desync_Angle_Deg", y="Real_Log10_T", text="Isotope",
                              title=f"Зависимость Времени Жизни от Угла Рассинхронизации (Z={selected_z})",
                              labels={"Desync_Angle_Deg": "Угол Рассинхрона 3D-Времени (Градусы)", "Real_Log10_T": "Log10(T) в секундах"},
                              trendline="ols", trendline_color_override="red", template="plotly_dark")
            fig1.update_traces(textposition='top center', marker=dict(size=12, color='#00E676'))
            fig1.add_vline(x=180, line_dash="dash", line_color="red", annotation_text="Kernel Panic (180°)")
            st.plotly_chart(fig1, use_container_width=True)
            
            st.info("💡 **Обратите внимание:** По мере того как угол рассинхрона приближается к 180°, красная линия тренда (время жизни) стремительно падает вниз. Это чистое геометрическое доказательство работы таймаута.")
        else:
            st.warning("Недостаточно нестабильных изотопов для построения тренда в этой цепи.")

    with tab2:
        st.subheader("Глобальный сдвиг фаз (Все нестабильные ядра)")
        unstable_df = df[df['Half_Life_Sec'] != np.inf].dropna(subset=['Real_Log10_T'])
        
        fig2 = px.scatter(unstable_df, x="Desync_Angle_Deg", y="Real_Log10_T", color="Z", hover_name="Isotope",
                          color_continuous_scale="Plasma", template="plotly_dark",
                          labels={"Desync_Angle_Deg": "Угол Рассинхрона 3D-Времени (°)", "Real_Log10_T": "Log10(T_1/2)"})
        fig2.add_vline(x=180, line_dash="dash", line_color="red", annotation_text="Аппаратный предел (180°)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### Системный лог 3D-Времени")
        display_cols = ['Isotope', 'Z', 'A', 'Jitter', 'Phase_Margin', 'Desync_Angle_Deg', 'HL_Raw']
        st.dataframe(df[display_cols].sort_values('Desync_Angle_Deg', ascending=False).style.background_gradient(subset=['Desync_Angle_Deg'], cmap='Reds'), use_container_width=True)
else:
    st.error("Базы данных не найдены в корневой папке. Пожалуйста, убедитесь, что charge_radii.csv и Nubase2020.txt на месте.")
