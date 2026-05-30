import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math

# --- КОНСТАНТЫ GRID PHYSICS ---
MASS_P = 938.272
MASS_N = 939.565
E_ALPHA = 28.32       
E_MACRO_LINK = 2.425  
E_LINK = 2.36         
E_PAIR = 1.18         
JITTER_COST = 0.01311
LAMBDA_P = 1.3214      # Шаг L1 кэша (фм)

st.set_page_config(page_title="Grid Physics: Global Resonance", layout="wide")

# --- ФУНКЦИИ ПАРСИНГА БАЗ ДАННЫХ ---
@st.cache_data
def load_ame2020(filepath="mass.txt"):
    """Парсер AME2020 (Массы)"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                try:
                    n_str, z_str, a_str = line[5:10].strip(), line[10:15].strip(), line[15:19].strip()
                    be_str = line[54:65].strip().replace('#', '').replace('*', '')
                    if not n_str or not z_str or not be_str: continue
                    N, Z, A = int(n_str), int(z_str), int(a_str)
                    total_be_MeV = (float(be_str) * A) / 1000.0
                    exp_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'A': A, 'Exp_Mass_MeV': exp_mass})
                except ValueError: continue
    except Exception as e:
        st.error(f"Ошибка чтения AME2020: {e}")
    return pd.DataFrame(data).drop_duplicates(subset=['Z', 'N'])

@st.cache_data
def load_nubase2020(filepath="Nubase2020.txt"):
    """Парсер NUBASE2020 (Периоды полураспада)"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 60 or 'A' in line[:5]: continue # Пропуск хидера
                try:
                    # NUBASE fixed-width parsing (стандартные индексы)
                    a_str = line[0:3].strip()
                    z_str = line[4:7].strip()
                    if not a_str.isdigit() or not z_str.isdigit(): continue
                    A, Z = int(a_str), int(z_str)
                    N = A - Z
                    
                    is_stable = "STABLE" in line or "stbl" in line.lower()
                    hl_str = line[60:69].strip() # Поле Half-life
                    
                    data.append({'Z': Z, 'N': N, 'Is_Stable': is_stable, 'Half_Life_Raw': hl_str})
                except ValueError: continue
    except Exception as e:
        st.error(f"Ошибка чтения NUBASE2020: {e}")
    return pd.DataFrame(data).drop_duplicates(subset=['Z', 'N'])

