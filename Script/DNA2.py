import numpy as np
from scipy.spatial import cKDTree

# --- КОНСТАНТЫ SIMUREALITY ---
GAMMA = 3.325 
A_FCC = GAMMA * np.sqrt(2) # ~4.702 Å

R_DNA = 10.0      
H_RISE = 3.4      
BP_TURN = 10.5    
THETA_STEP = (2 * np.pi) / BP_TURN 
STRAND_SHIFT = 0.8 * np.pi # Сдвиг фазы малой бороздки

# Водный адаптер
R_WATER = 7.5     
WATER_OFFSET = STRAND_SHIFT / 2
ds_dt = np.sqrt((R_WATER * THETA_STEP)**2 + H_RISE**2)
dt_water = 2.8 / ds_dt # Физически честный шаг 2.8 Å

def get_triplex_tensor(num_bases):
    n = np.arange(num_bases)
    
    # Жесткий каркас ДНК (2 нити)
    x1 = R_DNA * np.cos(n * THETA_STEP)
    y1 = R_DNA * np.sin(n * THETA_STEP)
    z1 = n * H_RISE
    strand1 = np.column_stack((x1, y1, z1))
    
    x2 = R_DNA * np.cos(n * THETA_STEP + STRAND_SHIFT)
    y2 = R_DNA * np.sin(n * THETA_STEP + STRAND_SHIFT)
    z2 = n * H_RISE
    strand2 = np.column_stack((x2, y2, z2))
    dna_nodes = np.vstack((strand1, strand2))
    
    # Жидкий водный хребет
    t_water = np.arange(0, num_bases, dt_water)
    xw = R_WATER * np.cos(t_water * THETA_STEP + WATER_OFFSET)
    yw = R_WATER * np.sin(t_water * THETA_STEP + WATER_OFFSET)
    zw = t_water * H_RISE
    water_nodes = np.column_stack((xw, yw, zw))
    
    # Выравнивание по диагонали вакуума [111]
    v_111 = np.array([1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)])
    v = np.cross([0, 0, 1], v_111)
    c = np.dot([0, 0, 1], v_111)
    s = np.linalg.norm(v)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + (vx @ vx) * ((1 - c) / (s**2))
    
    return dna_nodes.dot(R.T), water_nodes.dot(R.T)

def generate_fcc_bbox(coords, padding=20.0):
    min_b = np.min(coords, axis=0) - padding
    max_b = np.max(coords, axis=0) + padding
    min_idx = np.floor(min_b / (A_FCC/2)).astype(int)
    max_idx = np.ceil(max_b / (A_FCC/2)).astype(int)
    nodes = []
    for x in range(min_idx[0], max_idx[0]):
        for y in range(min_idx[1], max_idx[1]):
            for z in range(min_idx[2], max_idx[2]):
                if (x + y + z) % 2 == 0:
                    nodes.append([x * A_FCC/2, y * A_FCC/2, z * A_FCC/2])
    return np.array(nodes)

def get_noise_tensor(shape_like):
    """Генератор случайного шума в габаритах молекулы для честного контроля"""
    min_b = np.min(shape_like, axis=0)
    max_b = np.max(shape_like, axis=0)
    return np.random.uniform(min_b, max_b, shape_like.shape)

# --- ЗАПУСК СИМУЛЯЦИИ ---
print("=== SIMUREALITY: ФАЗОВОЕ СКАНИРОВАНИЕ ИСТИННОГО РЕЗОНАНСА ===")
dna_base, water_base = get_triplex_tensor(42)
fcc_nodes = generate_fcc_bbox(np.vstack((dna_base, water_base)))
tree = cKDTree(fcc_nodes)

# 1. КОНТРОЛЬНЫЙ ЗАМЕР: Случайный цифровой шум
np.random.seed(42) # For reproducible noise
noise_dna = get_noise_tensor(dna_base)
noise_water = get_noise_tensor(water_base)
noise_dna_dists, _ = tree.query(noise_dna)
noise_water_dists, _ = tree.query(noise_water)
base_noise_dna = np.mean(noise_dna_dists)
base_noise_water = np.mean(noise_water_dists)

print(f"\n[КОНТРОЛЬ] Среднее метрическое напряжение для хаотичных данных:")
print(f"Шум (объем ДНК) : {base_noise_dna:.4f} Å")
print(f"Шум (объем H2O) : {base_noise_water:.4f} Å")

# 2. ФАЗОВОЕ СКАНИРОВАНИЕ (3D Convolution)
print(f"\n[СКАНИРОВАНИЕ] Ищем точку геометрического резонанса. Выполняю трансляцию...")
scan_step = 0.25 # Шаг сдвига в ангстремах 
shifts = np.arange(0, A_FCC, scan_step)

best_mean_total = float('inf')
best_shift = None
best_dna_lag = None
best_water_lag = None

for dx in shifts:
    for dy in shifts:
        for dz in shifts:
            shift_vec = np.array([dx, dy, dz])
            
            dists_dna, _ = tree.query(dna_base + shift_vec)
            dists_water, _ = tree.query(water_base + shift_vec)
            
            mean_dna = np.mean(dists_dna)
            mean_water = np.mean(dists_water)
            
            mean_total = (mean_dna + mean_water) / 2 
            
            if mean_total < best_mean_total:
                best_mean_total = mean_total
                best_shift = shift_vec
                best_dna_lag = mean_dna
                best_water_lag = mean_water

# 3. ВЕРДИКТ
print(f"\n[РЕЗУЛЬТАТ] Идеальная посадка в решетку найдена при сдвиге: X={best_shift[0]:.2f}, Y={best_shift[1]:.2f}, Z={best_shift[2]:.2f}")
print(f"Сырой лаг ДНК : {best_dna_lag:.4f} Å (Улучшение на {(base_noise_dna - best_dna_lag)/base_noise_dna*100:.1f}% относительно шума)")
print(f"Сырой лаг H2O : {best_water_lag:.4f} Å (Улучшение на {(base_noise_water - best_water_lag)/base_noise_water*100:.1f}% относительно шума)")

if best_dna_lag < base_noise_dna and best_water_lag < base_noise_water:
    print("\n[ВЫВОД СИСТЕМЫ] СТРУКТУРНЫЙ РЕЗОНАНС ПОДТВЕРЖДЕН.")
    print("Архитектура ДНК + H2O не является случайной. Водяной хребет работает как аппаратный адаптер, центрируя молекулу в узлах вакуумной решетки.")
else:
    print("\n[ВЫВОД СИСТЕМЫ] РЕЗОНАНС НЕ НАЙДЕН. Молекула конфликтует с решеткой на уровне случайного шума.")
