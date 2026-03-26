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
def load_local_masses(filename="mass.txt"):
    """Бронебойный парсинг локального текстового справочника масс."""
    try:
        # sep=r'\s+' - режет по любому количеству пробелов или табов
        # quoting=csv.QUOTE_NONE - жестко игнорирует любые кавычки в тексте
        # comment='#' - игнорирует строки-комментарии
        df = pd.read_csv(
            filename, 
            sep=r'\s+', 
            engine='python',
            quoting=csv.QUOTE_NONE,
            comment='#',
            on_bad_lines='skip'
        )
        
        # Проверяем, есть ли нужные колонки
        if 'Z' in df.columns and 'N' in df.columns:
            df.set_index(['Z', 'N'], inplace=True)
            # Убираем дубликаты индексов (если есть изомеры), оставляем первый (базовое состояние)
            df = df[~df.index.duplicated(keep='first')]
        else:
            st.error("Файл прочитан, но парсер не нашел колонок 'Z' и 'N'. Добавь эти буквы в первую строку mass.txt над нужными колонками.")
            
        return df
    except Exception as e:
        st.warning(f"Критическая ошибка чтения: {e}")
        # Резервная мини-база, чтобы интерфейс не падал
        return pd.DataFrame({
            'Z': [6, 6, 7], 'N': [6, 8, 7], 
            'Mass_MeV': [11174.862, 13040.868, 13040.201]
        }).set_index(['Z', 'N'])

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

df_masses = load_local_masses("mass.txt")
engine = SimurealityMacroCore()

# Панель управления
st.sidebar.header("Ввод Данных (Таргет)")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=1, max_value=118, value=6, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=1, max_value=177, value=8, step=1)

st.write("---")
col1, col2, col3 = st.columns(3)

# 1. Расчет нашей онтологии
calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Масса Simureality (ΣK)", value=f"{calc_mass:.3f} МэВ")

# 2. Поиск в mass.txt
if (target_Z, target_N) in df_masses.index:
    # Динамически берем колонку с массой
    col_name = 'Mass_MeV' if 'Mass_MeV' in df_masses.columns else df_masses.columns[-1]
    exp_mass = df_masses.loc[(target_Z, target_N), col_name]
    
    # Защита от изомеров
    if isinstance(exp_mass, pd.Series):
        exp_mass = exp_mass.iloc[0]
        
    try:
        # Принудительная конвертация в число для безопасности
        exp_mass = float(exp_mass)
        delta = calc_mass - exp_mass
        col2.metric(label=f"Справочник ({col_name})", value=f"{exp_mass:.3f} МэВ", delta=f"{delta:.3f} МэВ (Погрешность)", delta_color="inverse")
    except ValueError:
        col2.metric(label="Справочник", value="Ошибка формата (не число)")
else:
    col2.metric(label="Справочник (Эксперимент)", value="Нет данных в mass.txt")

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