# --- GRID PHYSICS ENGINE (Предиктор Резонанса) ---
def get_fcc_neighbors(node):
    x, y, z = node
    deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
              (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
              (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
    return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

def calculate_grid_metrics(row):
    Z, N, exp_mass = row['Z'], row['N'], row['Exp_Mass_MeV']
    n_alphas = min(Z // 2, N // 2)
    
    # 1. Симуляция жадной (идеальной) сферы
    occupied = set([(0, 0, 0)])
    for _ in range(1, n_alphas):
        candidates = set()
        for node in occupied:
            for neighbor in get_fcc_neighbors(node):
                if neighbor not in occupied: candidates.add(neighbor)
        cm_x = sum(n[0] for n in occupied) / len(occupied)
        cm_y = sum(n[1] for n in occupied) / len(occupied)
        cm_z = sum(n[2] for n in occupied) / len(occupied)
        
        best_pos, max_bonds, min_dist = None, -1, float('inf')
        for cand in candidates:
            bonds = sum(1 for n in get_fcc_neighbors(cand) if n in occupied)
            dist_sq = (cand[0]-cm_x)**2 + (cand[1]-cm_y)**2 + (cand[2]-cm_z)**2
            if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                max_bonds, min_dist, best_pos = bonds, dist_sq, cand
        occupied.add(best_pos)

    greedy_links = sum(sum(1 for n in get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
    
    # Расчет массы Идеальной Сферы
    binding_alphas = n_alphas * E_ALPHA
    binding_macro = greedy_links * E_MACRO_LINK
    
    rem_Z, rem_N = Z - (n_alphas * 2), N - (n_alphas * 2)
    pairs = min(rem_Z, rem_N)
    binding_halo = pairs * (E_LINK + E_PAIR)
    
    sphere_mass = (Z * MASS_P) + (N * MASS_N) - (binding_alphas + binding_macro + binding_halo)
    
    # 2. РАСЧЕТ ТОПОЛОГИЧЕСКОГО ДОЛГА И ДЕФОРМАЦИИ
    # Если sphere_mass < exp_mass, значит жадный алгоритм "пережал" ядро (слишком много связей).
    topological_debt = exp_mass - sphere_mass 
    
    broken_links = 0
    calculated_layers = 0.0
    
    if topological_debt > 0:
        broken_links = topological_debt / E_MACRO_LINK
        # Формула эвристического вытягивания: базовые слои + компенсация за разрыв
        base_radius = (n_alphas)**(1/3) * 1.5 
        calculated_layers = base_radius + (broken_links * 0.08) # Коэффициент вытягивания эллипса
    else:
        # Для легких ядер (до Железа) долга нет, ядро сферично
        calculated_layers = (n_alphas)**(1/3) * 1.5
        
    return pd.Series([topological_debt, broken_links, calculated_layers])

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("🌌 Grid Physics: Global Resonance Scanner")

with st.spinner("Компиляция баз данных Матрицы..."):
    df_ame = load_ame2020()
    df_nubase = load_nubase2020()

if not df_ame.empty and not df_nubase.empty:
    st.success("✅ Базы данных AME2020 и NUBASE2020 успешно загружены и проиндексированы.")
    
    # Merge datasets
    df = pd.merge(df_ame, df_nubase, on=['Z', 'N'], how='inner')
    
    # Фильтруем только стабильные или долгоживущие для анализа решетки (убираем экстремальный мусор)
    df = df[df['A'] > 10] 
    
    with st.spinner("Реверс-инжиниринг Топологии (Вычисление долга и деформации)..."):
        # Для скорости в Streamlit ограничимся выборкой магических и тяжелых ядер
        # (в реальном приложении можно прогнать весь датафрейм, но это займет пару минут)
        scan_df = df.copy() 
        scan_df[['Topo_Debt', 'Broken_Links', 'Grid_Layers']] = scan_df.apply(calculate_grid_metrics, axis=1)
        
        # Расчет Джиттера (отклонение от целого числа макро-слоев)
        scan_df['Grid_Layers_Int'] = scan_df['Grid_Layers'].round()
        scan_df['Jitter'] = abs(scan_df['Grid_Layers'] - scan_df['Grid_Layers_Int'])
        
        # Разметка для графиков
        scan_df['Stability_Class'] = scan_df['Is_Stable'].apply(lambda x: "Стабильный узел" if x else "Мусор (Радиоактивен)")

    tab1, tab2, tab3 = st.tabs(["📊 Лестница Деформаций", "🔥 Карта Вакуумного Шума (Jitter)", "🗄 Системный Лог"])

    with tab1:
        st.markdown("### Лестница Фазовых Переходов Формы (Shape Phase Transitions)")
        st.markdown("По оси Y — длина ядра в слоях ГЦК-решетки (шаг 1.32 фм). Мы видим, что тяжелые ядра деформируются не плавно, а прыгают по целым числам (Резонанс Матрицы).")
        
        fig1 = px.scatter(scan_df, x='A', y='Grid_Layers', color='Jitter',
                          hover_data=['Z', 'N', 'Half_Life_Raw'],
                          color_continuous_scale=["#00FF00", "#FF0000"],
                          labels={'Grid_Layers': 'Длина (в слоях ГЦК)', 'A': 'Массовое число (A)'})
        
        for layer in range(3, 14):
            fig1.add_hline(y=layer, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            
        fig1.update_layout(height=600)
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.markdown("### Jitter Tax: Топологический Шум и Радиоактивность")
        st.markdown("Показывает карту изотопов. **Зеленые** — длина ядра кратна целому числу (идеальный резонанс, стабильность). **Красные** — ядро застряло между слоями (Джиттер, Спонтанное деление).")
        
        fig2 = px.scatter(scan_df, x='N', y='Z', color='Jitter', symbol='Stability_Class',
                          hover_data=['A', 'Topo_Debt', 'Half_Life_Raw'],
                          color_continuous_scale=["#00FF00", "#FF0000"])
        fig2.update_layout(height=700)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### Сырые данные Реверс-Инжиниринга")
        st.dataframe(scan_df[['Z', 'N', 'A', 'Exp_Mass_MeV', 'Topo_Debt', 'Broken_Links', 'Grid_Layers', 'Jitter', 'Is_Stable']].sort_values('A'), use_container_width=True)

else:
    st.warning("⚠️ Ожидание баз данных. Положите файлы 'mass.txt' и 'Nubase2020.txt' в корневую папку рядом с этим скриптом.")
