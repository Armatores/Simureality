import math

def log_header(text):
    print(f"\n{'='*80}")
    print(f" {text}")
    print(f"{'='*80}")

# ФУНДАМЕНТАЛЬНАЯ КОНСТАНТА (Импеданс Вакуума)
ALPHA_INV = 137.035999 

def analyze_fermionic_resonance():
    log_header("SIMUREALITY GRAPHENE PROBE: FERMIONIC RESONANCE (SPIN 1/2)")
    print("HYPOTHESIS: Optimal conductivity occurs when Lattice Load (N) matches")
    print("            HALF-INTEGER multiples of Vacuum Impedance (N ~ X.5 * 137).")
    print("-" * 80)
    
    print(f"{'INDEX':<6} | {'ANGLE (deg)':<12} | {'ATOMS (N)':<12} | {'RATIO (N/137)':<15} | {'DEV FROM X.5'}")
    print("-" * 80)
    
    candidates = []
    
    # Сканируем индексы (i), соответствующие малым углам
    # i=30 соответствует примерно 1.1 градусу
    for i in range(15, 50):
        # Формулы для гексагональной решетки (Commensurate Angles)
        n = i + 1
        m = i
        # Количество атомов в элементарной ячейке Муара
        N = 4 * (n**2 + n*m + m**2)
        
        # Угол поворота
        cos_theta = (n**2 + 4*n*m + m**2) / (2 * (n**2 + n*m + m**2))
        theta_rad = math.acos(cos_theta)
        theta_deg = math.degrees(theta_rad)
        
        # ПРОВЕРКА НА РЕЗОНАНС
        ratio = N / ALPHA_INV
        decimal_part = ratio % 1
        
        # Нас интересует, насколько дробная часть близка к 0.5 (Спин 1/2)
        dev_from_half = abs(decimal_part - 0.5)
        
        marker = ""
        # Критерий: если отклонение от X.5 меньше 5%
        if dev_from_half < 0.05:
            marker = "<< FERMIONIC SYNC"
            candidates.append((i, theta_deg, N, ratio))
        
        # Фильтруем вывод для чистоты
        print(f"{i:<6} | {theta_deg:<12.4f} | {N:<12} | {ratio:<15.4f} | {dev_from_half:.4f} {marker}")

    print("-" * 80)
    
    if candidates:
        print("\nTOP CANDIDATES (Resonance Peaks):")
        for i, ang, n, r in candidates:
            # r:.1f округлит 61.502 до 61.5, показывая чистоту резонанса
            print(f"Index {i}: Angle {ang:.3f}° | Ratio {r:.4f} (~{r:.1f})")
            
            if abs(ang - 1.1) < 0.2:
                print("   ^^^ THIS IS THE MAGIC ANGLE REGION ^^^")

if __name__ == "__main__":
    analyze_fermionic_resonance()
