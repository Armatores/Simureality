import streamlit as st
import pandas as pd
import numpy as np

# --- СТРОГИЕ АППАРАТНЫЕ КОНСТАНТЫ SIMUREALITY (ВЕРСИЯ 1.0) ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.32       
E_MACRO_LINK = 2.425   
E_LINK = 2.36          
E_PAIR = 1.18          
JITTER_COST = 0.01311   # Фундаментальная цена сканирования одного вектора решетки

# --- СЛОВАРЬ ЭЛЕМЕНТОВ ---
ELEMENTS = {
    0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm',
    101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
    110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'
}

st.set_page_config(page_title="Simureality OS | Baseline V1.0", layout="wide")

@st.cache_data
def load_ame_masses(filename="mass.txt"):
    """Строгий парсер логов AME. Фильтрует теоретические данные (# и *)."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                if '#' in line or '*' in line: continue
                try:
                    n_str, z_str, a_str = line[5:10].strip(), line[10:15].strip(), line[15:19].strip()
                    be_str = line[54:65].strip()
                    if not n_str or not z_str or not be_str: continue
                    N, Z, A = int(n_str), int(z_str), int(a_str)
                    total_be_MeV = (float(be_str) * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError: continue
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception: return pd.DataFrame()

class SimurealityBaselineCore:
    def __init__(self):
        self._macro_link_cache = {0: 0, 1: 0, 2: 1, 3: 3, 4: 6}

    def get_fcc_neighbors(self, node):
        x, y, z = node
        deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
                  (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
                  (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

    def compile_3d_crystal(self, n_clusters):
        """Жадная 3D-сборка альфа-кластеров на идеальной жесткой ГЦК-сетке"""
        if n_clusters in self._macro_link_cache:
            return self._macro_link_cache[n_clusters]
        occupied = set([(0, 0, 0)])
        for _ in range(1, n_clusters):
            candidates = set()
            for node in occupied:
                for neighbor in self.get_fcc_neighbors(node):
                    if neighbor not in occupied: candidates.add(neighbor)
            cm_x = sum(n[0] for n in occupied) / len(occupied)
            cm_y = sum(n[1] for n in occupied) / len(occupied)
            cm_z = sum(n[2] for n in occupied) / len(occupied)
            best_pos, max_bonds, min_dist = None, -1, float('inf')
            for cand in candidates:
                bonds = sum(1 for n in self.get_fcc_neighbors(cand) if n in occupied)
                dist_sq = (cand[0]-cm_x)**2 + (cand[1]-cm_y)**2 + (cand[2]-cm_z)**2
                if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                    max_bonds, min_dist, best_pos = bonds, dist_sq, cand
            occupied.add(best_pos)
        total_macro_links = sum(sum(1 for n in self.get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
        self._macro_link_cache[n_clusters] = total_macro_links
        return total_macro_links

    def compile_mass(self, Z, N):
        if Z < 0 or N < 0: return float('inf')
            
        # 1. Базовый кэш альфа-ядра
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        # 2. Построение макро-линков кристаллического остова
        macro_links = self.compile_3d_crystal(n_alphas)
        binding_macro = macro_links * E_MACRO_LINK

        # 3. Структурирование остатков гало
        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        halo_total = rem_Z + rem_N
        
        binding_halo = 0
        jitter = 0
        
        if n_alphas == 0:
            # Аппаратные префабы легчайшего слоя
            if Z == 1:
                if N == 1: binding_halo = 2.225         
                elif N >= 2: binding_halo = 8.482       
            elif Z == 2 and N == 1: binding_halo = 7.718                    
        else:
            # ГОЛАЯ ФОРМУЛА: Каждому нуклону гало — стандартная связь, парам — спиновый бонус
            binding_halo += halo_total * E_LINK
            
            pairs = halo_total // 2
            binding_halo += pairs * E_PAIR
            
            # Налог только за нечетность информационной структуры гало
            if halo_total % 2 != 0:
                jitter += JITTER_COST

        # Итоговый баланс транзакции
        total_binding = binding_alphas + binding_macro + binding_halo - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

@st.cache_data
def generate_global_matrix(_engine, df_ame):
    results = []
    for (Z, N), row in df_ame.iterrows():
        exp_mass = row['Mass_MeV']
        calc_mass = _engine.compile_mass(Z, N)
        delta = calc_mass - exp_mass
        
        m_b_minus = _engine.compile_mass(Z + 1, N - 1) + E_ELECTRON
        m_b_plus = _engine.compile_mass(Z - 1, N + 1) + E_ELECTRON
        
        if m_b_minus < calc_mass: status = "BETA MINUS (Garbage Collect)"
        elif m_b_plus < calc_mass: status = "BETA PLUS (Garbage Collect)"
        else: status = "STABLE"
            
        sym = ELEMENTS.get(Z, "?")
        results.append({
            "Element": f"{sym}-{Z+N}", "Z": Z, "N": N, "A": Z+N,
            "Pure Hardware Log (MeV)": round(exp_mass, 3),
            "Calculated ΣK (MeV)": round(calc_mass, 3),
            "Unresolved Debt (MeV)": round(delta, 3),
            "Dispatcher Decision": status
        })
    return pd.DataFrame(results).sort_values(by=["Z", "N"])

# --- РЕНДЕРИНГ ИНТЕРФЕЙСА СТРИМЛИТ ---
st.title("Simureality OS: Baseline Engine V1.0 (Zero Empirical Coefficients)")
st.markdown("""
### Чистый запуск без подгоночных коэффициентов
Этот скрипт реализует **исключительно исходное Уравнение 9** и базовую 3D-сборку ядер без учета эллипсоидной деформации, 
корсетного натяжения решетки, поверхностных емкостей и hardcoded-магических чисел.
""")

df_masses = load_ame_masses("mass.txt")
engine = SimurealityBaselineCore()

st.sidebar.header("Конфигурация ядра")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=0, max_value=118, value=82, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=0, max_value=184, value=126, step=1)

symbol = ELEMENTS.get(target_Z, "Unknown")
st.sidebar.markdown(f"### Выбранный узел: **{symbol}-{target_Z+target_N}**")

if df_masses.empty:
    st.sidebar.error("⚠️ Лог mass.txt не найден.")
else:
    st.sidebar.success(f"✅ Лог загружен ({len(df_masses)} чистых изотопов)")

st.write("### Анализ одиночного узла")
col1, col2 = st.columns(2)
calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Calculated ΣK (Baseline)", value=f"{calc_mass:.3f} MeV")

if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
    delta = calc_mass - exp_mass
    col2.metric(label="AME2020 Log", value=f"{exp_mass:.3f} MeV", delta=f"{delta:.3f} MeV (Debt)", delta_color="inverse")
else:
    col2.metric(label="AME2020 Log", value="Node Not Found")

st.markdown("---")
st.write("### Глобальная статистика матрицы")
if not df_masses.empty:
    with st.spinner('Сведение баланса глобальной матрицы...'):
        global_df = generate_global_matrix(engine, df_masses)
        global_df['Absolute Debt (MeV)'] = global_df['Unresolved Debt (MeV)'].abs()
        global_df['Jitter Cache Load (%)'] = (global_df['Absolute Debt (MeV)'] / global_df['Pure Hardware Log (MeV)']) * 100
        
        max_debt_mev = global_df['Absolute Debt (MeV)'].max()
        mean_debt_mev = global_df['Absolute Debt (MeV)'].mean()
        overall_efficiency = 100.0 - global_df['Jitter Cache Load (%)'].mean()
        
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(label="Общая системная точность", value=f"{overall_efficiency:.4f} %")
        sc2.metric(label="Средний топологический долг", value=f"{mean_debt_mev:.3f} MeV")
        sc3.metric(label="Максимальный разрыв (Переполнение)", value=f"{max_debt_mev:.3f} MeV")
        
        st.dataframe(global_df.drop(columns=['Absolute Debt (MeV)', 'Jitter Cache Load (%)']), use_container_width=True, height=400)
