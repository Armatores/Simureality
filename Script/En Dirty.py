import math

def log_header(title):
    print(f"\n{'='*100}")
    print(f" {title}")
    print(f"{'='*100}")

# --- КОНСТАНТЫ SIMUREALITY (НЕИЗМЕННЫ) ---
# E_ALPHA: Энергия связи He-4 (Тетраэдра)
E_ALPHA = 28.30
# E_LINK: Энергия одной геометрической связи (Сжатое ребро Up-кварка)
# Это наша "валюта" для спаривания и прилипания
E_LINK  = 2.425   

# --- БАЗА ДАННЫХ: 30 ГРЯЗНЫХ ИЗОТОПОВ (AME2020) ---
# Мы берем изотопы, которые НЕ делятся на 4 нацело (остаток 1, 2, 3)
EXTENDED_DIRTY_SET = {
    # Light (Li, Be, B)
    "Li-6":  31.99,  "Li-7":  39.24,
    "Be-9":  58.16,  "Be-10": 64.98,
    "B-10":  64.75,  "B-11":  76.20,
    
    # Medium (C, N, O, F)
    "C-13":  97.11,  "C-14": 105.28,
    "N-14": 104.66,  "N-15": 115.49,
    "O-17": 131.76,  "O-18": 139.81,
    "F-19": 147.80,
    
    # Heavy-ish (Ne, Na, Mg)
    "Ne-21": 167.41, "Ne-22": 177.77,
    "Na-23": 186.56, 
    "Mg-25": 205.58, "Mg-26": 216.68,
    
    # Metal & Silicon (Al, Si)
    "Al-27": 224.95,
    "Si-29": 245.01, "Si-30": 255.60,
    
    # Phosphorus & Sulfur (P, S)
    "P-31":  262.92,
    "S-33":  279.00, "S-34": 291.84,
    
    # Chlorine & Argon (Cl, Ar)
    "Cl-35": 298.21, "Cl-37": 317.32,
    "Ar-38": 327.34, "Ar-39": 333.68, # Ar-40 исключаем, это 10-Alpha (чистый)
    
    # Potassium & Calcium neighbors
    "K-39":  333.72, "K-41": 351.66
}

# --- ЛОГИКА МОДЕЛИ ---

def get_pairing_bonus(Z, N):
    """
    Раздельный учет спаривания (Pairing Term).
    Валюта: 0.75 * E_LINK за каждую пару.
    """
    bonus = 0
    # Бонус за пары внутри своей группы
    if N % 2 == 0: bonus += (E_LINK * 0.75)
    if Z % 2 == 0: bonus += (E_LINK * 0.75)
    
    # Штраф за Нечет-Нечет (Odd-Odd) - взаимная дестабилизация
    # Это "Wigner penalty" на языке геометрии
    if Z % 2 != 0 and N % 2 != 0:
        bonus -= E_LINK 
        
    return bonus

def get_geometry_energy(A):
    """
    Считает энергию геометрического каркаса.
    """
    n_alpha = A // 4
    remainder = A % 4
    
    # 1. Энергия Альфа-Ядра (Core)
    # Формула упаковки тетраэдров (3n - 6 связей)
    if n_alpha < 2: core_links = 0
    else: core_links = 3 * n_alpha - 6
    if core_links < 0: core_links = 0
    
    core_E = (n_alpha * E_ALPHA) + (core_links * E_LINK)
    
    # 2. Энергия "Мусора" (Debris Topology)
    # ВАЖНО: Топология зависит от формы остатка
    debris_E = 0
    
    if remainder == 1: 
        # Нейтрон/Протон. 
        # В нашей модели энергия одиночки ~0 (он не образует жесткой структуры сам по себе).
        # Его вклад идет через Pairing Bonus.
        debris_E = 0 
        
    elif remainder == 2:
        # Дейтрон (Палочка).
        # Топология: Ложится в желоб или к ребру.
        # Связи: 1 Link.
        debris_E = 2.22 + (1 * E_LINK)
        
    elif remainder == 3:
        # Тритон/He-3 (Треугольник).
        # Топология: Face-to-Face docking (Грань к Грани).
        # Связи: 3 Links! (Это наше главное открытие)
        debris_E = 8.48 + (3 * E_LINK) 
        
    return core_E + debris_E

def get_meta_data(name):
    # Парсер имени (Li-7 -> Z=3, A=7)
    # Упрощенная таблица для скрипта
    periodic_table = {
        "H":1, "He":2, "Li":3, "Be":4, "B":5, "C":6, "N":7, "O":8, "F":9, "Ne":10,
        "Na":11, "Mg":12, "Al":13, "Si":14, "P":15, "S":16, "Cl":17, "Ar":18, "K":19, "Ca":20
    }
    symbol = name.split("-")[0]
    A = int(name.split("-")[1])
    Z = periodic_table.get(symbol, 0)
    return Z, A

def run_simulation():
    log_header(f"SIMUREALITY MASTER TEST: {len(EXTENDED_DIRTY_SET)} DIRTY ISOTOPES")
    print(f"Logic: Alpha Core + Debris Topology + Pairing Bonus")
    print(f"Debris Rules: Rem=1(0L), Rem=2(1L), Rem=3(3L Face-to-Face)")
    print("-" * 100)
    print(f"{'NUCLEUS':<8} | {'STRUCT':<10} | {'SIM BE':<10} | {'REAL BE':<10} | {'ACCURACY'}")
    print("-" * 100)
    
    results = []
    
    # Сортируем по массе (A)
    sorted_iso = sorted(EXTENDED_DIRTY_SET.keys(), key=lambda x: int(x.split("-")[1]))
    
    total_acc = 0
    
    for name in sorted_iso:
        real_be = EXTENDED_DIRTY_SET[name]
        Z, A = get_meta_data(name)
        N = A - Z
        
        # Расчет
        geo_E = get_geometry_energy(A)
        pair_E = get_pairing_bonus(Z, N)
        sim_be = geo_E + pair_E
        
        acc = 100 * (1 - abs(sim_be - real_be)/real_be)
        total_acc += acc
        
        # Структура для вывода
        rem = A % 4
        n_alpha = A // 4
        struct = f"{n_alpha}a+{rem}n"
        
        results.append((name, struct, sim_be, real_be, acc))
        print(f"{name:<8} | {struct:<10} | {sim_be:<10.2f} | {real_be:<10.2f} | {acc:.2f}%")
        
    print("-" * 100)
    print(f"AVERAGE ACCURACY: {total_acc / len(results):.2f}%")
    
    # Анализ "Face-to-Face" (Rem=3)
    rem3_acc = sum([r[4] for r in results if "+3n" in r[1]]) / len([r for r in results if "+3n" in r[1]])
    print(f"SUB-ANALYSIS: Accuracy for 'Face-to-Face' clusters (+3n): {rem3_acc:.2f}%")

if __name__ == "__main__":
    run_simulation()
