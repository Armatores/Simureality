# 1. Сначала ставим библиотеку (в первой ячейке)
!pip install mp-api

# 2. Потом запускаем поиск (во второй ячейке)
from mp_api.client import MPRester

API_KEY = "Enter API key"  # <--- Вставь сюда свой ключ

# Наш таргет: Длина окружности орбиты Бора
TARGET = 3.3249 
TOL = 0.03 # Ищем в диапазоне +/- 0.03 Å

with MPRester(API_KEY) as mpr:
    print(f"[*] Connecting to Materials Project with Key...")
    
    # Ищем металлы (Band Gap = 0)
    docs = mpr.summary.search(
        band_gap=(0, 0),
        energy_above_hull=(0, 0.05), # Только стабильные
        fields=["material_id", "formula_pretty", "structure", "symmetry"]
    )
    
    print(f"[*] Scanning {len(docs)} candidates...")
    
    hits = []
    for doc in docs:
        if doc.structure:
            a = doc.structure.lattice.a
            b = doc.structure.lattice.b
            c = doc.structure.lattice.c
            
            # Проверяем все оси
            for val, axis in [(a, 'a'), (b, 'b'), (c, 'c')]:
                if abs(val - TARGET) < TOL:
                    hits.append((doc.formula_pretty, axis, val))

    # Сортируем по точности
    hits.sort(key=lambda x: abs(x[2] - TARGET))
    
    print(f"\n{'MATERIAL':<10} | {'AXIS':<4} | {'VALUE':<8} | {'DIFF'}")
    print("-" * 40)
    for name, axis, val in hits[:20]:
        diff = val - TARGET
        print(f"{name:<10} | {axis:<4} | {val:<8.4f} | {diff:+.4f}")
