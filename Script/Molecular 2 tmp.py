# =====================================================================
# SIMUREALITY: KERNEL V2.2 - PI-STRAIN DECOMPILER (CLI)
# Extracting the Matrix Tax for Double Bonds (Edge Deduplication)
# =====================================================================

GAMMA_SYS = 1.0418
RAW_CC = 327.51  # Базовая стоимость одного линка C-C
RAW_CH = 398.11  # Базовая стоимость одного линка C-H

# Экспериментальные энергии атомизации алкенов (кДж/моль)
ALKENES = {
    "Ethylene (C2H4 - 1 двойная связь)": {"C=C": 1, "C-C": 0, "C-H": 4, "E_exp": 2253},
    "Propylene (C3H6 - 1 двойная, 1 одинарная)": {"C=C": 1, "C-C": 1, "C-H": 6, "E_exp": 3438},
    "1-Butene (C4H8 - 1 двойная, 2 одинарных)": {"C=C": 1, "C-C": 2, "C-H": 8, "E_exp": 4611}
}

def calculate_pi_strain():
    print("--- АНАЛИЗАТОР ШТРАФА ДВОЙНОЙ СВЯЗИ (Pi-Strain) ---")
    print("Логика: C=C расценивается алгоритмом как попытка замкнуть 2 линка (2 * RAW_CC)\n")
    
    total_strain = 0
    
    for name, data in ALKENES.items():
        n_double = data["C=C"]
        n_single = data["C-C"]
        n_ch = data["C-H"]
        e_exp = data["E_exp"]
        
        # 1. Идеальный профит Матрицы (без штрафа за изгиб пи-связи)
        # Двойная связь = 2 замкнутых линка
        ideal_raw = (n_double * 2 * RAW_CC) + (n_single * RAW_CC) + (n_ch * RAW_CH)
        ideal_taxed = ideal_raw * GAMMA_SYS
        
        # 2. Вычисление штрафа за искривление портов (L_strain)
        pi_strain = ideal_taxed - e_exp
        total_strain += pi_strain
        
        print(f"[{name}]")
        print(f"  Идеальный профит (2x дедупликация): {ideal_taxed:.1f} кДж/моль")
        print(f"  Фактический профит (Эксперимент): {e_exp} кДж/моль")
        print(f"  [!] ШТРАФ МАТРИЦЫ ЗА ПИ-ИЗГИБ (L_strain): {pi_strain:.1f} кДж/моль")
        print("-" * 50)
        
    avg_strain = total_strain / len(ALKENES)
    print(f"\n[КРИТИЧЕСКИЙ ВЫВОД] Средний штраф Матрицы за каждую двойную связь: {avg_strain:.1f} кДж/моль")
    print("Это доказывает Градиент Оптимизации: второй линк между теми же узлами закрывается с огромным топологическим сопротивлением.")

if __name__ == "__main__":
    calculate_pi_strain()
