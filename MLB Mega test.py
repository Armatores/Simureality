import pandas as pd
import numpy as np
import gzip

# =====================================================================
# SIMUREALITY: MASS BDE COMPILER V6.0 (Batch Operation: UNMERGE)
# Testing Grid Physics across 850+ Database Entries
# =====================================================================

# --- 1. АППАРАТНЫЕ КОНСТАНТЫ МАТРИЦЫ (Из V5.0) ---
GAMMA_SYS = 1.0418
RAW_CONSTANTS = {
    "C-C": 327.51,
    "C-H": 398.11,
    "C-O": 330.91,
    "O-H": 437.81,
    "C-N": 327.18,
    "N-H": 387.58,
    "C=C": 655.02, # 2 * RAW_CC (До применения штрафа)
}

# Штрафы за излом маршрутизации (Routing Strain)
STRAIN_PI = 78.1
STRAIN_TRIPLE = 199.5

def calculate_grid_bde(bond_type, is_conjugated=False, is_strained_ring=False):
    """
    Алгоритм вычисления энергии разрыва связи (UNMERGE).
    BDE = (Базовый профит дедупликации * Системный Налог) - Снятие напряжения решетки
    """
    if bond_type not in RAW_CONSTANTS:
        return None # Пропускаем неизвестные Матрице связи в этой версии
    
    # 1. Снятие базового профита Матрицы
    base_bde = RAW_CONSTANTS[bond_type] * GAMMA_SYS
    
    # 2. Учет топологического напряжения
    # Если мы рвем двойную связь (C=C), мы возвращаем Матрице прямой путь, снимая PI_STRAIN
    if bond_type == "C=C":
        base_bde -= STRAIN_PI
        
    # Если связь находилась в ароматическом кольце (Token Ring),
    # ее разрыв разрушает динамическую балансировку! 
    # Матрица накидывает огромный штраф на разрыв идеального цикла.
    if is_conjugated:
        base_bde += (STRAIN_PI / 2) # Усредненный штраф за потерю резонанса
        
    # Снятие напряжения в кривых циклах (Graph Relaxation)
    if is_strained_ring:
        base_bde -= 30.0 # Приблизительный сброс напряжения при раскрытии малого кольцевого бага
        
    return base_bde

def run_mass_test(file_path):
    print("=" * 70)
    print(f" GRID PHYSICS V6.0: INITIALIZING MASS BDE COMPILER")
    print(f" Target Dataset: {file_path}")
    print("=" * 70)
    
    try:
        # Читаем сжатый CSV
        df = pd.read_csv(file_path, compression='gzip')
        print(f"[OK] Успешно загружено {len(df)} записей.")
    except Exception as e:
        print(f"[FATAL] Ошибка загрузки базы. Проверьте путь к {file_path}")
        print(f"Сведения: {e}")
        return

    # Нормализация столбцов (подгоните под ваш конкретный CSV, если названия отличаются)
    # Предполагаем наличие столбцов: 'bond_type' (напр. 'C-H'), 'bde_exp' (в ккал/моль или кДж/моль)
    col_bond = 'bond_type' if 'bond_type' in df.columns else df.columns[1]
    col_bde = 'bde' if 'bde' in df.columns else df.columns[-1]

    print("[SYSTEM] Запуск массовой операции UNMERGE...")
    
    predictions = []
    actuals = []
    
    for index, row in df.iterrows():
        b_type = str(row[col_bond]).upper()
        # Конвертация ккал/моль в кДж/моль (если база NREL, она обычно в ккал/моль)
        # Если база уже в кДж/моль, уберите "* 4.184"
        actual_bde = float(row[col_bde]) * 4.184 if float(row[col_bde]) < 200 else float(row[col_bde])
        
        # Эвристика для колец и конъюгации (если в базе есть SMILES, можно парсить глубже)
        smiles = str(row.get('smiles', ''))
        is_conj = 'c' in smiles.lower() or '=' in smiles # Примитивный маркер резонанса
        is_ring = '1' in smiles or '2' in smiles         # Примитивный маркер цикла
        
        grid_bde = calculate_grid_bde(b_type, is_conjugated=is_conj, is_strained_ring=is_ring)
        
        if grid_bde is not None:
            predictions.append(grid_bde)
            actuals.append(actual_bde)

    # --- СТАТИСТИКА И МЕТРИКИ ---
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    errors = np.abs(predictions - actuals)
    mae = np.mean(errors)
    mape = np.mean(errors / actuals) * 100
    
    # Расчет R^2 Score
    ss_res = np.sum((actuals - predictions) ** 2)
    ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
    r2_score = 1 - (ss_res / ss_tot)
    
    print("-" * 70)
    print(" РЕЗУЛЬТАТЫ ГЛОБАЛЬНОЙ ВАЛИДАЦИИ GRID PHYSICS:")
    print("-" * 70)
    print(f" Обработано валидных связей: {len(predictions)}")
    print(f" Средняя абсолютная ошибка (MAE): {mae:.2f} кДж/моль")
    print(f" Средняя относительная ошибка (MAPE): {mape:.2f}%")
    print(f" Коэффициент детерминации (R^2): {r2_score:.4f}")
    
    if r2_score > 0.90:
        print("\n[ВЕРДИКТ]: УСПЕХ. Константы Матрицы детерминируют свыше 90% дисперсии BDE. Квантовая химия признана избыточной.")
    else:
        print("\n[ВЕРДИКТ]: ТРЕБУЕТСЯ КАЛИБРОВКА. Топологический парсер не распознал сложные резонансы. Подключите RDKit для точного извлечения графов.")
        
if __name__ == "__main__":
    # Замените на реальное имя файла, если оно в другой папке
    run_mass_test('bde-db2.csv.gz')
