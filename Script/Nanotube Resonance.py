import math

def log_header(text):
    print(f"\n{'='*90}")
    print(f" {text}")
    print(f"{'='*90}")

ALPHA_INV = 137.035999 

def analyze_nanotubes():
    log_header("SIMUREALITY PROBE: CARBON NANOTUBE RESONANCE")
    print("HYPOTHESIS: Optimal Ballistic Transport occurs when the Tube Circumference (C)")
    print("            resonates with the Vacuum Impedance Length (L ~ 137).")
    print("-" * 90)
    print(f"{'CHIRALITY (n,m)':<18} | {'TYPE':<10} | {'DIAMETER (nm)':<14} | {'RES. FACTOR':<12} | {'DEV'}")
    print("-" * 90)
    
    # Константа решетки графена (расстояние между центрами сот) a = 0.246 нм
    a_cc = 0.246 
    
    candidates = []
    
    # Сканируем индексы n, m
    # n от 5 до 50 (реалистичные диаметры трубок)
    for n in range(5, 50):
        for m in range(0, n + 1):
            
            # 1. Определяем тип трубки
            # Если (n - m) делится на 3 -> Металл (проводник)
            # Иначе -> Полупроводник
            if (n - m) % 3 == 0:
                dtype = "METALLIC"
            else:
                dtype = "SEMICOND"
                
            # Нас интересуют только сверх-проводники (металлы)
            if dtype != "METALLIC":
                continue

            # 2. Вычисляем длину окружности (C) и Диаметр (d)
            # C = a * sqrt(n^2 + nm + m^2)
            # В единицах "количества углеродных колец" длина C пропорциональна sqrt(...)
            # Но Simureality оперирует чистыми числами.
            # Эффективное число атомов в "поясе" резонанса:
            # Для "кресельных" (armchair, n=m) трубок это просто 2*n
            # Для "зигзаг" (zigzag, m=0) это 2*n
            # Для хиральных сложнее. Используем метрику длины пути L.
            
            L_vector = math.sqrt(n**2 + n*m + m**2)
            
            # Диаметр в нанометрах
            d_nm = (a_cc * L_vector) / math.pi
            
            # 3. ПРОВЕРКА НА РЕЗОНАНС С 137
            # Гипотеза: Длина вектора хиральности (L) должна быть гармоникой 137?
            # Или L должно быть связано с Pi?
            # Попробуем простую гармонику: 137 / L должно быть целым (стоячая волна).
            
            # Частота моды (сколько раз длина укладывается в 137)
            mode = ALPHA_INV / L_vector
            
            # Проверяем на целочисленность (резонанс стоячей волны)
            # Или полу-целочисленность (фермионы)
            decimal_part = mode % 1
            dev_int = min(decimal_part, 1 - decimal_part) # Близость к целому
            dev_half = abs(decimal_part - 0.5)            # Близость к X.5
            
            # Ищем самый сильный сигнал (либо X.0 либо X.5)
            # Для трубок (цилиндр) ожидаем бозонный резонанс (X.0) - замыкание волны
            
            is_sync = False
            harmonic = 0.0
            
            if dev_int < 0.02:
                is_sync = True
                marker = "<< WAVE SYNC"
                dev = dev_int
                harmonic = round(mode)
            elif dev_half < 0.02:
                is_sync = True
                marker = "<< SPIN SYNC"
                dev = dev_half
                harmonic = mode
                
            if is_sync:
                 print(f"({n:>2}, {m:>2})           | {dtype:<10} | {d_nm:<14.4f} | {harmonic:<12.1f} | {dev:.4f} {marker}")

if __name__ == "__main__":
    analyze_nanotubes()
