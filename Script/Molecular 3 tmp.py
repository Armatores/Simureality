import numpy as np

# =====================================================================
# SIMUREALITY: KERNEL V2.1 - TOPO-STRAIN DECOMPILER (CLI)
# Extracting L_strain (Routing Tax) from distorted FCC graphs
# =====================================================================

GAMMA_SYS = 1.0418
RAW_CC = 327.51
RAW_CH = 398.11

# Экспериментальные энергии атомизации циклоалканов (кДж/моль)
CYCLOALKANES = {
    "Cyclopropane (C3H6 - Угол 60°)": {"C-C": 3, "C-H": 6, "E_exp": 3369},
    "Cyclobutane (C4H8 - Угол 90°)": {"C-C": 4, "C-H": 8, "E_exp": 4554},
    "Cyclopentane (C5H10 - Угол 108°)": {"C-C": 5, "C-H": 10, "E_exp": 5748},
    "Cyclohexane (C6H12 - Угол 109.5°)": {"C-C": 6, "C-H": 12, "E_exp": 6943}
}

def extract_routing_strain():
    print("--- АНАЛИЗАТОР ИСКРИВЛЕНИЯ ГРАФА (L_strain) ---")
    print(f"Базовые константы: CC={RAW_CC}, CH={RAW_CH}, Gamma={GAMMA_SYS}\n")
    
    for name, data in CYCLOALKANES.items():
        n_cc = data["C-C"]
        n_ch = data["C-H"]
        e_exp = data["E_exp"]
        
        # 1. Расчет идеального сброса энтропии (без искажений)
        ideal_raw = (n_cc * RAW_CC) + (n_ch * RAW_CH)
        ideal_taxed = ideal_raw * GAMMA_SYS
        
        # 2. Вычисление топологического штрафа Матрицы (L_strain)
        # L_strain = Ideal_Energy - Experimental_Energy
        l_strain = ideal_taxed - e_exp
        strain_per_node = l_strain / n_cc
        
        print(f"[{name}]")
        print(f"  Идеальный профит Матрицы: {ideal_taxed:.1f} кДж/моль")
        print(f"  Фактический профит (Эксперимент): {e_exp} кДж/моль")
        print(f"  [!] ШТРАФ ЗА ИСКРИВЛЕНИЕ (L_strain): {l_strain:.1f} кДж/моль")
        print(f"  Штраф на один излом (узел): {strain_per_node:.1f} кДж/моль")
        print("-" * 50)

if __name__ == "__main__":
    extract_routing_strain()
