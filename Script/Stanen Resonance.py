import math

def log_header(text):
    print(f"\n{'='*90}")
    print(f" {text}")
    print(f"{'='*90}")

ALPHA_INV = 137.035999 

def scan_stanene():
    # Станен: Геометрия как у графена (Factor 4), но физика Z=50.
    # Мы ищем не только "тонкие" резонансы (как 81.5), но и "грубые" (Low Harmonic),
    # которые могут быть стабильны для тяжелого атома.
    
    atoms_per_cell = 4
    
    log_header(f"MATERIAL SCAN: TWISTED BILAYER STANENE (Sn)")
    print(f"Load Factor: {atoms_per_cell} (Honeycomb Topology)")
    print(f"Target: Low-Order Harmonics (Strong Coupling due to Z=50)")
    print("-" * 90)
    print(f"{'INDEX':<6} | {'ANGLE (deg)':<12} | {'ATOMS (N)':<12} | {'HARMONIC':<15} | {'STRENGTH'}")
    print("-" * 90)
    
    candidates = []
    
    # Сканируем углы (индексы i)
    for i in range(1, 60):
        n = i + 1
        m = i
        
        # 1. Количество атомов
        N = atoms_per_cell * (n**2 + n*m + m**2)
        
        # 2. Угол
        cos_theta = (n**2 + 4*n*m + m**2) / (2 * (n**2 + n*m + m**2))
        if cos_theta > 1.0: cos_theta = 1.0
        theta_rad = math.acos(cos_theta)
        theta_deg = math.degrees(theta_rad)
        
        # 3. Резонанс
        ratio = N / ALPHA_INV
        decimal_part = ratio % 1
        dev_from_half = abs(decimal_part - 0.5)
        
        # Ищем Фермионные резонансы (X.5)
        if dev_from_half < 0.05:
            harmonic = ratio
            
            # Оценка силы резонанса для Станена
            # Графен работает только на высоких гармониках (>80).
            # Станен может сработать на низких (<50).
            strength_marker = ""
            if harmonic < 30:
                strength_marker = "🔥🔥🔥 (ULTRA)"
            elif harmonic < 50:
                strength_marker = "🔥🔥 (STRONG)"
            elif harmonic < 70:
                strength_marker = "🔥 (MEDIUM)"
            else:
                strength_marker = "(FINE TUNED)" # Как у графена

            candidates.append((theta_deg, harmonic))
            print(f"{i:<6} | {theta_deg:<12.4f} | {N:<12} | {harmonic:<15.4f} | {strength_marker}")

    print("-" * 90)
    print("INTERPRETATION FOR STANENE:")
    print("Look for 'STRONG' or 'ULTRA' peaks. These angles are likely unstable for Graphene")
    print("but could be the 'Room Temperature' sweet spots for Tin due to high SOC.")

if __name__ == "__main__":
    scan_stanene()
