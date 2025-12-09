import math

def log_header(text):
    print(f"\n{'='*100}")
    print(f" {text}")
    print(f"{'='*100}")

# --- 1. GEOMETRY KERNEL (FORMULAS ONLY) ---
# Источник формул: "On the number of atoms in a cluster", OEIS.

def gen_cuboctahedron(limit):
    """FCC: Классическая оболочка."""
    # Formula: 10n^3/3 + 5n^2 + 11n/3 + 1 (Centered) -> 1, 13, 55, 147, 309, 561
    # Проще рекурсией слоев: 10*n^2 + 2
    nums = [1]
    n = 1
    while nums[-1] < limit:
        # Mackay icosahedron / Cuboctahedron sequence
        val = (10 * n**3 + 15 * n**2 + 11 * n + 3) // 3
        val = int(val)
        if val > limit: break
        nums.append(val)
        n += 1
    return nums

def gen_truncated_octahedron(limit):
    """FCC: Усеченный октаэдр (Space-filling Wigner-Seitz cell)."""
    # Formula: 16n^3 + 15n^2 + 6n + 1 (для n=0,1..) ? 
    # Sequence: 1, 38, 201, 586, 1289...
    nums = [1]
    n = 1
    while nums[-1] < limit:
        val = 16*n**3 + 15*n**2 + 6*n + 1
        if val > limit: break
        nums.append(val)
        n += 1
    return nums

def gen_rhombic_dodecahedron(limit):
    """BCC: Ромбододекаэдр (Space-filling)."""
    # Sequence: 1, 15, 65, 175, 369...
    nums = [1]
    n = 1
    while nums[-1] < limit:
        val = 4*n**3 + 6*n**2 + 4*n + 1
        if val > limit: break
        nums.append(val)
        n += 1
    return nums

def gen_centered_cube(limit):
    """BCC: Центрированный куб."""
    # Sequence: 1, 9, 35, 91, 189...
    # Formula: n^3 + (n-1)^3
    nums = [1]
    n = 2 # start from 2 to get 9
    while nums[-1] < limit:
        val = n**3 + (n-1)**3
        if val > limit: break
        nums.append(val)
        n += 1
    return nums

# Генерируем "Справочник Геометрии"
GEO_LIB = {
    "FCC": {
        "Cuboctahedron": gen_cuboctahedron(1000),       # [1, 13, 55, 147, 309...]
        "Truncated Oct": gen_truncated_octahedron(1000) # [1, 38, 201, 586...]
    },
    "BCC": {
        "Rhombic Dod": gen_rhombic_dodecahedron(1000),  # [1, 15, 65, 175...]
        "Centered Cube": gen_centered_cube(1000)        # [1, 9, 35, 91...]
    }
}

# --- 2. DATASET (Real Mass) ---
SAMPLES = [
    # --- THE GOLD STANDARDS ---
    {"name": "H3S (Pressure)", "mass": 35.0,  "lat": "BCC", "Tc": 203.0}, # The King
    {"name": "Mercury (Hg)",   "mass": 200.59,"lat": "FCC", "Tc": 4.2},   # The First
    {"name": "Lead (Pb)",      "mass": 207.2, "lat": "FCC", "Tc": 7.2},   # The Heavy
    {"name": "Niobium (Nb)",   "mass": 92.9,  "lat": "BCC", "Tc": 9.2},   # The MRI Magnet
    
    # --- THE WEAK / NON-SC ---
    {"name": "Copper (Cu)",    "mass": 63.55, "lat": "FCC", "Tc": 0.0},
    {"name": "Gold (Au)",      "mass": 196.97,"lat": "FCC", "Tc": 0.0},
    {"name": "Aluminum (Al)",  "mass": 26.98, "lat": "FCC", "Tc": 1.2},
    {"name": "Iron (Fe)",      "mass": 55.85, "lat": "BCC", "Tc": 0.0},
    
    # --- TETRAGONAL (TREATED AS DISTORTED) ---
    {"name": "Tin (White Sn)", "mass": 118.7, "lat": "FCC", "Tc": 3.7}, # Beta-Sn is distorted cubic
    {"name": "Indium (In)",    "mass": 114.8, "lat": "FCC", "Tc": 3.4},
]

# --- 3. THE TEST ---

def run_test():
    log_header("SCIENTIFIC GEOMETRY MATCHING (NO MAGIC NUMBERS)")
    print(f"{'MATERIAL':<15} | {'MASS':<6} | {'LAT':<3} | {'SHAPE FOUND':<15} | {'TARGET':<4} | {'ERROR %':<7} | {'Tc'}")
    print("-" * 100)
    
    for s in SAMPLES:
        mass = s['mass']
        lat_type = s['lat'] # FCC or BCC
        
        # 1. Берем все доступные формы для этой решетки
        available_shapes = GEO_LIB[lat_type]
        
        # 2. Ищем лучшее совпадение среди ВСЕХ форм
        best_match = None
        min_error = 100.0
        best_target = 0
        shape_name = ""
        
        for s_name, sequence in available_shapes.items():
            # Находим ближайшее число в этой последовательности
            target = min(sequence, key=lambda x: abs(x - mass))
            error = abs(mass - target) / target * 100
            
            if error < min_error:
                min_error = error
                best_target = target
                shape_name = s_name
                best_match = target

        # 3. Вывод
        # Маркер для хороших совпадений
        marker = ""
        if min_error < 1.0: marker = " 🔥" # PERFECT
        elif min_error < 3.0: marker = " ✅" # GOOD
        
        print(f"{s['name']:<15} | {mass:<6.1f} | {lat_type:<3} | {shape_name:<15} | {best_target:<4} | {min_error:<7.2f}{marker} | {s['Tc']}")

    print("-" * 100)
    print("HYPOTHESIS CHECK:")
    print("1. H3S (35.0) -> Should match BCC Cube (35).")
    print("2. Mercury (200.6) -> Should match Truncated Octahedron (201).")
    print("3. Copper (63.5) -> Should MISS all shapes.")

if __name__ == "__main__":
    run_test()
