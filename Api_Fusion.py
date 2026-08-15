# ==============================================================================
# SIMUREALITY OS: HEAVY API EXTRACTOR (ГЛОБАЛЬНЫЙ ПАРСЕР С ТЯЖЕЛЫМИ БЛОКАМИ)
# Автоматически извлекает цены интерфейсов вплоть до Свинца-208
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

# РАСШИРЕННАЯ БАЗА КЭШЕЙ (Добавлены Никель, Олово и Свинец)
CORE_BLOCKS = [
    (1, 1, 'H-2'), (2, 2, 'He-4'), (3, 4, 'Li-7'), 
    (6, 6, 'C-12'), (8, 8, 'O-16'), (10, 10, 'Ne-20'), 
    (12, 12, 'Mg-24'), (14, 14, 'Si-28'), (16, 16, 'S-32'), (20, 20, 'Ca-40'),
    (28, 28, 'Ni-56'), (50, 82, 'Sn-132'), (82, 126, 'Pb-208')
]

def run_auto_extraction():
    print("================================================================================")
    print("      SIMUREALITY OS: СБОРЩИК КОНСТАНТ HEAVY API (AME2020)")
    print("================================================================================\n")
    
    df_masses = load_ame_masses("mass.txt")
    if df_masses.empty:
        print("❌ Файл 'mass.txt' не найден! Положи его рядом со скриптом.")
        return

    block_masses = {}
    for z, n, name in CORE_BLOCKS:
        if (z, n) in df_masses.index:
            block_masses[name] = df_masses.loc[(z, n), 'Mass_MeV']

    interface_database = defaultdict(list)

    print(f"[*] Сканирование базы изотопов ({len(df_masses)} строк). Ищем макро-стыковки...")
    
    scanned = 0
    for (z, n), row in df_masses.iterrows():
        if z < 2 or n < 2: continue 
        target_mass = row['Mass_MeV']
        
        available_blocks = [(bx, by, bname) for bx, by, bname in CORE_BLOCKS if bname in block_masses]
        
        for b1, b2 in itertools.combinations_with_replacement(available_blocks, 2):
            if b1[0] + b2[0] == z and b1[1] + b2[1] == n:
                m1 = block_masses[b1[2]]
                m2 = block_masses[b2[2]]
                fusion_energy = (m1 + m2) - target_mass
                
                pair_key = tuple(sorted([b1[2], b2[2]]))
                interface_database[pair_key].append(fusion_energy)
                scanned += 1

    print(f"[*] Готово! Просканировано связей: {scanned}\n")
    print("================================================================================")
    print("      ИТОГОВЫЙ АВТОМАТИЧЕСКИЙ СЛОВАРЬ API МАТРИЦЫ (ВКЛЮЧАЯ ТЯЖЕЛЫЕ)")
    print("================================================================================")
    
    final_api_dictionary = {}
    for pair, energies in interface_database.items():
        if len(energies) > 0:
            avg_energy = np.median(energies)
            final_api_dictionary[pair] = round(float(avg_energy), 3)
            
    # Сортируем вывод: сначала самые выгодные интерфейсы, потом штрафные (отрицательные)
    sorted_api = sorted(final_api_dictionary.items(), key=lambda x: x[1], reverse=True)
    
    for pair, energy in sorted_api:
        pair_str = f"('{pair[0]}', '{pair[1]}')"
        if energy < 0:
            print(f"{pair_str:<22} | {energy:>14.3f} МэВ  [🚨 GEOMETRY OVERFLOW]")
        else:
            print(f"{pair_str:<22} | {energy:>14.3f} МэВ")

    print("\n[+] Готовый программный словарь для вставки в Ab Initio Компилятор:")
    print("API_FUSION = {")
    for k, v in final_api_dictionary.items():
        print(f"    ('{k[0]}', '{k[1]}'): {v},")
    print("}")

if __name__ == "__main__":
    run_auto_extraction()
