import streamlit as st
import pandas as pd
import numpy as np
import os

# =====================================================================
# SIMUREALITY V10: ULTIMATE MASS ENGINE (GEOMETRY + ENTANGLEMENT)
# =====================================================================

# --- Фундаментальные Константы (Эффективная Геометрия) ---
MASS_P = 938.272
MASS_N = 939.565
E_ALPHA = 28.295       
E_MACRO_LINK = 2.425   
E_LINK = 2.36          
E_PAIR = 1.18          
JITTER_COST = 0.0131   

MAGIC_NODES = [2, 8, 14, 28, 50, 82, 126, 184]

def get_base_binding_energy(Z, N):
    """Фаза 1: Расчет чистой топологии графа (Старая архитектура)"""
    if Z <= 0 or N <= 0: return 0
    
    n_alpha = min(Z // 2, N // 2)
    l_ideal = max(0, 3 * n_alpha - 6)
    
    dist_Z = min([abs(Z - m) for m in MAGIC_NODES])
    dist_N = min([abs(N - m) for m in MAGIC_NODES])
    l_lost = (dist_Z + dist_N) * 0.4
    
    profit = (n_alpha * E_ALPHA) + (max(0, l_ideal - l_lost) * E_MACRO_LINK)
    
    halo_n = N - Z
    if halo_n > 0:
        max_strong = int(Z * 0.4)
        strong = min(halo_n, max_strong)
        weak = halo_n - strong
        profit += strong * E_LINK
        profit += weak * (E_PAIR / 2.0)
        
    base_ports = 10.0 * ((Z + N)**(2/3))
    jitter = (base_ports + (15.0 * ((dist_Z + dist_N)**1.6))) * JITTER_COST
    dangling = (E_LINK / 2.0) * ((Z % 2) + (N % 2))
    
    return profit - jitter - dangling

def get_entanglement_cache(Z, N):
    """Фаза 2: Динамический Кэш Запутанности (Иерархический LOD)"""
    A = Z + N
    if A <= 16: 
        return 0 # Для легких ядер достаточно базовой геометрии
        
    dist_Z = min([abs(Z - m) for m in MAGIC_NODES])
    dist_N = min([abs(N - m) for m in MAGIC_NODES])
    
    # 1. Базовый L2 кэшбек (Премия за объем и Барицентр)
    base_l2 = A * 0.466  
    
    # 2. Штраф за Асимметрию (Удаление "строительных лесов" из скидки)
    asymmetry_tax = (dist_Z + dist_N) * 1.22
    
    # 3. L3 Субсидия (Компенсация маршрутизации висячих портов)
    orphan_count = (Z % 2) + (N % 2)
    l3_subsidy = orphan_count * 8.4
    
    return max(0, base_l2 - asymmetry_tax + l3_subsidy)

@st.cache_data
def load_ame2020():
    db = {}
    file_path = "mass.txt"
    if not os.path.exists(file_path): return db
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if len(line) < 100 or "A T O M I C" in line or "mass.mas20" in line: continue
            try:
                n_str, z_str, be_str = line[4:9].strip(), line[9:14].strip(), line[54:67].strip().replace('#', '')
                if not n_str.isdigit() or not z_str.isdigit() or '*' in be_str or not be_str: continue
                N, Z = int(n_str), int(z_str)
                # Извлекаем общую энергию связи
                db[(Z, N)] = (float(be_str) * (N + Z)) / 1000.0
            except ValueError: continue
    return db

# --- STREAMLIT UI ---
st.set_page_config(page_title="Simureality V10 Engine", layout="wide")
st.title("💠 Simureality V10: Entanglement Architecture")
st.markdown("Финальный рендер: Базовая ГЦК-топология + Динамический Кэш Матрицы (L2/L3).")

ame_db = load_ame2020()

if st.button("🚀 ЗАПУСТИТЬ АБСОЛЮТНЫЙ БЕНЧМАРК", type="primary"):
    if not ame_db:
        st.error("Файл mass.txt не найден! Положи базу AME2020 в папку со скриптом.")
    else:
        with st.spinner("Компиляция ядерной архитектуры и расчет кэша..."):
            results = []
            for (Z, N), exp_be in ame_db.items():
                if Z < 2: continue # Пропускаем Водород
                
                # Считаем сырую геометрию
                base_be = get_base_binding_energy(Z, N)
                # Считаем бонус запутанности
                cache_bonus = get_entanglement_cache(Z, N)
                
                # Итоговая Энергия Связи (Геометрия + Скидка Матрицы)
                ultimate_be = base_be + cache_bonus
                
                error_mev = ultimate_be - exp_be
                
                # Чтобы не делить на ноль
                error_pct = (abs(error_mev) / exp_be) * 100 if exp_be > 0 else 0
                accuracy = 100.0 - error_pct
                
                results.append({
                    "Element": f"Z={Z}, N={N}",
                    "Z": Z, "N": N, "A": Z + N,
                    "AME2020 BE (MeV)": exp_be,
                    "Raw Geometry BE": base_be,
                    "Entanglement Cache": cache_bonus,
                    "Simureality V10 BE": ultimate_be,
                    "Delta Error (MeV)": error_mev,
                    "Accuracy (%)": accuracy
                })
                
            df = pd.DataFrame(results)
            
        st.success(f"Рендер завершен. Обработано {len(df)} изотопов.")
        
        # Вывод статистики
        c1, c2, c3 = st.columns(3)
        c1.metric("Средняя Точность", f"{df['Accuracy (%)'].mean():.5f}%")
        c2.metric("Медианная Ошибка", f"{df['Delta Error (MeV)'].median():.3f} MeV")
        
        # Находим и выводим наши "эталонные" элементы для быстрой сверки
        st.subheader("Критическая Выборка (Проверка Инсайтов)")
        bench_elements = df[(df['Z'].isin([2, 6, 26, 82, 92])) & (df['N'].isin([2, 6, 30, 126, 146]))]
        st.dataframe(bench_elements.style.format(precision=3), use_container_width=True)
        
        st.subheader("Полный Дамп Изотопов")
        st.dataframe(df.sort_values("A").style.background_gradient(subset=['Accuracy (%)'], cmap='Greens').format(precision=3), use_container_width=True)
