import math

def log(msg):
    print(msg)

def check_vector_alignment(name, x, y, z):
    # Нормализуем вектор (делим на максимальный компонент по модулю)
    m = max(abs(x), abs(y), abs(z))
    if m == 0: return # Центр (s-орбиталь)
    
    nx, ny, nz = x/m, y/m, z/m
    
    # Проверяем, близки ли компоненты к целым числам (или 0.5)
    # В ГЦК решетке направления - это [1,0,0], [1,1,0], [1,1,1]
    
    # Округляем до 3 знаков для проверки
    vec = [round(nx, 3), round(ny, 3), round(nz, 3)]
    
    # Определяем тип узла решетки
    lattice_type = "UNKNOWN / OFF-GRID"
    
    # 1. FACE CENTER / CORNER (Кубические оси) -> [1, 0, 0]
    if vec in ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]):
        lattice_type = "LATTICE AXIS (Кубическая грань)"
        
    # 2. EDGE CENTER (Диагональ грани) -> [1, 1, 0]
    elif abs(vec[0])==1 and abs(vec[1])==1 and vec[2]==0:
        lattice_type = "LATTICE EDGE (Диагональ грани)"
    elif abs(vec[0])==1 and abs(vec[2])==1 and vec[1]==0:
        lattice_type = "LATTICE EDGE (Диагональ грани)"
    elif abs(vec[1])==1 and abs(vec[2])==1 and vec[0]==0:
        lattice_type = "LATTICE EDGE (Диагональ грани)"
        
    # 3. BODY CENTER (Диагональ куба) -> [1, 1, 1]
    elif abs(vec[0])==1 and abs(vec[1])==1 and abs(vec[2])==1:
        lattice_type = "LATTICE VOID (Диагональ куба - Тетраэдр)"

    print(f"Orbital {name:<10} | Max Vector: {vec} | {lattice_type}")

def scan_orbitals():
    print("--- ELECTRON LATTICE SCANNER ---")
    print("Hypothesis: Orbital lobes point to Integer Lattice Nodes.")
    print("-" * 65)
    
    # Сканируем сферу направлений (грубый перебор для наглядности)
    # Шаг сканирования
    step = 0.05 
    
    # База данных "Реальных Орбиталей" (Real Spherical Harmonics)
    # Мы ищем углы (theta, phi), где функция максимальна.
    
    # 1. P-Orbitals (l=1)
    # Pz = cos(theta) -> Max at Z axis
    check_vector_alignment("p_z", 0, 0, 1)
    # Px = sin(theta)cos(phi) -> Max at X axis
    check_vector_alignment("p_x", 1, 0, 0)
    
    # 2. D-Orbitals (l=2) - Самое интересное!
    # d_z2 (Z-квадрат) -> Вдоль оси Z
    check_vector_alignment("d_z2", 0, 0, 1)
    
    # d_x2-y2 (X квадрат минус Y квадрат) -> Вдоль осей X и Y
    check_vector_alignment("d_x2-y2", 1, 0, 0)
    
    # d_xy (Клевер) -> Биссектриса между X и Y
    # Максимум при phi=45 grad (x=y)
    check_vector_alignment("d_xy", 1, 1, 0)
    
    # d_yz -> Биссектриса Y и Z
    check_vector_alignment("d_yz", 0, 1, 1)
    
    # d_xz -> Биссектриса X и Z
    check_vector_alignment("d_xz", 1, 0, 1)
    
    # 3. F-Orbitals (l=3) - Сложная геометрия
    # f_xyz (Кубическая орбиталь) -> Max при x=y=z
    check_vector_alignment("f_xyz", 1, 1, 1)
    
    # f_z3 -> Вдоль Z
    check_vector_alignment("f_z3", 0, 0, 1)
    
    print("-" * 65)
    print("ANALYSIS COMPLETE.")

if __name__ == "__main__":
    scan_orbitals()
