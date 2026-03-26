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
def load_ame_masses(filename="mass.txt"):
    """Жесткий парсер фиксированной ширины для формата AME."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line:
                    continue
                try:
                    n_str = line[5:10].strip()
                    z_str = line[10:15].strip()
                    a_str = line[15:19].strip()
                    be_str = line[54:65].strip().replace('#', '').replace('*', '')
                    
                    if not n_str or not z_str or not be_str: continue
                        
                    N = int(n_str)
                    Z = int(z_str)
                    A = int(a_str)
                    be_per_A_keV = float(be_str)
                    
                    total_be_MeV = (be_per_A_keV * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError:
                    continue
                    
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception as e:
        return pd.DataFrame()

class SimurealityMacroCore:
    def compile_mass(self, Z, N):
        """Аналитический подсчет макро-архитектуры (MVP)."""
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        # Заглушка: прописаны макро-линки только для очень легких ядер.
        # Для тяжелых (Z > 10) дельта будет расти до тех пор, пока мы не опишем 3D-геометрию их кластеров.
        macro_links = 0
        if n_alphas == 3: macro_links = 3 
        elif n_alphas == 4: macro_links = 6 
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        
        binding_halo = 0
        jitter = 0
        
        if rem_N == 2 and rem_Z == 0: # C-14 и подобные
            binding_halo = (5 * E_LINK) + E_PAIR
            jitter = 10 * JITTER_COST

        total_binding = binding_alphas + binding_macro + binding_halo - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

@st.cache_data
def generate_global_matrix(_engine, df_ame):
    """Пакетный анализ всех изотопов."""
    results = []
    for (Z, N), row in df_ame.iterrows():
        exp_mass = row['Mass_MeV']
        calc_mass = _engine.compile_mass(Z, N)
        delta = calc_mass - exp_mass
        
        # Оценка распада
        m_b_minus = _engine.compile_mass(Z + 1, N - 1) + E_ELECTRON
        m_b_plus = _engine.compile_mass(Z - 1, N + 1) + E_ELECTRON
        
        if m_b_minus < calc_mass:
            status = "BETA MINUS"
        elif m_b_plus < calc_mass:
            status = "BETA PLUS"
        else:
            status = "STABLE"
            
        results.append({
            "Z": Z, "N": N, "A": Z+N,
            "AME (МэВ)": round(exp_mass, 3),
            "Simureality (МэВ)": round(calc_mass, 3),
            "Дельта (МэВ)": round(delta, 3),
            "Решение Диспетчера": status
        })
    
    return pd.DataFrame(results).sort_values(by=["Z", "N"])

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("Simureality OS: Ядерный Диспетчер Задач")
st.markdown("Аналитический расчет ΣK на базе ГЦК-матрицы. Интеграция с базой AME.")

df_masses = load_ame_masses("mass.txt")
engine = SimurealityMacroCore()

st.sidebar.header("Ввод Данных (Таргет)")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=1, max_value=118, value=6, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=1, max_value=177, value=8, step=1)

if df_masses.empty:
    st.sidebar.error("⚠️ База масс не загружена. Проверь mass.txt")
else:
    st.sidebar.success(f"✅ База загружена ({len(df_masses)} ядер)")

st.write("### Локальный анализ (Single Core)")
col1, col2, col3 = st.columns(3)

calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Масса Simureality (ΣK)", value=f"{calc_mass:.3f} МэВ")

if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
    delta = calc_mass - exp_mass
    col2.metric(label="Справочник AME", value=f"{exp_mass:.3f} МэВ", delta=f"{delta:.3f} МэВ (Дельта)", delta_color="inverse")
else:
    col2.metric(label="Справочник AME", value="Нет данных")

mass_beta_minus = engine.compile_mass(target_Z + 1, target_N - 1) + E_ELECTRON
mass_beta_plus = engine.compile_mass(target_Z - 1, target_N + 1) + E_ELECTRON

if mass_beta_minus < calc_mass:
    st.error(f"**FATAL DEBT.** БЕТА-МИНУС РАСПАД. Сброс электрона сэкономит **{(calc_mass - mass_beta_minus):.3f} МэВ**.")
elif mass_beta_plus < calc_mass:
    st.error(f"**FATAL DEBT.** БЕТА-ПЛЮС РАСПАД. Сброс позитрона сэкономит **{(calc_mass - mass_beta_plus):.3f} МэВ**.")
else:
    st.success("**[OK] Аппаратная сборка стабильна.** ΣK в глобальном минимуме.")

# --- ГЛОБАЛЬНАЯ МАТРИЦА ---
st.markdown("---")
st.write("### Глобальный лог компиляции (Матрица AME2020)")
if not df_masses.empty:
    with st.spinner('Синхронизация с базой... Формируем таблицу 3500+ ядер...'):
        global_df = generate_global_matrix(engine, df_masses)
        st.dataframe(global_df, use_container_width=True, height=600)
        
        # Даем возможность скачать результаты в CSV для статьи
        csv_data = global_df.to_csv(index=False).encode('utf-8')
        st.download_button("Скачать матрицу (CSV)", data=csv_data, file_name="simureality_global_log.csv", mime="text/csv")
