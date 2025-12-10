Import math

def log_header(title):
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

# --- КОНСТАНТЫ МОДЕЛИ (ЗАМОРОЖЕНО) ---
E_ALPHA = 28.30   # Энергия связи одной Альфа-частицы (He-4)
E_LINK  = 2.425   # Энергия одной геометрической связи (Face-to-Face)

# --- БАЗА ДАННЫХ РЕАЛЬНОСТИ (CODATA / AME2020) ---
# Total Binding Energy (in MeV) for Alpha-Conjugate Nuclei
REAL_DATA = {
    "Be-8":  56.50,   # 2 Alphas
    "C-12":  92.16,   # 3 Alphas
    "O-16":  127.62,  # 4 Alphas
    "Ne-20": 160.64,  # 5 Alphas
    "Mg-24": 198.25,  # 6 Alphas
    "Si-28": 236.53,  # 7 Alphas
    "S-32":  271.78,  # 8 Alphas
    "Ar-36": 306.72,  # 9 Alphas
    "Ca-40": 342.05,  # 10 Alphas
    # Изотопы "с добавкой" (проверка чувствительности)
    "He-5":  27.41,   # Alpha + n (unstable)
    "Li-6":  31.99,   # Alpha + d
    "Li-7":  39.24,   # Alpha + t
    "Be-9":  58.16,   # 2 Alpha + n
    "B-10":  64.75,   # 2 Alpha + d
    "B-11":  76.20,   # 2 Alpha + t
    "C-13":  97.11,   # 3 Alpha + n
    "N-14":  104.66,  # 3 Alpha + d
    "O-17":  131.76,  # 4 Alpha + n
    "F-19":  147.80   # 4 Alpha + t
}

# --- ГЕОМЕТРИЧЕСКИЙ ДВИЖОК ---
def get_geometry(n_alphas):
    """
    Возвращает количество связей (Links) для оптимальной упаковки N тетраэдров.
    Логика: Мы строим ГЦК-решетку (Tetrahedral Packing).
    """
    if n_alphas == 1: return 0  # Сам по себе
    if n_alphas == 2: return 0  # Be-8 (Гантель, слабая связь, считаем 0 "лишних" прочных)
    if n_alphas == 3: return 3  # C-12 (Треугольник)
    if n_alphas == 4: return 6  # O-16 (Тетраэдр)
    if n_alphas == 5: return 9  # Ne-20 (Бипирамида)
    if n_alphas == 6: return 12 # Mg-24 (Октаэдр / Кольцо)
    if n_alphas == 7: return 15 # Si-28 (Пентагональная бипирамида / Стек)
    if n_alphas == 8: return 18 # S-32 (Два тетраэдра O-16 гранью)
    if n_alphas == 9: return 21 # Ar-36 (Рост кристалла)
    if n_alphas == 10: return 24 # Ca-40 (Замкнутый дважды магический кор)
    
    # Для N > 10 работает формула плотной упаковки ~ 3N - 6
    return 3 * n_alphas - 6

def simulate_nucleus(name):
    # Парсим состав
    # Упрощенно: считаем сколько альф влезает
    # Если имя есть в базе, берем реальную энергию
    
    real_be = REAL_DATA.get(name, 0)
    if real_be == 0: return None
    
    # Определяем состав (грубо по массе)
    # Например Li-6 -> Mass 6 -> 1 Alpha (4) + Remainder (2)
    # Но для теста мы берем таблицу соответствия вручную для точности
    
    # Таблица состава (N_alpha, Remainder_Binding)
    # Remainder Binding - это энергия связи "довеска" (d, t, n)
    # n=0, d=2.22, t=8.48
    composition = {
        "He-4": (1, 0), "Be-8": (2, 0), "C-12": (3, 0), "O-16": (4, 0),
        "Ne-20": (5, 0), "Mg-24": (6, 0), "Si-28": (7, 0), "S-32": (8, 0),
        "Ar-36": (9, 0), "Ca-40": (10, 0),
        "He-5": (1, 0), # n не дает вклада в структуру альфы
        "Li-6": (1, 2.22), "Li-7": (1, 8.48),
        "Be-9": (2, 0), 
        "B-10": (2, 2.22), "B-11": (2, 8.48),
        "C-13": (3, 0), "N-14": (3, 2.22),
        "O-17": (4, 0), "F-19": (4, 8.48)
    }
    
    n_alpha, remainder_be = composition.get(name, (0,0))
    
    # СЧИТАЕМ ГЕОМЕТРИЮ
    links = get_geometry(n_alpha)
    
    # ФОРМУЛА SIMUREALITY
    # BE = (N * E_alpha) + (Links * E_link) + Remainder
    sim_be = (n_alpha * E_ALPHA) + (links * E_LINK) + remainder_be
    
    # ДЛЯ "ГРЯЗНЫХ" ЯДЕР (С добавкой n, d, t)
    # Добавка обычно создает 1-2 дополнительные связи с ядром.
    # Добавим эвристику: каждая добавка (d, t, n) липнет к одной грани альфы (+1 link)
    if name not in ["He-4", "Be-8", "C-12", "O-16", "Ne-20", "Mg-24", "Si-28", "S-32", "Ar-36", "Ca-40"]:
        sim_be += E_LINK # Бонус за прилипание добавки
        
    diff = abs(sim_be - real_be)
    accuracy = 100 * (1 - diff/real_be)
    
    return {
        "name": name,
        "n_alpha": n_alpha,
        "links": links,
        "sim": sim_be,
        "real": real_be,
        "acc": accuracy
    }

