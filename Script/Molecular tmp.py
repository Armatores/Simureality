# =====================================================================
# SIMUREALITY: KERNEL V2.3 - TRIPLE-STRAIN DECOMPILER (CLI)
# Extracting the Matrix Tax for Triple Bonds (Face Deduplication)
# =====================================================================

GAMMA_SYS = 1.0418
RAW_CC = 327.51  # Базовая стоимость одного линка C-C
RAW_CH = 398.11  # Базовая стоимость одного линка C-H

# Экспериментальные энергии атомизации алкинов (кДж/моль)
ALKYNES = {
    "Acetylene (C2H2 - 1 тройная связь)": {"C#C": 1, "C-C": 0, "C-H": 2, "E_exp": 1644},
    "Propyne (C3H4 - 1 тройная, 1 одинарная)": {"C#C": 1, "C-C": 1, "C-H": 4, "E_exp": 2828},
    "1-Butyne (C4H6 - 1 тройная, 2 одинарных)": {"C#C": 1, "C-C": 2, "C-H": 6, "E_exp": 4001}
}

def calculate_triple_strain():
    print("--- АНАЛИЗАТОР ШТРАФА ТРОЙНОЙ СВЯЗИ (Triple-Strain) ---")
    print("Логика: C#C расценивается алгоритмом как попытка замкнуть 3 линка (3 * RAW_CC)\n")
    
    total_strain = 0
    
    for name, data in ALKYNES.items():
        n_triple = data["C#C"]
        n_single = data["C-C"]
        n_ch = data["C-H"]
        e_exp = data["E_exp"]
        
        # 1. Идеальный профит Матрицы (без штрафа за изгиб)
        # Тройная связь = 3 замкнутых линка
        ideal_raw = (n_triple * 3 * RAW_CC) + (n_single * RAW_CC) + (n_ch * RAW_CH)
        ideal_taxed = ideal_raw * GAMMA_SYS
        
        # 2. Вычисление штрафа за экстремальное искривление портов (L_strain)
        triple_strain = ideal_taxed - e_exp
        total_strain += triple_strain
        
        print(f"[{name}]")
        print(f"  Идеальный профит (3x дедупликация): {ideal_taxed:.1f} кДж/моль")
        print(f"  Фактический профит (Эксперимент): {e_exp} кДж/моль")
        print(f"  [!!!] ЭКСТРЕМАЛЬНЫЙ ШТРАФ ЗА ИЗЛОМ (L_strain): {triple_strain:.1f} кДж/моль")
        print("-" * 50)
        
    avg_strain = total_strain / len(ALKYNES)
    print(f"\n[КРИТИЧЕСКИЙ ВЫВОД] Средний штраф Матрицы за каждую тройную связь: {avg_strain:.1f} кДж/моль")

if __name__ == "__main__":
    calculate_triple_strain()
