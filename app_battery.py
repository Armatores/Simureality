import pandas as pd
import numpy as np
import math

# ==============================================================================
# SIMUREALITY V36.0: HARMONIC RESONANCE ENGINE (PURE GEOMETRY)
# Zero Chemistry. Zero Curve-Fitting. Only Vacuum Wave Harmonics.
# ==============================================================================

# --- 1. АБСОЛЮТНЫЕ КОНСТАНТЫ МАТРИЦЫ (БЕЗ ПОДГОНОК) ---
BOHR_CIRCUMFERENCE = 2 * math.pi * 0.529177
VACUUM_GATE = round(BOHR_CIRCUMFERENCE, 3)  # 3.325 Å (Базовый такт Вселенной)

# Идеальные гармоники роутинга (Проекции Пикселя в 3D пространстве)
HARMONICS = {
    "H0 (Native Base 3.325 Å)": VACUUM_GATE,
    "H_BCC (BCC Diag 2.879 Å)": VACUUM_GATE * (np.sqrt(3) / 2.0), 
    "H_FCC (FCC Diag 2.351 Å)": VACUUM_GATE * (np.sqrt(2) / 2.0)  
}

# --- 2. СЫРЫЕ АППАРАТНЫЕ ДАННЫЕ (Удален весь мусор и костыли) ---
raw_data = [
    {"id": "LCO (iPhone Cathode)", "a": 2.816, "b": 2.816, "c": 14.05, "calc_method": "Layer_A"},
    {"id": "NMC811 (Tesla Cathode)", "a": 2.874, "b": 2.874, "c": 14.21, "calc_method": "Layer_A"},
    {"id": "LFP (BYD Cathode)", "a": 10.33, "b": 6.01, "c": 4.69, "calc_method": "Olivine_B_Half"},
    {"id": "Spinel LMO", "a": 8.24, "b": 8.24, "c": 8.24, "calc_method": "Spinel_Hop"},
    {"id": "Lithium Metal (Anode)", "a": 3.51, "b": 3.51, "c": 3.51, "calc_method": "NN_BCC"},
    {"id": "Chevrel Mo6S8", "a": 6.50, "b": 6.50, "c": 6.50, "calc_method": "NN_FCC_Ion"}
]

# --- 3. ЧЕСТНЫЙ МАТЕМАТИЧЕСКИЙ ДВИЖОК ---
def extract_hop_distance(row):
    # Только строгая 3D кристаллография (Никаких a/2.5!)
    method = row['calc_method']
    a, b, c = row['a'], row['b'], row['c']
    
    if method == 'Layer_A': return a
    elif method == 'Olivine_B_Half': return b / 2.0
    elif method == 'Spinel_Hop': return a * np.sqrt(2) / 4.0 # Точный 3D-прыжок в Шпинели (от 8a к 16c)
    elif method == 'NN_BCC': return a * np.sqrt(3) / 2.0     # От центра к углу куба
    elif method == 'NN_FCC_Ion': return a / 2.0
    return 0.0

def evaluate_resonance(hop):
    # Матрица ищет ближайшую РАЗРЕШЕННУЮ частоту (как радиоприемник)
    best_name = None
    best_diff = float('inf')
    best_target = 0
    
    for name, val in HARMONICS.items():
        diff = abs(hop - val)
        if diff < best_diff:
            best_diff = diff
            best_name = name
            best_target = val
            
    pct = (best_diff / best_target) * 100
    
    # Жесткий грейд. Идеальный резонанс не прощает ошибок.
    if pct <= 1.5: status = "🏆 PERFECT RESONANCE (Super-Ionic)"
    elif pct <= 4.5: status = "✅ SYNCED (Low Drag)"
    elif pct <= 8.0: status = "⚠️ LOSSY (Thermal Noise / Jitter)"
    else: status = "❌ KERNEL PANIC (Stuck)"
        
    return best_name, pct, status

# --- 4. КОМПИЛЯЦИЯ БЕЗ ПОДГОНОК ---
results = []
for idx, row in pd.DataFrame(raw_data).iterrows():
    hop = extract_hop_distance(row)
    if hop == 0.0: continue
        
    harm_name, err_pct, status = evaluate_resonance(hop)
    
    results.append({
        "Material": row['id'],
        "Calculated Hop (Å)": round(hop, 3),
        "Locked Harmonic": harm_name,
        "Deviation (%)": round(err_pct, 2),
        "Grid Status": status
    })

res_df = pd.DataFrame(results)

print("\n==========================================================================")
print(" SIMUREALITY V36.0: PURE VACUUM HARMONICS AUDIT (ZERO CURVE-FITTING)")
print("==========================================================================\n")
print(res_df.to_string(index=False))
