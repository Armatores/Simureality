# ==============================================================================
# SIMUREALITY OS: FULLY AUTOMATED API EXTRACTOR (ГЛОБАЛЬНЫЙ АВТО-ПАРСЕР)
# Автоматически сканирует все 3000+ изотопов и выстраивает полный Словарь Интерфейсов
# ==============================================================================

import itertools
import numpy as np
import pandas as pd
from collections import defaultdict

MASS_P = 938.272
MASS_N = 939.565

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
        print(f"❌ Ошибка чтения файла {filename}: {e}")
        return pd.DataFrame()

# Базовые аппаратные кэши Матрицы для поиска путей сборки
CORE_BLOCKS = [
    (1, 1, 'H-2'), (2, 2, 'He-4'), (3, 4, 'Li-7'), 
    (6, 6, 'C-12'), (8, 8, 'O-16'), (10, 10, 'Ne-20'), 
    (12, 12, 'Mg-24'), (14, 14, 'Si-28'), (16, 16, 'S-32'), (20, 20, 'Ca-40')
]

def run_auto_extraction():
    print("================================================================================")
    print("      SIMUREALITY OS: АВТОМАТИЧЕСКИЙ СБОРЩИК КОНСТАНТ (AME2020)")
    print("================================================================================\n")
    
    df_masses = load_ame_masses("mass.txt")
    if df_masses.empty:
        print("❌ Файл 'mass.txt' не найден! Положи его в корневую папку со скриптом.")
        return

    # Собираем массы доступных базовых блоков из базы данных
    block_masses = {}
    for z, n, name in CORE_BLOCKS:
        if (z, n) in df_masses.index:
            block_masses[name] = df_masses.loc[(z, n), 'Mass_MeV']

    interface_database = defaultdict(list)

    print(f"[*] Запущено автоматическое сканирование изотопов (всего строк в базе: {len(df_masses)})...")
    
    scanned = 0
    # Автоматический перебор каждого ядра в таблице AME2020
    for (z, n), row in df_masses.iterrows():
        if z < 2 or n < 2: continue 
        target_mass = row['Mass_MeV']
        
        available_blocks = [(bx, by, bname) for bx, by, bname in CORE_BLOCKS if bname in block_masses]
        
        # Проверяем парные комбинации блоков, которые в сумме дают текущее ядро (Z, N)
        for b1, b2 in itertools.combinations_with_replacement(available_blocks, 2):
            if b1[0] + b2[0] == z and b1[1] + b2[1] == n:
                m1 = block_masses[b1[2]]
                m2 = block_masses[b2[2]]
                fusion_energy = (m1 + m2) - target_mass
                
                pair_key = tuple(sorted([b1[2], b2[2]]))
                interface_database[pair_key].append(fusion_energy)
                scanned += 1

    print(f"[*] Сканирование завершено. Успешно сопоставлено связей: {scanned}\n")
    print("================================================================================")
    print("      ИТОГОВЫЙ АВТОМАТИЧЕСКИЙ СЛОВАРЬ API МАТРИЦЫ")
    print("================================================================================")
    print(f"{'ТИП ИНТЕРФЕЙСА (ПАРА БЛОКОВ)':<22} | {'СРЕДНЯЯ ЦЕНА (МэВ)':<18} | {'КОМБИНАЦИЙ'}")
    print("-" * 60)

    final_api_dictionary = {}
    for pair, energies in interface_database.items():
        if len(energies) > 0:
            avg_energy = np.median(energies) # Медиана исключает аномальные выбросы
            pair_str = f"('{pair[0]}', '{pair[1]}')"
            print(f"{pair_str:<22} | {avg_energy:>14.3f} МэВ   | {len(energies)}")
            final_api_dictionary[pair] = round(float(avg_energy), 3)

    print("-" * 60)
    print("\n[+] Готовый программный словарь для вставки в наш Ab Initio Компилятор:")
    print("API_FUSION = {")
    for k, v in final_api_dictionary.items():
        print(f"    ('{k[0]}', '{k[1]}'): {v},")
    print("}")

if __name__ == "__main__":
    run_auto_extraction()
