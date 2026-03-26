import streamlit as st
import pandas as pd
import numpy as np

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
def load_ame_masses(filename="mass.txt"):
    """Жесткий парсер фиксированной ширины для формата AME."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Пропускаем текстовую шапку и слишком короткие строки
                if len(line) < 65 or 'N-Z' in line or 'keV' in line:
                    continue
                    
                try:
                    # Вырезаем данные по жестким символьным индексам формата AME
                    n_str = line[5:10].strip()
                    z_str = line[10:15].strip()
                    a_str = line[15:19].strip()
                    be_str = line[54:65].strip() # Binding energy / A (keV)
                    
                    if not n_str or not z_str or not be_str:
                        continue
                        
                    # Очищаем от физических пометок неуверенности (#) и нулей (*)
                    be_str = be_str.replace('#', '').replace('*', '')
                    if not be_str: 
                        continue
                        
                    N = int(n_str)
                    Z = int(z_str)
                    A = int(a_str)
                    be_per_A_keV = float(be_str)
                    
                    # Переводим энергию связи в МэВ и считаем ЧЕСТНУЮ массу голого ядра
                    total_be_MeV = (be_per_A_keV * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError:
                    continue # Игнорируем битые строки
                    
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            # Убиваем дубликаты изомеров, оставляем только базовое состояние ядра
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception as e:
        st.error(f"Файл {filename} не найден. Положи его в папку со скриптом. Лог: {e}")
        return pd.DataFrame()

class SimurealityMacroCore:
    def compile_mass(self, Z, N):
        """Аналитический подсчет макро-архитектуры."""
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        # Хардкод макро-линков для легких ядер
        macro_links = 0
        if n_alphas == 3: macro_links = 3 
        elif n_alphas == 4: macro_links = 6 
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        
        binding_halo = 0
        jitter = 0
        
        # Эвристика гало для C-14
        if rem_N == 2 and rem_Z == 0:
            binding_halo = (5 * E_LINK) + E_PAIR
            jitter = 10 * JITTER_COST

        total_binding = binding_alphas + binding_macro + binding_halo - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("Simureality OS: Ядерный Диспетчер Задач")
st.markdown("Аналитический расчет ΣK на базе ГЦК-матрицы. Интеграция с базой AME.")

df_masses = load_ame_masses("mass.txt")
engine = SimurealityMacroCore()

# Панель управления
st.sidebar.header("Ввод Данных (Таргет)")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=1, max_value=118, value=6, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=1, max_value=177, value=8, step=1)

if df_masses.empty:
    st.sidebar.error("⚠️ База масс не загружена. Проверь mass.txt")
else:
    st.sidebar.success(f"✅ База загружена ({len(df_masses)} ядер)")

st.write("---")
col1, col2, col3 = st.columns(3)

# 1. Расчет нашей онтологии
calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Масса Simureality (ΣK)", value=f"{calc_mass:.3f} МэВ")

# 2. Поиск в AME
if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
    delta = calc_mass - exp_mass
    col2.metric(label="Справочник AME (Эксперимент)", value=f"{exp_mass:.3f} МэВ", delta=f"{delta:.3f} МэВ (Дельта)", delta_color="inverse")
else:
    col2.metric(label="Справочник AME (Эксперимент)", value="Нет данных в базе")

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
