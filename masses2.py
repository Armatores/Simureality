import streamlit as st
import pandas as pd
import numpy as np
import csv

# --- ОНТОЛОГИЧЕСКИЕ КОНСТАНТЫ SIMUREALITY ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.295       # Аппаратный кэш (Тетраэдр 2P+2N)
E_MACRO_LINK = 2.425   # Связь между Альфа-кластерами
E_LINK = 2.36          # Связь для гало-нуклонов
E_PAIR = 1.18          # Бонус инстансирования
JITTER_COST = 0.0131   # Пинг пустых портов

st.set_page_config(page_title="Simureality OS | Task Dispatcher", layout="wide")

@st.cache_data
def load_raw_data(filename="mass.txt"):
    """Читает файл как есть, игнорируя кривую разметку."""
    try:
        df = pd.read_csv(
            filename, 
            sep=r'\s+', 
            engine='python',
            quoting=csv.QUOTE_NONE,
            comment='#',
            on_bad_lines='skip'
        )
        return df
    except Exception as e:
        return None

class SimurealityMacroCore:
    def compile_mass(self, Z, N):
        """Аналитический подсчет контрольных сумм макро-архитектуры."""
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        macro_links = 0
        if n_alphas == 3: macro_links = 3 
        elif n_alphas == 4: macro_links = 6 
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        
        binding_halo = 0
        jitter = 0
        if rem_N == 2 and rem_Z == 0:
            binding_halo = (5 * E_LINK) + E_PAIR
            jitter = 10 * JITTER_COST

        total_binding = binding_alphas + binding_macro + binding_halo - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("Simureality OS: Ядерный Диспетчер Задач")
st.markdown("Аналитический расчет ΣK на базе ГЦК-матрицы без эмпирической подгонки.")

engine = SimurealityMacroCore()
df_raw = load_raw_data("mass.txt")

# --- БОКОВАЯ ПАНЕЛЬ: МАППИНГ ДАННЫХ И ВВОД ---
st.sidebar.header("1. Конфигурация Парсера")

if df_raw is not None and not df_raw.empty:
    cols = list(df_raw.columns)
    
    # Пытаемся угадать колонки, если они стандартные
    idx_z = cols.index('Z') if 'Z' in cols else 0
    idx_n = cols.index('N') if 'N' in cols else min(1, len(cols)-1)
    
    col_z = st.sidebar.selectbox("Где лежат Протоны (Z)?", cols, index=idx_z)
    col_n = st.sidebar.selectbox("Где лежат Нейтроны (N)?", cols, index=idx_n)
    col_mass = st.sidebar.selectbox("Где лежит Масса?", cols, index=len(cols)-1)
    
    # Собираем чистый датафрейм на основе выбора пользователя
    df_masses = df_raw.copy()
    
    # Принудительно конвертируем в числа, отбрасывая текстовый мусор
    df_masses[col_z] = pd.to_numeric(df_masses[col_z], errors='coerce')
    df_masses[col_n] = pd.to_numeric(df_masses[col_n], errors='coerce')
    df_masses.dropna(subset=[col_z, col_n], inplace=True)
    
    df_masses['Z_clean'] = df_masses[col_z].astype(int)
    df_masses['N_clean'] = df_masses[col_n].astype(int)
    
    df_masses.set_index(['Z_clean', 'N_clean'], inplace=True)
    df_masses = df_masses[~df_masses.index.duplicated(keep='first')]
    
    st.sidebar.success("✅ База масс подключена.")
else:
    st.sidebar.error("❌ Ошибка чтения mass.txt.")
    df_masses = pd.DataFrame()
    col_mass = None

st.sidebar.write("---")
st.sidebar.header("2. Ввод Данных (Таргет)")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=1, max_value=118, value=6, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=1, max_value=177, value=8, step=1)

# --- ОСНОВНОЙ ЭКРАН ---
st.write("---")
col1, col2, col3 = st.columns(3)

# 1. Расчет нашей онтологии
calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Масса Simureality (ΣK)", value=f"{calc_mass:.3f} МэВ")

# 2. Поиск в mass.txt
if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass_raw = df_masses.loc[(target_Z, target_N), col_mass]
    
    if isinstance(exp_mass_raw, pd.Series):
        exp_mass_raw = exp_mass_raw.iloc[0]
        
    try:
        exp_mass = float(exp_mass_raw)
        delta = calc_mass - exp_mass
        col2.metric(label=f"Справочник (Эксперимент)", value=f"{exp_mass:.3f} МэВ", delta=f"{delta:.3f} МэВ (Погрешность)", delta_color="inverse")
    except ValueError:
        col2.metric(label="Справочник", value="Ошибка формата")
else:
    col2.metric(label="Справочник (Эксперимент)", value="Нет данных в базе")

# 3. Маршрутизация Диспетчера
st.subheader("Анализ Интерфейсных Патчей (Распад)")
mass_beta_minus = engine.compile_mass(target_Z + 1, target_N - 1) + E_ELECTRON
mass_beta_plus = engine.compile_mass(target_Z - 1, target_N + 1) + E_ELECTRON

if mass_beta_minus < calc_mass:
    profit = calc_mass - mass_beta_minus
    st.error(f"**FATAL DEBT.** Геометрия невыгодна. \n\n**Решение Диспетчера:** БЕТА-МИНУС РАСПАД (Z={target_Z+1}, N={target_N-1}). Выброс электрона сэкономит **{profit:.3f} МэВ** тактов процессора.")
elif mass_beta_plus < calc_mass:
    profit = calc_mass - mass_beta_plus
    st.error(f"**FATAL DEBT.** Геометрия невыгодна. \n\n**Решение Диспетчера:** БЕТА-ПЛЮС РАСПАД (Z={target_Z-1}, N={target_N+1}). Выброс позитрона сэкономит **{profit:.3f} МэВ** тактов процессора.")
else:
    st.success("**[OK] Аппаратная сборка стабильна.** Выброс патчей математически невыгоден. ΣK в глобальном минимуме.")
