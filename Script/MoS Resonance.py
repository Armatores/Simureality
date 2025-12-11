import math

def log_header(text):
    print(f"\n{'='*90}")
    print(f" {text}")
    print(f"{'='*90}")

# ФУНДАМЕНТАЛЬНАЯ КОНСТАНТА (Импеданс Вакуума)
ALPHA_INV = 137.035999 

def scan_material(name, atoms_per_bilayer_cell):
    """
    name: Название материала
    atoms_per_bilayer_cell: Множитель атомов (4 для Графена, 6 для MoS2)
    """
    log_header(f"MATERIAL SCAN: {name} (Load Factor: {atoms_per_bilayer_cell})")
    print(f"HYPOTHESIS: Resonance at N_atoms / 137 = Half-Integer (Fermionic Mode)")
    print("-" * 90)
    print(f"{'INDEX (i)':<10} | {'ANGLE (deg)':<12} | {'ATOMS (N)':<12} | {'HARMONIC':<15} | {'DEV'}")
    print("-" * 90)
    
    candidates = []
    
    # Сканируем широкий диапазон индексов (геометрий)
    # Для MoS2 углы могут быть больше, поэтому берем i от 10 до 60
    for i in range(10, 65):
        n = i + 1
        m = i
        
        # 1. Вычисляем количество атомов в супер-ячейке Муара
        # Формула N_cell * (n^2 + nm + m^2)
        N = atoms_per_bilayer_cell * (n**2 + n*m + m**2)
        
        # 2. Вычисляем угол поворота
        cos_theta = (n**2 + 4*n*m + m**2) / (2 * (n**2 + n*m + m**2))
        # Защита от ошибок округления
        if cos_theta > 1.0: cos_theta = 1.0
        theta_rad = math.acos(cos_theta)
        theta_deg = math.degrees(theta_rad)
        
        # 3. ПРОВЕРКА НА ВАКУУМНЫЙ РЕЗОНАНС
        ratio = N / ALPHA_INV
        decimal_part = ratio % 1
        dev_from_half = abs(decimal_part - 0.5)
        
        # Ищем точные совпадения (< 2% отклонения)
        if dev_from_half < 0.02:
            candidates.append((theta_deg, ratio))
            marker = "<< SYNC"
            print(f"{i:<10} | {theta_deg:<12.4f} | {N:<12} | {ratio:<15.4f} | {dev_from_half:.4f} {marker}")
            
    return candidates

def main():
    # 1. Контрольная группа: Графен (должен найти ~1.08)
    graphene_peaks = scan_material("Twisted Bilayer Graphene", 4)
    
    # 2. Тестовая группа: MoS2 (должен найти новые углы)
    # В ячейке MoS2 (1 Mo + 2 S) * 2 слоя = 6 атомов
    mos2_peaks = scan_material("Twisted MoS2 (TMD)", 6)
    
    print("\n" + "="*90)
    print("COMPARATIVE PREDICTION:")
    print("If Simureality is correct, Experimentalists should find flat bands for MoS2 near:")
    for angle, harmonic in mos2_peaks:
        # Фильтруем самые "чистые" и реалистичные углы (1-4 градуса)
        if 1.0 < angle < 4.0:
            print(f" -> {angle:.2f}° (Harmonic {harmonic:.1f})")

if __name__ == "__main__":
    main()
