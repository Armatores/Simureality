import pandas as pd

# --- НАСТРОЙКИ (проверь названия файлов) ---
# Имя твоего старого файла с хроносом (где лежат периоды полураспада)
OLD_FILE = "simureality_chronos_v8_benchmark.csv" # Замени на свое, если оно другое
# Имя твоего нового идеального дампа масс
NEW_FILE = "Masses_5_export.csv"
# Как назовем новый файл для Питера и GitHub
OUTPUT_FILE = "chronos_v10_master_debt.csv"

print("Запуск системного слияния (Merge)...")

try:
    # 1. Читаем старый файл (забираем из него ТОЛЬКО физику NUBASE)
    df_old = pd.read_csv(OLD_FILE)
    cols_to_keep = ['Isotope', 'Z', 'A', 'Status', 'Log10(T_1/2)']
    
    # Очищаем его от старых расчетов (старого долга и фаз), чтобы не было конфликтов
    existing_cols = [c for c in cols_to_keep if c in df_old.columns]
    df_old = df_old[existing_cols]
    
    # 2. Читаем новый дамп масс V11
    df_new = pd.read_csv(NEW_FILE)
    
    # 3. Объединяем базы строго по Z (протоны) и A (массовое число)
    df_merged = pd.merge(df_old, df_new[['Z', 'A', 'Grid Debt/Error (MeV)']], on=['Z', 'A'], how='inner')
    
    # 4. Переименовываем колонку. 
    # ВАЖНО: берем модуль (abs), так как Хронос извлекает из долга корень!
    df_merged['ΔK Debt (MeV)'] = df_merged['Grid Debt/Error (MeV)'].abs()
    df_merged = df_merged.drop(columns=['Grid Debt/Error (MeV)'])
    
    # 5. Сохраняем финальный файл
    df_merged.to_csv(OUTPUT_FILE, index=False)
    print(f"🔥 УСПЕШНО! Файл {OUTPUT_FILE} сгенерирован.")
    print(f"Сшито изотопов: {len(df_merged)}")
    print("Теперь просто укажи этот файл в load_chronos_data() в твоем app.py на Streamlit!")
    
except FileNotFoundError as e:
    print(f"❌ Ошибка: Не найден файл. Убедись, что файлы лежат в этой же папке. Детали: {e}")
