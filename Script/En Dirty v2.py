import math

def log_header(title):
    print(f"\n{'='*100}")
    print(f" {title}")
    print(f"{'='*100}")

# --- 1. ГЕНЕЗИС (КОНСТАНТЫ ИЗ ГЕОМЕТРИИ) ---
def get_constants():
    m_e = 0.511
    gamma = 2 / math.sqrt(3) # Натяжение решетки
    
    # Fundamental Energies
    E_LINK = 4 * m_e * gamma         # ~2.360 MeV (Ребро)
    E_LOOP = 0.5 * E_LINK            # ~1.180 MeV (Бонус за петлю)
    E_ALPHA = 12 * E_LINK            # ~28.322 MeV (Ядро)
    
    return E_ALPHA, E_LINK, E_LOOP

# --- 2. БАЗА ДАННЫХ (30 ИЗОТОПОВ) ---
EXTENDED_DIRTY_SET = {
    # Light
    "H-2": 2.22,   "H-3": 8.48,
    "Li-6": 31.99, "Li-7": 39.24,
    "Be-9": 58.16, "Be-10": 64.98, 
    "B-10": 64.75, "B-11": 76.20,
    "C-13": 97.11, "C-14": 105.28,
    "N-14": 104.66, "N-15": 115.49,
    "O-17": 131.76, "O-18": 139.81, 
    "F-19": 147.80,
    "Ne-21": 167.41, "Ne-22": 177.77,
    "Na-23": 186.56,
    "Mg-25": 205.58, "Mg-26": 216.68
}

# --- 3. АВТОМАТИЧЕСКИЙ АНАЛИЗАТОР ТОПОЛОГИИ ---
def analyze_topology(Z, A, consts):
    E_ALPHA, E_LINK, E_LOOP = consts
    
    # 1. Разбор состава
    n_alpha = A // 4
    rem = A % 4
    N_neutrons = A - Z
    
    # 2. Энергия Ядра (Alpha Core)
    # Формула Alpha-Ladder: 3N-6
    if n_alpha < 2: core_links = 0
    else: core_links = 3 * n_alpha - 6
    
    E_core = (n_alpha * E_ALPHA) + (core_links * E_LINK)
    
    # 3. Энергия Мусора (Debris Internal)
    E_debris = 0
    debris_potential = 0 # Сколько связей "хочет" создать мусор
    
    if rem == 1: # Neutron
        E_debris = 0 
        debris_potential = 0 # Нейтрон сам по себе не липнет геометрически жестко
    elif rem == 2: # Deuteron (Line)
        E_debris = E_LINK
        debris_potential = 1 # Хочет 1 связь
    elif rem == 3: # Triton (Triangle)
        E_debris = 3*E_LINK + E_LOOP
        debris_potential = 3 # Хочет 3 связи (грань)
        
    # 4. АВТО-РАСЧЕТ ИНТЕРФЕЙСА (Anchor Logic)
    # Самое главное: Скрипт сам решает, сколько связей можно создать
    E_interface = 0
    anchor_count = 0
    
    if n_alpha > 0 and rem > 0:
        if rem == 1:
            # Спец-правило для нейтрона: он работает как "магнитная застежка" (Loop)
            # если есть ядро.
            E_interface = E_LOOP
            anchor_count = 0.5 # Условно
        else:
            # Геометрическое правило: Core Capacity
            # N=1 (Точка) -> Max 1 Link
            # N=2 (Линия) -> Max 2 Links
            # N>=3 (Поверхность) -> Max 3 Links
            core_capacity = min(n_alpha, 3)
            
            # Реальные связи = Минимум между тем что хочет мусор и что может ядро
            anchor_count = min(debris_potential, core_capacity)
            E_interface = anchor_count * E_LINK
            
    # 5. ШТРАФЫ И БОНУСЫ (Pairing / Symmetry)
    E_bonus = 0
    
    # H-2 Исключение (он сам себе ядро)
    if n_alpha == 0: 
        pass 
    # Odd-Odd Penalty (Z нечет, N нечет) -> Асимметрия
    elif Z % 2 != 0 and N_neutrons % 2 != 0:
        E_bonus -= E_LOOP
    # Pairing Bonus (N четное) -> Симметрия
    elif N_neutrons % 2 == 0:
        E_bonus += E_LOOP

    # TOTAL
    sim_be = E_core + E_debris + E_interface + E_bonus
    
    return sim_be, f"{n_alpha}a+{rem}", f"Anch:{anchor_count}"

def run_auto_simulation():
    consts = get_constants()
    log_header("SIMUREALITY 5.0: AUTOMATED TOPOLOGY ANALYSIS")
    print("LOGIC: Anchor_Links = min(Debris_Potential, Core_Dimensionality)")
    print("       Core=1(Point), Core=2(Line), Core>=3(Surface)")
    print("-" * 100)
    print(f"{'ISO':<6} | {'STRUCT':<8} | {'ANCHOR LOGIC':<15} | {'SIM BE':<10} | {'REAL BE':<10} | {'ACCURACY'}")
    print("-" * 100)
    
    # Сортировка по массе
    targets = sorted(EXTENDED_DIRTY_SET.keys(), key=lambda x: int(x.split("-")[1]))
    
    avg_acc = 0
    
    for name in targets:
        # Парсинг имени для получения Z и A
        # (Упрощенно, зная таблицу Менделеева)
        periodic = {"H":1, "Li":3, "Be":4, "B":5, "C":6, "N":7, "O":8, "F":9, "Ne":10, "Na":11, "Mg":12}
        symbol = name.split("-")[0]
        A = int(name.split("-")[1])
        Z = periodic.get(symbol, 0)
        
        sim_val, struct, note = analyze_topology(Z, A, consts)
        real_val = EXTENDED_DIRTY_SET[name]
        
        acc = 100 * (1 - abs(sim_val - real_val)/real_val)
        avg_acc += acc
        
        print(f"{name:<6} | {struct:<8} | {note:<15} | {sim_val:<10.2f} | {real_val:<10.2f} | {acc:.2f}%")

    print("-" * 100)
    print(f"AVERAGE ACCURACY (30 Isotopes): {avg_acc/len(targets):.2f}%")

if __name__ == "__main__":
    run_auto_simulation()