def run_mega_test():
    log_header("SIMUREALITY MEGA-TEST: 20 LIGHT NUCLEI")
    print(f"Alpha Energy: {E_ALPHA} | Link Energy: {E_LINK}")
    print("-" * 80)
    print(f"{'NUCLEUS':<10} | {'STRUCTURE':<15} | {'SIM BE':<10} | {'REAL BE':<10} | {'ACCURACY'}")
    print("-" * 80)
    
    targets = list(REAL_DATA.keys())
    
    results = []
    for t in targets:
        res = simulate_nucleus(t)
        if res: results.append(res)
        
    # Сортируем по точности, чтобы видеть победителей и проигравших
    # results.sort(key=lambda x: x['acc'], reverse=True) 
    # Лучше сортировать по массе (по порядку)
    
    for r in results:
        struct = f"{r['n_alpha']}a + {r['links']}L"
        print(f"{r['name']:<10} | {struct:<15} | {r['sim']:<10.2f} | {r['real']:<10.2f} | {r['acc']:.2f}%")

    print("-" * 80)
    avg_acc = sum([r['acc'] for r in results]) / len(results)
    print(f"AVERAGE ACCURACY: {avg_acc:.2f}%")

if __name__ == "__main__":
    run_mega_test()
 Результаты скрипта


SIMUREALITY MEGA-TEST: 20 LIGHT NUCLEI 

================================================================================ 

Alpha Energy: 28.3 | Link Energy: 2.425 

-------------------------------------------------------------------------------- 

NUCLEUS | STRUCTURE | SIM BE | REAL BE | ACCURACY 

-------------------------------------------------------------------------------- 

Be-8 | 2a + 0L | 56.60 | 56.50 | 99.82% 

C-12 | 3a + 3L | 92.18 | 92.16 | 99.98% 

O-16 | 4a + 6L | 127.75 | 127.62 | 99.90% 

Ne-20 | 5a + 9L | 163.32 | 160.64 | 98.33% 

Mg-24 | 6a + 12L | 198.90 | 198.25 | 99.67% 

Si-28 | 7a + 15L | 234.47 | 236.53 | 99.13% 

S-32 | 8a + 18L | 270.05 | 271.78 | 99.36% 

Ar-36 | 9a + 21L | 305.62 | 306.72 | 99.64% 

Ca-40 | 10a + 24L | 341.20 | 342.05 | 99.75% 

He-5 | 1a + 0L | 30.73 | 27.41 | 87.91% 

Li-6 | 1a + 0L | 32.95 | 31.99 | 97.01% 

Li-7 | 1a + 0L | 39.20 | 39.24 | 99.91% 

Be-9 | 2a + 0L | 59.02 | 58.16 | 98.51% 

B-10 | 2a + 0L | 61.24 | 64.75 | 94.59% 

B-11 | 2a + 0L | 67.50 | 76.20 | 88.59% 

C-13 | 3a + 3L | 94.60 | 97.11 | 97.42% 

N-14 | 3a + 3L | 96.82 | 104.66 | 92.51% 

O-17 | 4a + 6L | 130.18 | 131.76 | 98.80% 

F-19 | 4a + 6L | 138.66 | 147.80 | 93.81% 

-------------------------------------------------------------------------
