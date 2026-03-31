import numpy as np

# =====================================================================
# SIMUREALITY: KERNEL V3.0 - HETEROATOM DECOMPILER (CLI)
# Extracting the Hardware Buffer Tax (Lone Pair Pressure)
# =====================================================================

GAMMA_SYS = 1.0418
RAW_CC = 327.51  # Идеальный 3D-линк решетки
RAW_CH = 398.11  # Идеальный терминальный линк

# Экспериментальные теплоты атомизации (кДж/моль)
# OXYGEN_DATA: Вычисляем C-O и O-H
OXYGEN_DATA = {
    "Methanol (CH3OH)": {"C-C": 0, "C-H": 3, "C-O": 1, "O-H": 1, "E_exp": 2037},
    "Dimethyl ether (CH3OCH3)": {"C-C": 0, "C-H": 6, "C-O": 2, "O-H": 0, "E_exp": 3178},
    "Ethanol (C2H5OH)": {"C-C": 1, "C-H": 5, "C-O": 1, "O-H": 1, "E_exp": 3224}
}

# NITROGEN_DATA: Вычисляем C-N и N-H
NITROGEN_DATA = {
    "Methylamine (CH3NH2)": {"C-C": 0, "C-H": 3, "C-N": 1, "N-H": 2, "E_exp": 2384},
    "Dimethylamine ((CH3)2NH)": {"C-C": 0, "C-H": 6, "C-N": 2, "N-H": 1, "E_exp": 3574},
    "Ethylamine (C2H5NH2)": {"C-C": 1, "C-H": 5, "C-N": 1, "N-H": 2, "E_exp": 3572}
}

def decompile_buffers(dataset, target_links, buffer_count, node_name):
    print(f"\n--- ДЕКОМПИЛЯЦИЯ УЗЛА [{node_name}] (Аппаратных заглушек: {buffer_count}) ---")
    
    A = []
    B = []
    
    for name, data in dataset.items():
        A.append([data[target_links[0]], data[target_links[1]]])
        # Считаем известную базу (C-C и C-H), снимаем налог с E_exp
        known_raw = (data["C-C"] * RAW_CC) + (data["C-H"] * RAW_CH)
        remaining_raw = (data["E_exp"] / GAMMA_SYS) - known_raw
        B.append(remaining_raw)
        
    A = np.array(A)
    B = np.array(B)
    
    # Извлекаем стоимости линков гетероатома
    costs, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    raw_c_x = costs[0]
    raw_x_h = costs[1]
    
    print(f"Чистая стоимость линка {target_links[0]} (Raw): {raw_c_x:.2f} ед.")
    print(f"Чистая стоимость линка {target_links[1]} (Raw): {raw_x_h:.2f} ед.")
    
    # Вычисляем Buffer Strain Tax (деградация линка относительно идеального C-C / C-H)
    strain_cx = RAW_CC - raw_c_x
    strain_xh = RAW_CH - raw_x_h
    
    # Приводим к физическим кДж/моль (умножаем на системный налог)
    tax_cx = strain_cx * GAMMA_SYS
    tax_xh = strain_xh * GAMMA_SYS
    
    print(f"[!] Скрытый налог на заглушки в {target_links[0]}: {tax_cx:.1f} кДж/моль")
    print(f"[!] Скрытый налог на заглушки в {target_links[1]}: {tax_xh:.1f} кДж/моль")
    
    avg_buffer_tax = (tax_cx + tax_xh) / buffer_count if buffer_count > 0 else 0
    print(f"-> ИТОГОВЫЙ STRAIN-ШТРАФ НА ОДНУ ЗАГЛУШКУ: ~{avg_buffer_tax:.1f} кДж/моль")

if __name__ == "__main__":
    print("ИНИЦИАЛИЗАЦИЯ V3.0 HETEROATOM DECOMPILER...\n")
    print(f"Эталон решетки: C-C = {RAW_CC} | C-H = {RAW_CH}")
    
    # Кислород (2 открытых порта, 2 аппаратные заглушки)
    decompile_buffers(OXYGEN_DATA, ["C-O", "O-H"], buffer_count=2, node_name="OXYGEN")
    
    # Азот (3 открытых порта, 1 аппаратная заглушка)
    decompile_buffers(NITROGEN_DATA, ["C-N", "N-H"], buffer_count=1, node_name="NITROGEN")
