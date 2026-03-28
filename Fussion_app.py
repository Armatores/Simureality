import math

# =====================================================================
# SIMUREALITY: FISSION CLEAVAGE SIMULATOR (MERGED ARCHITECTURE)
# Deterministic Asymmetric Fission via Topology Optimization + Dynamic Garbage Collection
# =====================================================================

# Константы из Таблицы 2 препринта
E_ALPHA = 28.320       
E_MACRO = 2.425        
E_PAIR = 1.180         
J_TAX = 0.0131         

# Идеальные геометрические каркасы (Платоновы сборки / Оболочки)
MAGIC_Z = [28, 40, 50, 82] 
MAGIC_N = [50, 82, 126]

def get_jitter_tax(Z, N):
    """Штраф за 'шероховатость'."""
    if Z <= 0 or N <= 0: return 0
    dist_Z = min([abs(Z - m) for m in MAGIC_Z])
    dist_N = min([abs(N - m) for m in MAGIC_N])
    geom_mismatch = dist_Z + dist_N
    
    # Базовые порты (поверхность) + Штраф за кривизну
    base_ports = 10.0 * ((Z + N)**(2/3))
    total_ports = base_ports + (15.0 * (geom_mismatch**1.2))
    return total_ports * J_TAX

def calculate_topological_profit(Z, N):
    """Универсальная Формула Компиляции"""
    if Z <= 0 or N <= 0: return 0
    N_alpha = min(Z // 2, N // 2)
    
    # Идеальные Макро-линки минус разрывы из-за деформации
    l_ideal = max(0, 3 * N_alpha - 6)
    l_lost = (min([abs(Z - m) for m in MAGIC_Z]) + min([abs(N - m) for m in MAGIC_N])) * 0.4
    N_macro_links = max(0, l_ideal - l_lost)
    
    # Суммарная структурная выгода (Binding Energy)
    BE = (N_alpha * E_ALPHA) + (N_macro_links * E_MACRO) - get_jitter_tax(Z, N)
    if Z % 2 == 0 and N % 2 == 0: BE += E_PAIR
    return BE

# 1. Эмулируем энергию напряженного материнского Урана-236 (до раскола)
BE_U236 = calculate_topological_profit(92, 144) - 22.0 # Штраф за перегрузку ядра

print("="*80)
print("Executing Garbage Collection Protocol (Topology Optimization + Dynamic Neutrons)...")
print("="*80)

# 2. Диспетчер перебирает варианты раскола и ИЩЕТ оптимальный сброс мусора
results = []
for Z1 in range(35, 60): 
    Z2 = 92 - Z1
    best_profit = -float('inf')
    best_A1 = 0
    best_N2 = 0
    best_free_n = 0
    
    # ДИНАМИЧЕСКИЙ СБРОС МУСОРА: Вакуум сам решает, сколько нейтронов выкинуть (от 0 до 5)
    for free_n in range(0, 6): 
        remaining_N = 144 - free_n
        
        for N1 in range(40, 95):
            N2 = remaining_N - N1
            if N2 < 40 or N2 > 105: continue
            
            # Вычислительный Профит = Энергия Осколков - Старая Энергия
            profit = calculate_topological_profit(Z1, N1) + calculate_topological_profit(Z2, N2) - BE_U236
            if profit > best_profit:
                best_profit = profit
                best_A1 = Z1 + N1
                best_N2 = N2
                best_free_n = free_n
                
    results.append((Z1, best_A1, Z2, Z2 + best_N2, best_profit, best_free_n))

# --- РЕНДЕР ГРАФИКА ДЕЛЕНИЯ ---
print(f"{'FRAG 1 (Light)':<16} | {'FRAG 2 (Heavy)':<16} | {'DROP':<4} | {'Q-PROFIT (MeV)':<20}")
print("-" * 80)
max_Q = max(r[4] for r in results)

for r in results:
    Z1, A1, Z2, A2, profit, free_n = r
    # Экспоненциальная вероятность выбора пути (Сборщик Мусора ищет Максимум)
    probability = math.exp((profit - max_Q) / 1.5) * 100 
    
    bar = "█" * int(probability / 3)
    marker = " <== PEAK (ASYMMETRIC CACHE)" if probability > 90 else ""
    marker = " <== SYMMETRIC (VALLEY)" if Z1 == 46 else marker
    
    # Выводим только вероятные исходы (и симметричную долину для контраста)
    if probability > 0.5 or Z1 == 46:
        print(f"Z={Z1:02d} A={A1:03d}     | Z={Z2:02d} A={A2:03d}     | {free_n}n   | {profit:.1f} MeV {bar}{marker}")
