import streamlit as st
import pandas as pd
import numpy as np
import itertools
from collections import defaultdict

# --- CONFIG & UI SETUP ---
st.set_page_config(page_title="Heavy API Extractor", layout="wide")
st.title("⚙️ Grid Physics: Heavy API Matrix Extractor")
st.markdown("Автоматический парсер базы AME2020 для извлечения аппаратного прайс-листа интерфейсов Матрицы, включая **сверхтяжелые префабы (Ni-56, Sn-132, Pb-208)** и расчет **Geometry Overflow**.")

MASS_P = 938.272
MASS_N = 939.565

# --- 1. ROBUST AME2020 PARSER ---
@st.cache_data
def load_ame_masses(filename="mass.txt"):
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                try:
                    n_str, z_str, a_str = line[5:10].strip(), line[10:15].strip(), line[15:19].strip()
                    be_str = line[54:65].strip().replace('#', '').replace('*', '')
                    if not n_str or not z_str or not be_str: continue
                    N, Z, A = int(n_str), int(z_str), int(a_str)
                    total_be_MeV = (float(be_str) * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError: continue
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception as e:
        return pd.DataFrame(), str(e)

df_masses = load_ame_masses("mass.txt")

if isinstance(df_masses, tuple) or df_masses.empty:
    st.error("❌ Ошибка: файл `mass.txt` не найден в корневой директории! Положите его рядом с `app.py`.")
    st.stop()

st.success(f"✅ База AME2020 успешно загружена. Изотопов в памяти: **{len(df_masses)}**")

# --- 2. EXTENDED HARDWARE CACHE PREFABS ---
CORE_BLOCKS = [
    (1, 1, 'H-2'), (2, 2, 'He-4'), (3, 4, 'Li-7'), 
    (6, 6, 'C-12'), (8, 8, 'O-16'), (10, 10, 'Ne-20'), 
    (12, 12, 'Mg-24'), (14, 14, 'Si-28'), (16, 16, 'S-32'), (20, 20, 'Ca-40'),
    (28, 28, 'Ni-56'), (50, 82, 'Sn-132'), (82, 126, 'Pb-208') # Добавлены тяжелые модули
]

block_masses = {}
for z, n, name in CORE_BLOCKS:
    if (z, n) in df_masses.index:
        block_masses[name] = df_masses.loc[(z, n), 'Mass_MeV']

st.markdown("---")
st.subheader("🚀 Запуск глубокого сканирования интерфейсов")
st.markdown("Нажми кнопку ниже, чтобы вычислить цены стыковок, включая критические переполнения геометрии (Geometry Overflow) на тяжелых блоках.")

if st.button("Запустить Heavy Auto-Extractor", type="primary"):
    interface_database = defaultdict(list)
    available_blocks = [(bx, by, bname) for bx, by, bname in CORE_BLOCKS if bname in block_masses]
    
    items = list(df_masses.iterrows())
    total_items = len(items)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    scanned_links = 0
    
    # Run loop with progress bar so UI never freezes
    for idx, ((z, n), row) in enumerate(items):
        if z < 2 or n < 2: continue
        target_mass = row['Mass_MeV']
        
        for b1, b2 in itertools.combinations_with_replacement(available_blocks, 2):
            if b1[0] + b2[0] == z and b1[1] + b2[1] == n:
                m1 = block_masses[b1[2]]
                m2 = block_masses[b2[2]]
                fusion_energy = (m1 + m2) - target_mass
                
                pair_key = tuple(sorted([b1[2], b2[2]]))
                interface_database[pair_key].append(fusion_energy)
                scanned_links += 1
                
        if idx % 100 == 0:
            progress_bar.progress(min(idx / total_items, 1.0))
            status_text.text(f"Обработано строк: {idx} / {total_items} | Найдено связей: {scanned_links}")

    progress_bar.progress(1.0)
    status_text.text(f"✅ Сканирование завершено! Проанализировано связей: {scanned_links}")
    
    # Process results into a clean dataframe
    results_list = []
    final_api_dict = {}
    
    for pair, energies in interface_database.items():
        if len(energies) > 0:
            avg_energy = float(np.median(energies))
            spread = float(np.max(energies) - np.min(energies))
            pair_str = f"('{pair[0]}', '{pair[1]}')"
            
            # Помечаем красным флажком штрафные интерфейсы
            status = "✅ Норма"
            if avg_energy < 0:
                status = "🚨 GEOMETRY OVERFLOW"
                
            results_list.append({
                "Interface Pair": pair_str,
                "Median Price (MeV)": round(avg_energy, 3),
                "Spread (MeV)": round(spread, 3),
                "Occurrences": len(energies),
                "Status": status
            })
            final_api_dict[pair] = round(avg_energy, 3)
            
    # Сортируем так, чтобы сверху были выгодные интерфейсы, а снизу - жесткие штрафы
    df_results = pd.DataFrame(results_list).sort_values(by="Median Price (MeV)", ascending=False)
    
    st.markdown("### 📊 Итоговый Словарь API Матрицы (Интерфейсные Константы)")
    
    # Функция для подсветки строк с Overflow
    def highlight_overflow(row):
        if row['Status'] == "🚨 GEOMETRY OVERFLOW":
            return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
        return [''] * len(row)

    st.dataframe(df_results.style.apply(highlight_overflow, axis=1), use_container_width=True)
    
    st.markdown("### 📋 Готовый код словаря для Ab Initio Компилятора:")
    code_snippet = "API_FUSION = {\n"
    # Сортируем словарь по убыванию цены, чтобы было красиво в коде
    sorted_dict = sorted(final_api_dict.items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_dict:
        code_snippet += f"    ('{k[0]}', '{k[1]}'): {v},\n"
    code_snippet += "}"
    
    st.code(code_snippet, language="python")
