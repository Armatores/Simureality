# ==============================================================================
# SIMUREALITY OS: AUTO-API EXTRACTOR (ГЛОБАЛЬНЫЙ АВТО-ЭКСТРАКТОР КОНСТАНТ)
# Сканирует всю базу AME2020 и автоматически собирает полный Словарь Интерфейсов
# ==============================================================================

import pandas as pd
import numpy as np
import itertools
from collections import defaultdict

MASS_P = 938.272
MASS_N = 939.565

# 1. Загрузка базы AME2020 (твой точный парсер)
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
        print(f"Ошибка загрузки файла: {e}")
        return pd.DataFrame()

# Базовые аппаратные кэши для поиска
CORE_BLOCKS = [
    (1, 1, 'H-2'), (2, 2, 'He-4'), (3, 4, 'Li-7'), 
    (6, 6, 'C-12'), (8, 8, 'O-16'), (10, 10, 'Ne-20'), 
    (12, 12, 'Mg-24'), (14, 14, 'Si-28'), (16, 16, 'S-32'), (20, 20, 'Ca-40')
]

def run_global_extraction():
    print("================================================================================")
    print("        ГЛОБАЛЬНЫЙ АВТО-ЭКСТРАКТОР ИНТЕРФЕЙСОВ МАТРИЦЫ (AME2020)")
    print("================================================================================\n")
    
    df_masses = load_ame_masses("mass.txt")
    if df_masses.empty:
        print("Файл mass.txt не найден или пуст!")
        return

    # Строим словарь масс базовых блоков
    block_masses = {}
    for z, n, name in CORE_BLOCKS:
        try:
            block_masses[name] = df_masses.loc[(z, n), 'Mass_MeV']
        except KeyError:
            pass

    # Контейнер для сбора всех найденных энергий интерфейсов по типам пар
    interface_database = defaultdict(list)

    print("[*] Сканирование всей таблицы изотопов и декомпиляция связей...")
    
    # Пробегаем по всем ядрам в базе
    scanned_count = 0
    for (z, n), row in df_masses.iterrows():
        if z < 3 or n < 3: continue # Пропускаем простейшие
        target_mass = row['Mass_MeV']
        
        # Проверяем все возможные комбинации из 2 блоков (парная стыковка)
        available_blocks = [(bx, by, bname) for bx, by, bname in CORE_BLOCKS if bname in block_masses]
        
        for b1, b2 in itertools.combinations_with_replacement(available_blocks, 2):
            sum_z = b1[0] + b2[0]
            sum_n = b1[1] + b2[1]
            
            if sum_z == z and sum_n == n:
                # Нашли точное совпадение сборки ядро = блок1 + блок2
                m1 = block_masses[b1[2]]
                m2 = block_masses[b2[2]]
                fusion_energy = (m1 + m2) - target_mass
                
                # Сортируем имена блоков по алфавиту для универсальности ключа
                pair_key = tuple(sorted([b1[2], b2[2]]))
                interface_database[pair_key].append(fusion_energy)
                scanned_count += 1

    print(f"[*] Просканировано и найдено макро-связей: {scanned_count}\n")
    print("================================================================================")
    print("      ИТОГОВЫЙ АВТОМАТИЧЕСКИЙ СЛОВАРЬ КОНСТАНТ (API_FUSION)")
    print("================================================================================")
    print(f"{'ТИП ИНТЕРФЕЙСА (ПАРА БЛОКОВ)':<22} | {'СРЕДНЯЯ ЦЕНА (МэВ)':<18} | {'РАЗБРОС (МэВ)'}")
    print("-" * 65)

    final_api_dictionary = {}

    for pair, energies in interface_database.items():
        if len(energies) >= 1: # Если комбинация встречается в таблице
            avg_energy = np.median(energies) # Медиана устойчива к выбросам
            spread = np.max(energies) - np.min(energies)
            pair_str = f"('{pair[0]}', '{pair[1]}')"
            print(f"{pair_str:<22} | {avg_energy:>14.3f} МэВ   | ±{spread:.3f}")
            final_api_dictionary[pair] = round(float(avg_energy), 3)

    print("-" * 65)
    print("\n[+] Готовый код словаря для вставки в Ab Initio Компилятор:")
    print("API_FUSION = {")
    for k, v in final_api_dictionary.items():
        print(f"    ('{k[0]}', '{k[1]}'): {v},")
    print("}")

if __name__ == "__main__":
    run_global_extraction()
